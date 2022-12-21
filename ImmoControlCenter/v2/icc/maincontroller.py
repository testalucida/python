from typing import List, Iterable

from PySide2.QtWidgets import QMenu

from base.baseqtderivates import BaseAction
from base.messagebox import InfoBox, ErrorBox
from v2.abrechnungen.abrechnungcontroller import NKAbrechnungController, HGAbrechnungController
from v2.einaus.einauscontroller import EinAusController
from v2.einaus.einauswritedispatcher import EinAusWriteDispatcher
from v2.icc.constants import EinAusArt
from v2.icc.icccontroller import IccController
from v2.icc.iccmainwindow import IccMainWindow
from v2.icc.iccwidgets import IccCheckTableViewFrame
from v2.icc.interfaces import XEinAus, XSummen
from v2.icc.mainlogic import MainLogic
from v2.mtleinaus.mtleinauscontroller import MieteController, HausgeldController, AbschlagController


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
        EinAusWriteDispatcher.inst().ea_inserted.connect( self.onEinAusInserted )
        EinAusWriteDispatcher.inst().ea_updated.connect( self.onEinAusUpdated )
        EinAusWriteDispatcher.inst().ea_deleted.connect( self.onEinAusDeleted )
        # Summenfelder versorgen

    def createGui( self ) -> IccMainWindow:
        self._win = IccMainWindow( self._env )
        self._win.addMenu( self.getMenu() )
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
        # todo
        # HGAbrechnungen
        tvf: IccCheckTableViewFrame = self._hgaCtrl.createGui()
        # todo
        self._win.setHGAbrechnungenTableViewFrame( tvf )
        # NKAbrechnungen
        tvf: IccCheckTableViewFrame = self._nkaCtrl.createGui()
        # todo
        self._win.setNKAbrechnungenTableViewFrame( tvf )
        ### Die View für "alle" Zahlungen (Rechnungen etc.)
        tvf: IccCheckTableViewFrame = self._einausCtrl.createGui()
        self._win.setAlleZahlungenTableViewFrame( tvf )
        self._provideSummen()
        return self._win

    def getMenu( self ) -> QMenu:
        menu = QMenu( "ImmoCenter" )
        # Menü "Datenbank zum Server exportieren"
        action = BaseAction( "Datenbank zum Server exportieren", parent=menu )
        action.triggered.connect( self.onExportDatabase )
        menu.addAction( action )

        # Menü "Datenbank vom Server importieren"
        action = BaseAction( "Datenbank vom Server importieren", parent=menu )
        action.triggered.connect( self.onImportDatabase )
        menu.addAction( action )

        menu.addSeparator()

        # # Menüpunkt "Ende"
        action = BaseAction( "Ende", parent=menu )
        action.triggered.connect( self.onExit )
        action.setShortcut( "Alt+F4")
        menu.addAction( action )
        return menu

    def _provideSummen( self ):
        summen:XSummen = self._logic.getSummen( self.getYearToStartWith() )
        self._win.setSummenValues( summen )

    def onEinAusInserted( self, x:XEinAus ):
        summen = self._win.getSummenValues()
        betrag = round(x.betrag)
        summen.saldo += betrag
        if x.ea_art == EinAusArt.HAUSGELD_VORAUS.display:
            summen.sumHGV += betrag
        elif x.betrag < 0:
            summen.sumSonstAus += betrag
        elif x.betrag >= 0:
            summen.sumEin += betrag
        else:
            # hoppala!
            box = ErrorBox( "Interner Fehler", "MainController.onEinAusInserted:\nNicht bedachte Konstellation!\n",
                            more=x.toString() )
            box.exec_()
            return
        self._win.setSummenValues( summen )

    def onEinAusUpdated( self, x:XEinAus ):
        print( "onEinAusUpdated")

    def onEinAusDeleted( self, x:XEinAus ):
        print( "onEinAusDeleted")

    def onExportDatabase( self ):
        try:
            self._logic.exportDatabaseToServer()
            box = InfoBox( "Datenbank-Export", "Export der Datenbank abgeschlossen.", "", "OK" )
            box.exec_()
        except Exception as ex:
            box = ErrorBox( "Datenbank-Export", "Export der Datenbank fehlgeschlagen.", str(ex) )
            box.exec_()

    def onImportDatabase( self ):
        try:
            self._logic.importDatabaseFromServer()
            # todo: nach Dateinamen fragen etc.
            box = InfoBox( "Datenbank-Import", "Import der Datenbank abgeschlossen.", "", "OK" )
            box.exec_()
        except Exception as ex:
            box = ErrorBox( "Datenbank-Import", "Import der Datenbank fehlgeschlagen.", str(ex) )
            box.exec_()

    def onExit( self ):
        print( "onExit" )


def testScreenSize( win:IccMainWindow ):
    from PySide2 import QtWidgets
    from PySide2.QtWidgets import QDesktopWidget
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

    rect2 = QDesktopWidget().availableGeometry()
    print( rect2 )
    return rect

def test():
    from PySide2.QtWidgets import QApplication
    from PySide2.QtCore import QSize

    app = QApplication()
    c = MainController( "DEVELOP" )
    win = c.createGui()
    win.show()
    # testScreenSize( win )
    w = win.getPreferredWidth()
    #h = win.getPreferredHeight()
    win.resize( QSize( w, 1000 ) )
    app.exec_()