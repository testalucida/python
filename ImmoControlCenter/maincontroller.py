from typing import List

from PySide2.QtCore import QAbstractItemModel, QObject, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QDialog, QApplication

from anlage_v.anlagev_controller import AnlageVController
from business import BusinessLogic
from dictlisttablemodel import DictListTableModel
from generictable_stuff.customtableview import CustomTableView
from geschaeftsreise.geschaeftsreisencontroller import GeschaeftsreisenController
from icc.iccdialog import IccDialog
from icc.iccmainwindow import IccMainWindow, MainWindowAction
from checkcontroller import MietenController, HGVController
from messagebox import ErrorBox, InfoBox
from mietobjekt.mietobjektcontroller import MietobjektController
from mietobjekt.mietobjektview import MietobjektView
from mietverhaeltnis.mieterwechselcontroller import MieterwechselController
from mietverhaeltnis.mietverhaeltniscontroller import MietverhaeltnisController
from mtleinaus.mtleinausservices import MtlEinAusServices
from notizen.notizencontroller import NotizenController
from offene_posten.offenepostencontroller import OffenePostenController
from qtderivates import AuswahlDialog
from rendite.renditecontroller import RenditeController
from returnvalue import ReturnValue
from sollzahlungencontroller import SollmietenController, SollHgvController
from sonstaus.sonstauscontroller import SonstAusController
from sumfieldsprovider import SumFieldsProvider
from abrechnungencontroller import NkAbrechnungenController, HgAbrechnungenController


class MainController( QObject ):
    def __init__( self, win:IccMainWindow ):
        QObject.__init__( self )
        self._mainwin:IccMainWindow = win
        datum, text = BusinessLogic.inst().getLetzteBuchung()
        win.setLetzteBuchung( datum, text )
        win.setTabellenAuswahl( BusinessLogic.inst().getIccTabellen() )
        win.setActionCallback( self.onMainWindowAction )
        win.setShutdownCallback( self.onShutdown )

        #win.bringDialogToFront.connect( self.onBringDialogToFront )
        #win.showTableContent.connect( self.onShowTableContent )

        self._mietverhaeltnisDlg:IccDialog = None
        self._mieteDlg:IccDialog = None
        self._hgvDlg:IccDialog = None
        self._sonstAusDlg:IccDialog = None
        self._oposDlg:IccDialog = None
        self._sollMietenDlg:IccDialog = None
        self._sollHausgeldDlg:IccDialog = None
        self._nkaDlg:IccDialog = None
        self._hgaDlg:IccDialog = None
        self._notizenDlg:IccDialog = None
        self._renditeDlg:IccDialog = None
        self._anlageVDlg:IccDialog = None
        self._mieterWechselDlg:IccDialog = None
        self._mietobjektDlg:IccDialog = None
        self._geschaeftsreiseDlg:IccDialog = None
        self._anlageVDlg:IccDialog = None

        self._mietverhaeltnisCtrl = MietverhaeltnisController()
        self._mietenCtrl:MietenController = MietenController()
        self._mietenCtrl.changedCallback = self.onViewChanged
        self._mietenCtrl.savedCallback = self.onViewSaved
        self._hgvCtrl:HGVController = HGVController()
        self._hgvCtrl.changedCallback = self.onViewChanged
        self._hgvCtrl.savedCallback = self.onViewSaved
        self._sonstAusCtrl:SonstAusController = SonstAusController()
        self._sonstAusCtrl.changedCallback = self.onViewChanged
        self._sonstAusCtrl.savedCallback = self.onViewSaved
        self._sollMietenCtrl = SollmietenController()
        self._sollHausgelderCtrl = SollHgvController()
        self._nkaCtrl = NkAbrechnungenController()
        self._hgaCtrl = HgAbrechnungenController()
        self._oposCtrl:OffenePostenController = OffenePostenController()
        self._notizenCtrl:NotizenController = NotizenController()
        self._renditeCtrl:RenditeController = RenditeController()
        self._anlageVCtrl: AnlageVController = None
        self._mieterWechselCtrl:MieterwechselController = None
        self._mietobjektCtrl:MietobjektController = None
        self._geschaeftsreiseCtrl:GeschaeftsreisenController = None
        self._nChanges = 0  # zählt die Änderungen, damit nach Speichern-Vorgängen das Sternchen nicht zu früh entfernt wird.
        self._x, self._y = 0, 0
        self._provideSumFields()

    def _provideSumFields( self ):
        #sumMieten, sumAusgaben, sumHGV = BusinessLogic.inst().getSummen()
        sfa:SumFieldsProvider = SumFieldsProvider.inst()
        sfa.setSumFields()
        #sfa.setSumMieten( sumMieten )
        #sfa.setSumAusgaben( sumAusgaben )
        #sfa.setSumHGV( sumHGV )

    # def showStartViews( self ):
    #     self.showMieteView()
    #     # self.showHGVView()
    #     # self.showSonstAusView()

    def onMainWindowAction( self, action:MainWindowAction, arg=None ):
        """
        Hier laufen alle Menü-Auswahlen ein, die der User trifft (klickt)
        :param action:
        :return:
        """
        switcher = {
            MainWindowAction.OPEN_OBJEKT_STAMMDATEN_VIEW: self.showObjektStammdatenDialog,
            MainWindowAction.OPEN_MIETVERH_VIEW: self.showMietverhaeltnis,
            MainWindowAction.SAVE_ALL: self._saveAll,
            #MainWindowAction.PRINT_ACTIVE_VIEW: self._printActiveView,
            MainWindowAction.OPEN_MIETE_VIEW: self.showMieteView,
            MainWindowAction.OPEN_HGV_VIEW: self.showHGVView,
            MainWindowAction.FOLGEJAHR: self.createFolgejahr,
            MainWindowAction.OPEN_SOLL_MIETE_VIEW: self.showSollMietenView,
            MainWindowAction.OPEN_SOLL_HG_VIEW: self.showSollHausgelderView,
            MainWindowAction.OPEN_NKA_VIEW: self.showNKAbrechnungenView,
            MainWindowAction.OPEN_HGA_VIEW: self.showHGAbrechnungenView,
            MainWindowAction.OPEN_SONST_EIN_AUS_VIEW: self.showSonstAusView,
            MainWindowAction.OPEN_ANLAGEV_VIEW: self.showAnlageVView,
            MainWindowAction.EXPORT_CSV: self.exportToCsv,
            MainWindowAction.OPEN_OFFENE_POSTEN_VIEW: self.showOffenePostenView,
            MainWindowAction.NOTIZEN: self.showNotizenView,
            MainWindowAction.RENDITE_VIEW: self.showRenditeView,
            MainWindowAction.MIETERWECHSEL: self.showMieterwechselDialog,
            MainWindowAction.OPEN_GESCHAEFTSREISE_VIEW: self.showGeschaeftsreiseDialog,
            MainWindowAction.SAMMELABGABE_DETAIL: self.showSammelAbgabeDialog,
            MainWindowAction.EXIT: self.exit
        }

        fnc = switcher.get( action )
        if not fnc:
            if action == MainWindowAction.SHOW_TABLE_CONTENT:
                self.showTableContent( arg )
            elif action == MainWindowAction.BRING_DIALOG_TO_FRONT:
                self.bringDialogToFront( arg )
            return

        try:
            fnc()
        except Exception as ex:
            print( "MainController.onMainWindowAction()\n" + str( ex ) )
            self._mainwin.showException( "function call failed",
                                         "MainController.onMainWindowAction():\nconcerned action: '%s'." %
                                         (str( action ) ) )

    def exit( self ):
        self._mainwin.close()

    def onViewChanged( self ):
        self._mainwin.setWindowTitle( "ImmoControlCenter *" )
        self._someViewChanged = True
        self._nChanges += 1

    def onViewSaved( self ):
        self._nChanges -= 1
        if self._nChanges == 0:
            self._mainwin.setWindowTitle( "ImmoControlCenter" )
            self._someViewChanged = False


    def _saveAll( self ):
        self._setLetzteBuchung()

    def _showDialog( self, dlg:IccDialog, w, h ):
        win = self._mainwin
        x = win.x()
        print( win.y(), " / " , win.height() )
        y = win.y() + win.height() + 50 # 120
        dlg.setGeometry( x, y, w, h )
        title = dlg.windowTitle()
        win.addOpenedDialog( title, dlg )
        dlg.dialogClosing.connect( lambda name=title, data=dlg: win.removeClosedDialog( title, dlg ) )
        dlg.show()

    def showMietverhaeltnis( self ):
        self._mietverhaeltnisDlg = self._mietverhaeltnisCtrl.createDialog( self._mainwin )
        if self._mietverhaeltnisDlg:
            w = 900
            h = 500
            self._showDialog( self._mietverhaeltnisDlg, w, h )

    def showMieteView( self ):
        self._mieteDlg = self._mietenCtrl.createDialog( self._mainwin )
        if self._mieteDlg:
            w = self._mieteDlg.getPreferredWidth()
            h = 900 #screen.screenheight
            #x, y = self._getXY( self._mieteDlg )
            self._showDialog( self._mieteDlg, w, h )

    def showHGVView( self ):
        self._hgvDlg = self._hgvCtrl.createDialog( self._mainwin )
        #w = self._hgvDlg.getPreferredWidth()
        w = 1550
        h = 730
        #x, y = self._getXY( self._hgvDlg )
        self._showDialog( self._hgvDlg, w, h )

    def showSonstAusView( self ):
        self._sonstAusDlg = self._sonstAusCtrl.createDialog( self._mainwin )
        w = 1800
        h = 900
        #x, y = self._getXY( self._sonstAusDlg )
        self._showDialog( self._sonstAusDlg, w, h )

    def showOffenePostenView( self ):
        self._oposDlg = self._oposCtrl.createDialog( self._mainwin )
        w = 1000
        h = 900
        #x, y = self._getXY( self._oposDlg )
        self._showDialog( self._oposDlg, w, h )

    def showSollMietenView( self ):
        self._sollMietenDlg = self._sollMietenCtrl.createDialog( self._mainwin )
        w = 1100
        h = 950
        self._showDialog( self._sollMietenDlg, w, h )

    def showSollHausgelderView( self ):
        self._sollHausgeldDlg = self._sollHausgelderCtrl.createDialog( self._mainwin )
        w = 1100
        h = 1000
        self._showDialog( self._sollHausgeldDlg, w, h )

    def showNKAbrechnungenView( self ):
        self._nkaDlg = self._nkaCtrl.createDialog( self._mainwin )
        w = 1500
        h = 950
        self._showDialog( self._nkaDlg, w, h )

    def showHGAbrechnungenView( self ):
        self._hgaDlg = self._hgaCtrl.createDialog( self._mainwin )
        w = 1500
        h = 950
        self._showDialog( self._hgaDlg, w, h )

    def showNotizenView( self ):
        self._notizenDlg = self._notizenCtrl.createDialog( self._mainwin )
        w = 1200
        h = 800
        self._showDialog( self._notizenDlg, w, h )

    def showRenditeView( self ):
        self._renditeDlg = self._renditeCtrl.createDialog( self._mainwin )
        w = 1100
        h = 900
        self._showDialog( self._renditeDlg, w, h )

    def showAnlageVView( self ):
        self._anlageVCtrl = AnlageVController()
        self._anlageVDlg = self._anlageVCtrl.createDialog( self._mainwin )
        if self._anlageVDlg:
            self._showDialog( self._anlageVDlg, 1300, 1300 )

    def showMieterwechselDialog( self ):
        self._mieterWechselCtrl = MieterwechselController()
        self._mieterWechselDlg = self._mieterWechselCtrl.createDialog( self._mainwin )
        if not self._mieterWechselDlg: return
        w = 900
        h = 900
        self._showDialog( self._mieterWechselDlg, w, h )

    def showGeschaeftsreiseDialog( self ):
        self._geschaeftsreiseCtrl = GeschaeftsreisenController()
        self._geschaeftsreiseDlg = self._geschaeftsreiseCtrl.createDialog( self._mainwin )
        w = 1500
        h = 900
        self._showDialog( self._geschaeftsreiseDlg, w, h )

    def showObjektStammdatenDialog( self ):
        self._mietobjektCtrl = MietobjektController()
        self._mietobjektDlg = self._mietobjektCtrl.createDialog( self._mainwin )
        if not self._mietobjektDlg: return
        view:MietobjektView = self._mietobjektDlg.getView()
        #view.edit_verwaltung.connect( )
        w = 1000
        h = 550
        self._showDialog( self._mietobjektDlg, w, h )

    def showSammelAbgabeDialog( self ):

        raise NotImplementedError( "MainController.showSammelAbgabeDialog" )

    def exportToCsv( self ):
        self._mainwin.setCursor( Qt.WaitCursor )
        QApplication.processEvents()
        dlgs:List[IccDialog] = self._mainwin.getOpenedDialogs()
        titles = [d.windowTitle() for d in dlgs]
        cnt = len( titles )
        if cnt == 0:
            box = InfoBox( "CSV-Export", "Kein Dialog zum Exportieren geöffnet.", "", "OK" )
            box.exec_()
        elif cnt == 1:
            self._doCsvExport( dlgs[0] )
        else:
            dlgAuswahlDlg = AuswahlDialog()
            dlgAuswahlDlg.appendItemList( titles )
            if dlgAuswahlDlg.exec_() == QDialog.Accepted:
                selTitle:str = dlgAuswahlDlg.getSelection()[0][0]
                selDlg:IccDialog = [d for d in dlgs if d.windowTitle() == selTitle][0]
                self._doCsvExport( selDlg )
        self._mainwin.setCursor( Qt.ArrowCursor )
        QApplication.processEvents()

    def _doCsvExport( self, dlg:IccDialog ):
        model: QAbstractItemModel = dlg.getView().getModel()
        try:
            BusinessLogic.inst().exportToCsv( model )
        except Exception as ex:
            box = ErrorBox( "Export als .csv-Datei", str( ex ), "in MainController.exportToCsv()" )
            box.exec_()

    def bringDialogToFront( self, data: IccDialog ):
        dlg:IccDialog = data
        dlg.activateWindow()

    def showTableContent( self, table:str ):
        dictList = BusinessLogic.inst().getTableContent( table )
        tm = DictListTableModel( dictList )
        dlg = IccDialog( self._mainwin )
        dlg.mayClose = lambda : 1 == 1
        tv = CustomTableView()
        tv.setModel( tm )
        tv.setFont( QFont( "Arial", 12 ) )
        tv.resizeColumnsToContents()
        tv.resizeRowsToContents()
        tv.setSortingEnabled( True )
        tm.setSortable( True )
        tm.layoutChanged.connect( tv.resizeRowsToContents )  ## <======== WICHTIG bei mehrzeiligem Text in einer Zelle!
        dlg.setView( tv )
        dlg.setWindowTitle( table )
        w = 0
        for c in range( tm.columnCount() ):
            w += tv.columnWidth( c )
        self._showDialog( dlg, w, 900 )

    def onShutdown( self ) -> bool:
        if not ( self._mietenCtrl.mayDialogClose() and
                 self._hgvCtrl.mayDialogClose() and
                 self._sonstAusCtrl.mayDialogClose() and
                 self._sollMietenCtrl.mayDialogClose() and
                 self._sollHausgelderCtrl.mayDialogClose() and
                 self._nkaCtrl.mayDialogClose() and
                 self._hgaCtrl.mayDialogClose() and
                 self._oposCtrl.mayDialogClose() and
                 self._notizenCtrl.mayDialogClose() ):
            return False
        self._setLetzteBuchung()
        return True

    def _setLetzteBuchung( self ):
        d = self._mainwin.getLetzteBuchung()
        try:
            BusinessLogic.inst().setLetzteBuchung( d["datum"], d["text"] )
        except Exception as ex:
            self._mainwin.showException( str( ex ), "MainController.onShutdown()" )

    def createFolgejahr( self ):
        retval:ReturnValue = MtlEinAusServices.processFolgejahrNeu()
        if not retval.missionAccomplished():
            self._mainwin.showException( retval.exceptiontype, retval.errormessage )
        else:
            self._mietenCtrl.addJahr( retval.returnvalue )
            self._hgvCtrl.addJahr( retval.returnvalue )
            self._mainwin.showInfo( "Folgejahr eingerichtet.", "Das Folgejahr wurde eingerichtet." )

def test():
    import sys
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication( sys.argv )
    win = IccMainWindow()
    mc = MainController( win )
    mc.showSollMietenView()

    # c = SollHgvController()
    # v = c.createView()
    win.setGeometry( 2000, 100, 1000, 800 )
    win.show()

    sys.exit( app.exec_() )


if __name__ == "__main__":
    test()