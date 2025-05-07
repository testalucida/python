import os
import sys
import traceback
from typing import List, Iterable, Dict

from PySide6.QtCore import Slot, QCoreApplication, Qt, QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QMenu, QMessageBox, QInputDialog, QLineEdit, QApplication

import datehelper
from base.baseqtderivates import BaseAction
from base.filtertablewidget import FilterTableWidgetFrame
from base.messagebox import InfoBox, ErrorBox, WarningBox
from v2.abrechnungen.abrechnungcontroller import NKAbrechnungController, HGAbrechnungController
from v2.einaus.einauscontroller import EinAusController
#from v2.einaus.einauswritedispatcher import EinAusWriteDispatcher
from v2.einaus.einauswritedispatcher import EinAusWriteDispatcher
from v2.extras.extrascontroller import ExtrasController
from v2.geschaeftsreise.geschaeftsreisecontroller import GeschaeftsreiseController
from v2.icc.constants import EinAusArt
from v2.icc.definitions import ROOT_DIR
from v2.icc.icccontroller import IccController
from v2.icc.iccmainwindow import IccMainWindow, InfoPanel
from v2.icc.iccwidgets import IccCheckTableViewFrame
from v2.icc.interfaces import XEinAus, XSummen
from v2.icc.mainlogic import MainLogic
from v2.mietobjekt.mietobjektcontroller import MietobjektController
from v2.mietverhaeltnis.mietverhaeltniscontroller import MietverhaeltnisController
from v2.mtleinaus.mtleinauscontroller import MieteController, HausgeldController, AbschlagController
from v2.sollhausgeld.sollhausgeldcontroller import SollHausgeldController, SollzahlungenController
from v2.sollmiete.sollmietecontroller import SollMieteController

class WorkerSignals( QObject ):
    finished = Signal()
    error = Signal( tuple )
    result = Signal( object )

##############################################################
class Worker( QRunnable ):
    def __init__( self, fn ):
        super( Worker, self ).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.signals = WorkerSignals()

    @Slot()
    def run( self ):
        try:
            result = self.fn()
        except:
            print( "mainController.Worker.run(): Exception aufgetreten"  )
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit( (exctype, value, traceback.format_exc()) )
        else:
            print( "mainController.Worker.run(): vor signals.result.emit" )
            self.signals.result.emit( result )  # Return the result of the processing
        finally:
            print( "mainController.Worker.run(): vor signals.finished.emit" )
            self.signals.finished.emit()  # Done


###########################################################
class MainController( IccController ):
    def __init__( self, environment:str ):
        IccController.__init__( self )
        self._win:IccMainWindow = None
        self._env = environment
        self._logic:MainLogic = MainLogic()
        self._mieteCtrl = MieteController()
        self._hausgeldCtrl = HausgeldController()
        self._abschlagCtrl = AbschlagController()
        self._einausCtrl = EinAusController()
        self._nkaCtrl = NKAbrechnungController()
        self._hgaCtrl = HGAbrechnungController()
        self._sollZahlungenCtrl = SollzahlungenController()
        self._reiseCtrl = GeschaeftsreiseController()
        self._mietObjektCtrl = MietobjektController()
        self._mietObjektCtrl.edit_miete.connect( self.onEditMiete )
        self._mietObjektCtrl.edit_mieter.connect( self.onEditMieter )
        self._mvCtrl = MietverhaeltnisController()
        self._extrasCtrl = ExtrasController()
        self._threadpool = QThreadPool()
        self._rcFtpExportDatabase = False
        self._connectToSignals()

    def _connectToSignals( self ):
        # connect to EinAusWriteDispatcher wg. Versorgung Summenfelder
        EinAusWriteDispatcher.inst().ea_inserted.connect( self.onEinAusInserted )
        EinAusWriteDispatcher.inst().ea_updated.connect( self.onEinAusUpdated )
        EinAusWriteDispatcher.inst().ea_deleted.connect( self.onEinAusDeleted )

        self._einausCtrl.year_changed.connect( self.onYearChanged )
        self._mieteCtrl.show_objekt.connect(self._mietObjektCtrl.onShowMasterMietobjektMieter)
        self._mieteCtrl.show_mietverhaeltnis.connect( self._mvCtrl.onMietverhaeltnisShowOrEdit )
        self._mieteCtrl.kuendige_mietverhaeltnis.connect( self._mvCtrl.onMietverhaeltnisKuendigen )
        self._mieteCtrl.show_NettomieteAndNkv.connect( self.onShowNettomieteAndNkv )
        self._hausgeldCtrl.show_verwaltung.connect( self.onShowVerwaltung )
        self._hausgeldCtrl.show_hgaAndRueZuFue.connect( self.onShowHgaAndRueZuFue )
        # self._sollHausgeldCtrl = SollHausgeldController()
        # self._sollMieteCtrl = SollMieteController()

    @Slot( int )
    def onYearChanged( self, newyear:int ):
        self._provideSummen( newyear )

    @Slot( str, int, int )
    def onShowNettomieteAndNkv( self, mv_id:str, year:int, monthNumber:int ):
        #self._sollMieteCtrl.showSollMieteAndNkv( mv_id, year, monthNumber )
        SollMieteController().showSollMieteAndNkv( mv_id, year, monthNumber )

    @Slot( str, int, int )
    def onShowVerwaltung( self, weg_name:str, year:int, monthNumber:int ):
        print( "onShowVerwaltung ", weg_name )

    @Slot( str, int, int )
    def onShowHgaAndRueZuFue( self, mobj_id:str, year:int, monthNumber:int ):
        #self._sollHausgeldCtrl.showHgvAndRueZuFue( mobj_id, year, monthNumber )
        SollHausgeldController().showHgvAndRueZuFue( mobj_id, year, monthNumber )

    @Slot( str )
    def onEditMieter( self, mv_id:str ):
        self._mvCtrl.showMietverhaeltnis( mv_id )

    @Slot( str )
    def onEditMiete( self, mv_id:str ):
        self._notYetImplemented( "'%s': Funktion Miete Ändern noch nicht realisiert" % mv_id )

    @staticmethod
    def _notYetImplemented( msg: str ):
        box = InfoBox( "Not yet implemented", msg, "", "OK" )
        box.exec_()

    def createGui( self ) -> IccMainWindow:
        self._win = IccMainWindow( self._env )
        #self._win.setShutdownCallback( self.onBeforeShutdown )
        self._win.addMenu( self.getMenu() )

        menu = self._mietObjektCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._sollZahlungenCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._mvCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._mieteCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._hausgeldCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._abschlagCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._einausCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._reiseCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        menu = self._extrasCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        ### die Views für die monatlichen Zahlungen erzeugen und dem MainWindow hinzufügen
        # Mietzahlungen
        tvf:IccCheckTableViewFrame = self._mieteCtrl.createGui()
        self._win.setMieteTableViewFrame( tvf )
        # Hausgeldzahlungen
        tvf: IccCheckTableViewFrame = self._hausgeldCtrl.createGui()
        self._win.setHausgeldTableViewFrame( tvf )
        # Abschlagszahlungen (KEW, Gaswerk etc.)
        tvf: IccCheckTableViewFrame = self._abschlagCtrl.createGui()
        self._win.setAbschlagTableViewFrame( tvf )
        # Übrige regelmäßige (z.B. jährliche) Zahlungen (Versicherungen, Grundsteuer etc.)
        # HGAbrechnungen
        tvf: IccCheckTableViewFrame = self._hgaCtrl.createGui()
        self._win.setHGAbrechnungenTableViewFrame( tvf )
        # NKAbrechnungen
        tvf: IccCheckTableViewFrame = self._nkaCtrl.createGui()
        self._win.setNKAbrechnungenTableViewFrame( tvf )
        ### Die View für "alle" Zahlungen (Rechnungen etc.)
        tvf: FilterTableWidgetFrame = self._einausCtrl.createGui()
        self._win.setAlleZahlungenTableViewFrame( tvf )
        self._provideSummen( self.getYearToStartWith() )
        self._provideLetzteBuchung()
        return self._win

    def getMenu( self ) -> QMenu:
        menu = QMenu( "ImmoCenter" )
        # Menü "Datenbank zum Server exportieren"
        # action = BaseAction( "Datenbank zum Server exportieren", parent=menu )
        # action.triggered.connect( self.onExportDatabase )
        # menu.addAction( action )
        #
        # # Menü "Datenbank vom Server importieren"
        # action = BaseAction( "Datenbank vom Server importieren", parent=menu )
        # action.triggered.connect( self.onImportDatabase )
        # menu.addAction( action )
        #
        # Menü "Datenbank vom Server importieren"
        action = BaseAction( "Datenbank auf externe Festplatte sichern", parent=menu )
        action.triggered.connect( self.onSaveDatabase )
        menu.addAction( action )

        menu.addSeparator()

        # # Menüpunkt "Ende"
        action = BaseAction( "Ende", parent=menu )
        action.triggered.connect( self.onExit )
        action.setShortcut( "Alt+F4")
        menu.addAction( action )
        return menu

    def _provideSummen( self, year:int ):
        summen:XSummen = self._logic.getSummen( year )
        self._win.setSummenValues( summen )

    def _provideLetzteBuchung( self ):
        datum, text = self._logic.getLetzteBuchung()
        self._win.setLetzteBuchung( datum, text )

    def onEinAusInserted( self, x:XEinAus ):
        """
        Ist mit dem ea_inserted-Signal des EinAusWriteDispatchers connected.
        Aktualisiert die Summenfelder in der ToolBar der Anwendung
        :param ea_id_list: wird hier nicht benötigt
        :param ea_art_display: wird benötigt, um die Summenfelder richtig zu versorgen
        :param betrag: betrag, der dem betreffenden Summenfeld addiert werden muss
        :return:
        """
        # Summenfelder aktualisieren
        betrag = round(x.betrag)
        self._updateSummen( x.ea_art, betrag )

    def _updateSummen( self, ea_art_display:str, betrag:int ):
        summen = self._win.getSummenValues()
        summen.saldo += betrag
        if ea_art_display == EinAusArt.HAUSGELD_VORAUS.display:
            summen.sumHGV += betrag
        elif ea_art_display in (EinAusArt.BRUTTOMIETE.display, EinAusArt.NEBENKOSTEN_ABRECHNG.display) :
            summen.sumEin += betrag
        else:
            summen.sumSonstAus += betrag
        self._win.setSummenValues( summen )

    def onEinAusUpdated( self, x:XEinAus, delta:int or float ):
        """
        Ist mit dem ea_updated-Signal des EinAusWriteDispatchers connected.
        Aktualisiert die Summenfelder in der ToolBar der Anwendung
        :param x: das geänderte XEinAus-Objekt
        :param delta: wird benötigt, Wert der Änderung
        :return:
        """
        if delta != 0:
            self._updateSummen( x.ea_art, delta )

    def onEinAusDeleted( self, ea_id_list:List[int], ea_art_display:str, betrag:int or float ):
        """
        Ist mit dem ea_deleted-Signal des EinAusWriteDispatchers connected.
        Aktualisiert die Summenfelder in der ToolBar der Anwendung.
        :param ea_id_list: wird hier nicht benötigt
        :param ea_art_display: wird benötigt, um die Summenfelder richtig zu versorgen
        :param betrag: betrag, der dem betreffenden Summenfeld addiert werden muss
        :return:
        """
        self._updateSummen( ea_art_display, betrag )

    # def onExportDatabase( self ):
    #     try:
    #         dic = self._win.getLetzteBuchung()
    #         self._logic.saveLetzteBuchung( dic["datum"], dic["text"] )
    #         self._logic.exportDatabaseToServer()
    #         box = InfoBox( "Datenbank-Export", "Export der Datenbank abgeschlossen.", "", "OK" )
    #         box.exec_()
    #     except Exception as ex:
    #         box = ErrorBox( "Datenbank-Export", "Export der Datenbank fehlgeschlagen.", str(ex) )
    #         box.exec_()

    # def onImportDatabase( self ):
    #     dlg = QInputDialog()
    #     dlg.move( self._mainwin.cursor().pos() )
    #     name, ok = dlg.getText( self._mainwin, "Immo-Datenbank importieren",
    #                             "Datenbank wird ins Verzeichnis\n\n'%s'\n\n importiert.\n\n"
    #                             "<<<<Sie wird nicht für die laufende Anwendung verwendet!!>>>>\n\n"
    #                             "Lokalen Namen für die Datenbank angeben: " % self._logic.getFtpLocalPath(),
    #                             QLineEdit.Normal, "immo.db.imported" )
    #
    #     if not (ok and name): return
    #     try:
    #         self._logic.importDatabaseFromServer( name )
    #         box = InfoBox( "Datenbank-Import", "Import der Datenbank abgeschlossen.", "", "OK" )
    #         box.exec_()
    #     except Exception as ex:
    #         box = ErrorBox( "Datenbank-Import", "Import der Datenbank fehlgeschlagen.", str(ex) )
    #         box.exec_()

    def onExit( self ):
        self._win.close()

    def onBeforeShutdown( self ) -> bool:
        """
        "Letzte Buchung" speichern.
        :return:
        """
        try:
            self._saveLetzteBuchung()
            return True
        except Exception as ex:
            box = WarningBox( "Speichern der letzten Buchung", "Speichern fehlgeschlagen: " + str( ex ),
                              "Anwendung trotzdem schließen?", "Ja", "Nein" )
            if box.exec_() == QMessageBox.Yes:
                return True
            return False

    def _saveLetzteBuchung( self ):
        dic = self._win.getLetzteBuchung()
        self._logic.saveLetzteBuchung( dic["datum"], dic["text"] )

    def exportDatabaseOnClose( self ) -> bool:
        """
        Datenbank zum Server hochladen.
        :return:
        """
        self._win.setCursor( Qt.WaitCursor )
        try:
            self._saveLetzteBuchung()
        except Exception as ex:
            box = WarningBox( "Speichern der letzten Buchung", "Speichern fehlgeschlagen: " + str(ex),
                              "Anwendung trotzdem schließen?", "Ja", "Nein" )
            if box.exec_() != QMessageBox.Yes:
                self._win.setCursor( Qt.ArrowCursor )
                return False
            return True
        try:
            self._logic.exportDatabaseToServer()
            self._win.setCursor( Qt.ArrowCursor )
        except Exception as ex:
            box = ErrorBox( "Export der Datenbank fehlgeschlagen", str(ex), "\nAnwendung wird beendet." )
            box.exec_()
        return True

    def onExportDatabase___( self ):
        """
        Datenbank zum Server hochladen.
        :return:
        """
        self._win.setCursor( Qt.WaitCursor )
        try:
            self._saveLetzteBuchung()
        except Exception as ex:
            box = WarningBox( "Speichern der letzten Buchung", "Speichern fehlgeschlagen: " + str(ex),
                              "Datenbank trotzdem exportieren?", "Ja", "Nein" )
            if box.exec_() != QMessageBox.Yes:
                self._win.setCursor( Qt.ArrowCursor )
                return
        try:
            self._logic.exportDatabaseToServer()
            box = InfoBox( "Datenbankexport", "Datenbank erfolgreich exportiert." )
            box.exec_()
        except Exception as ex:
            box = ErrorBox( "Export der Datenbank fehlgeschlagen:\nException:\n" + str(ex) )
            box.exec_()
        finally:
            self._win.setCursor( Qt.ArrowCursor )

    def exportDatabaseOnCloseWorker( self ) -> bool:
        """
        Datenbank zum Server hochladen.
        Methode steigt manchmal mit Exception aus:
                        QBasicTimer::stop: Failed. Possibly trying to stop from a different thread
                        Illegal instruction (core dumped)
        Da ich den Fehler nicht finde, kommt o.a. Methode onExportDatabase zum Einsatz.
        :return:
        """
        def onExported():
            print( "Database exported.")
            self._rcFtpExportDatabase = True

        def onExportResult( obj ):
            print( "Export Database dieses Mal gutgegangen." )

        def onExportError(args=None):
            print( "uups - something went wrong" )
            msg = ""
            if args:
                for arg in args:
                    print( arg )
                    msg += str(arg)
                    msg += "\n"
            self._win.setCursor( Qt.ArrowCursor )
            box2 = ErrorBox( "Datenbank-Export", "Export der Datenbank fehlgeschlagen.", msg )
            box2.exec_()
            self._rcFtpExportDatabase = False

        self._rcFtpExportDatabase = None
        try:
            self._saveLetzteBuchung()
        except Exception as ex:
            box = WarningBox( "Speichern der letzten Buchung", "Speichern fehlgeschlagen: " + str(ex),
                              "Datenbank trotzdem exportieren?", "Ja", "Nein" )
            if box.exec_() != QMessageBox.Yes:
                return False

        self._win.setCursor( Qt.WaitCursor )
        worker = Worker( self._logic.exportDatabaseToServer )
        worker.signals.finished.connect( onExported )
        worker.signals.error.connect( onExportError )
        worker.signals.result.connect( onExportResult )
        infopanel = InfoPanel( "Bitte warten", "Datenbank wird zum Server exportiert..." )
        infopanel.moveToCursor()
        infopanel.show()
        infopanel.raise_()
        self._threadpool.start( worker )
        while self._rcFtpExportDatabase is None:
            QApplication.processEvents()
        infopanel.close()
        self._win.setCursor( Qt.ArrowCursor )
        return True

    def onSaveDatabase( self ) -> None:
        def try_saveLetzteBuchung() -> bool:
            try:
                self._saveLetzteBuchung()
                return True
            except Exception as ex:
                box = ErrorBox( "Speichern der letzten Buchung", "Speichern fehlgeschlagen: " + str( ex ),
                                  "Datenbank wird nicht auf externe Festplatte gesichert." )
                box.exec_()
                return False
        def try_copyfile():
            try:
                copyfile( src, dest )
            except Exception as ex:
                box = WarningBox( "Datenbank auf lokalen Datenträger sichern",
                                  "Sicherung nicht möglich:\n\n" + str( ex ),
                                  "Ist der Datenträger eingehängt?", "Nochmal versuchen", "Beenden" )
                rc = box.exec_()
                if rc == QMessageBox.Yes:
                    try_copyfile()
        # Zuerst die letzte Buchung speichern, dann auf Festplatte sichern
        if not try_saveLetzteBuchung():
            return
        from shutil import copyfile
        scriptdir = os.path.dirname( os.path.realpath( __file__ ) )
        src = ROOT_DIR + "/immo.db"
        if "Vermietung" in scriptdir:
            print( "Running in REL; try to copy immo.db" )
            dest = "/media/martin/Elements1/Vermietung_V2/ImmoControlCenter/v2/icc/immo.db"
        elif "Projects/python" in scriptdir:
            print( "Running in DEV; try to copy immo.db" )
            dest = "/media/martin/Elements1/Projects/python/ImmoControlCenter/v2/icc/immo.db"
        if os.path.isfile( src ):
            box = QMessageBox()
            box.setIcon( QMessageBox.Question )
            box.setWindowTitle( "Sicherung der Datenbank" )
            box.setText( "Datenbank\n\n   '%s'\n\nsichern in\n\n   '%s'?" % (scriptdir + "/immo.db", dest) )
            box.setStandardButtons( QMessageBox.Save | QMessageBox.Cancel )
            r = box.exec_()
            if r == QMessageBox.Save:
                try_copyfile()
        else:
            box = ErrorBox( "Datenbank auf lokalen Datenträger sichern", "Sicherung nicht möglich",
                            "Es gibt keine Datenbank namens immo.db" )
            box.exec_()


####################################################################################
def testScreenSize( win:IccMainWindow ):
    from PySide6 import QtWidgets
    #from PySide6.QtWidgets import QDesktopWidget
    app = QtWidgets.QApplication.instance()

    r = win.rect()
    print( r )

    screens = app.screens()
    for screen in screens:
        rect = screen.availableGeometry()
        print( rect )

    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    print( rect )

    # rect2 = QDesktopWidget().availableGeometry()
    # print( rect2 )
    # return rect

def test():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QSize

    app = QApplication()
    c = MainController( "DEVELOP" )
    win = c.createGui()
    win.show()
    # testScreenSize( win )
    w = win.getPreferredWidth()
    #h = win.getPreferredHeight()
    win.resize( QSize( w, 1000 ) )
    app.exec_()