from typing import List, Any

from PySide2.QtCore import Slot, QObject
from PySide2.QtWidgets import QApplication, QDialog, QMessageBox

from anlage_v.anlagev_preview_logic import AnlageV_Preview_Logic
from anlage_v.anlagev_gui import AnlageVView, AnlageVTableView, AnlageVAuswahlDialog #, AnlageVDialog
from anlage_v.anlagev_print_logic import AnlageV_Print_Logic
from anlage_v.anlagev_tablemodel import AnlageVTableModel
from anlage_v.anlagev_ausgabentablemodel import AnlageV_AusgabenTableModel
from constants import DetailLink
from generictable_stuff.generictableviewdialog import GenericTableViewDialog
from icccontroller import IccController
from mdisubwindow import MdiSubWindow


class AnlageVController( IccController ):
    """
    Controller für AnlageVView.
    Lässt den Anwender beim Aufruf von startWork() eine Liste von Master-Objekten bestimmen,
    die dann in der AnlageVView angezeigt werden.
    Dieser Controller hat nichts mit der Druckfunktion zu tun.
    Er sendet nur ein Signal, wenn der Anwender einen der Drucken-Buttons gedrückt hat.
    """
    def __init__( self ):
        IccController.__init__( self )
        self._master_objekte:List[str] = list()
        self._jahr:int = 0
        self._subwin:MdiSubWindow = MdiSubWindow()
        self._view:AnlageVView = AnlageVView()
        self._tmlist:List[AnlageVTableModel] = list()
        try:
            self._busi:AnlageV_Preview_Logic = AnlageV_Preview_Logic()
        except Exception as ex:
            print( str(ex) )

    def createView( self ) -> AnlageVView:
        self._view.openAnlageV.connect( self.onOpenAnlageV )
        self._view.printAnlageV.connect( self.onPrintAnlageV )
        self._view.printAllAnlageV.connect( self.onPrintAllAnlageV )
        master_objekte = self._busi.getObjektNamen()
        jahre = self._busi.getJahre()
        accepted, jahr, objlist = self.showAnlageVAuswahlDialog( jahre, master_objekte )
        if accepted:
            self._jahr = jahr
            self._master_objekte = objlist
            self._provideTabs( objlist )
            return self._view
        else:
            self._jahr = 0
            self._master_objekte.clear()
            return None

    # def createDialog( self, parent ) -> AnlageVDialog:
    #     """
    #     instead of only creating a view (and getting returned that view)
    #     a dialog containing this view may be created.
    #     A parent must be given so that the dialog can be non-modal.
    #     """
    #     view = self.createView()
    #     dlg = AnlageVDialog( view, parent )
    #     return dlg

    def showAnlageVAuswahlDialog( self, jahre:List[int], master_objekte:List[str] ) -> [bool, int, List]:
        """
        zeigt den Objekt-Auswahldialog und liefert die ausgewählten Objekte und das ausgewählte Jahr zurück
        :return: accepted: True/False, jahr, Liste der ausgewählten Masterobjekte
        """
        dlg = AnlageVAuswahlDialog( master_objekte, jahre, checked=False )
        if len( jahre ) > 1:
            dlg.setCurrentJahr( jahre[len( jahre ) - 2] )
        dlg.setMinimumHeight( len( master_objekte * 30 ) )
        if dlg.exec_() == QDialog.Accepted:
            ausw = dlg.getAuswahl()
            return True, ausw[0], ausw[1]
        else:
            return False, 0, None

    def _provideTabs( self, master_objekte:List[str] ):
        for obj in master_objekte:
            tm = self._busi.getAnlageVTableModel( obj, self._jahr )
            self._tmlist.append( tm )
            tv:AnlageVTableView = self._view.addAnlageV( tm )
            tv.cell_clicked.connect( self.onAnlageVLeftClick )

    @Slot()
    def onOpenAnlageV( self ):
        master_objekte = self._busi.getObjektNamen()  # alle Objekte holen
        # nur die zur Auswahl geben, die noch nicht geöffnet sind:
        rem = [x for x in master_objekte if x not in self._master_objekte]
        if self._jahr == 0:
            jahre = self._busi.getJahre()
        else:
            jahre = [self._jahr,]
        accepted, jahr, objlist = self.showAnlageVAuswahlDialog( jahre, rem )
        if accepted:
            self._jahr = jahr
            self._master_objekte.extend( objlist )
            self._provideTabs( objlist )

    @Slot()
    def onPrintAnlageV( self ):
        master_name:str = self._view.getActiveAnlageV()
        self._doPrinting( [master_name,] )

    @Slot()
    def onPrintAllAnlageV( self ):
        self._doPrinting( self._master_objekte )

    def testPrinting( self, master_name:str, jahr:int ):
        self._jahr = jahr
        self._doPrinting( [master_name,] )

    def _doPrinting( self, master_names:List[str] ):
        mb = QMessageBox()
        ret = mb.question( self._view, "", "Nur Kopfdaten drucken?", mb.Yes | mb.No )
        onlyKopfdaten = False
        if ret == mb.Yes:
            onlyKopfdaten = True
        printCtrl = AnlageV_Print_Logic()
        printCtrl.printAnlagenV( master_names, self._jahr, onlyKopfdaten )

    def onAnlageVLeftClick( self, master_objekt:str, jahr:int, row:int, column:int ) -> None:
        #print( "AnlageV clicked: %s, %d, %d, %d" % (master_objekt, jahr, row, column ) )
        col = self._tmlist[0].getDetailLinkColumnIndex()
        if col == column:
            tm = self._getAnlageVTableModel( master_objekt )
            linkvalue = tm.getValue( row, column )
            if linkvalue:
                if linkvalue == DetailLink.ALLGEMEINE_KOSTEN.value[0]:
                    tm:AnlageV_AusgabenTableModel = self._busi.getAllgemeineAusgabenModel( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Allgemeine Hauskosten" )
                elif linkvalue == DetailLink.ERHALTUNGSKOSTEN.value[0]:
                    tm:AnlageV_AusgabenTableModel = self._busi.getReparaturausgabenNichtVerteilt( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Voll abzuziehende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.ZU_VERTEIL_GESAMTKOSTEN_VJ.value[0]:
                    # Aufwände, die im VJ entstanden und zu verteilen sind
                    tm:AnlageV_AusgabenTableModel = self._busi.getZuVerteilendeAufwaende( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Im VJ zu verteilende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.ERHALTUNGSKOSTEN_VERTEILT.value[0]:
                    # Anzusetzende Teilbeträge der Aufwände, die im VJ und den vergangenen 4 Jahren entstanden sind
                    tm:AnlageV_AusgabenTableModel = self._busi.getReparaturausgabenVerteilt( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Anteilig anzusetzende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.SONSTIGE_KOSTEN.value[0]:
                    pass

    def _showAusgabenDialog( self, tm:AnlageV_AusgabenTableModel, title:str ):
        dlg = GenericTableViewDialog( tm )
        dlg.setWindowTitle( "%s für %s" % (title, tm.getMasterName()) )
        dlg.setCancelButtonVisible( False )
        dlg.setOkButtonText( "Schließen" )
        dlg.exec_()

    def _getAnlageVTableModel( self, master_objekt:str ) -> AnlageVTableModel:
        for tm in self._tmlist:
            if tm.getMasterName() == master_objekt:
                return tm
        raise NameError( "AnlageVController._getAnlageVTableModel(): TableModel for master_object '%s' not found."
                         % (master_objekt) )

    ####### Implementierung der abstrakten Methonden von IccController
    def isChanged( self ) -> bool:
        return False

    def getChanges( self ) -> Any:
        return None

    def writeChanges( self, changes: Any = None ) -> bool:
        return True

    def clearChanges( self ) -> None:
        pass

    def getViewTitle( self ) -> str:
        return "Anlagen V ausgewählter Objekte"


def testPreview():
    app = QApplication()
    ctrl = AnlageVController( )
    # ctrl.testPrinting( "ILL_Eich", 2021 )
    # tm:AusgabenModel = ctrl._busi.getAusgabenModel( "ILL_Eich", 2021 )
    # ctrl._showAusgabenDialog( tm )
    win = ctrl.createView()
    #win.resize( 900, 900 )
    win.setGeometry( 1700, 50, 1400, 1300 )
    win.show()

    app.exec_()

if __name__ == "__main__":
    testPreview()