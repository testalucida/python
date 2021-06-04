from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QTabWidget, QApplication, QDialog

from anlage_v.anlagev_preview_logic import AnlageV_Preview_Logic
from anlage_v.anlagev_gui import AnlageVView, AnlageVTableView, AnlageVAuswahlDialog
from anlage_v.anlagev_tablemodel import AnlageVTableModel
from anlage_v.ausgabenmodel import AusgabenModel
from constants import DetailLink
from generictableviewdialog import GenericTableViewDialog
from mdisubwindow import MdiSubWindow


class AnlageVController:
    """
    Controller für AnlageVView.
    Lässt den Anwender beim Aufruf von startWork() eine Liste von Master-Objekten bestimmen,
    die dann in der AnlageVView angezeigt werden.
    """
    def __init__( self ):
        self._master_objekte:List[str] = list()
        self._jahr:int = 0
        self._subwin:MdiSubWindow = MdiSubWindow()
        self._view:AnlageVView = AnlageVView()
        self._view.openAnlageV.connect( self.onOpenAnlageV )
        self._tmlist:List[AnlageVTableModel] = list()
        try:
            self._busi:AnlageV_Preview_Logic = AnlageV_Preview_Logic()
        except Exception as ex:
            print( str(ex) )

    def createView( self ) -> AnlageVView:
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

    def onAnlageVLeftClick( self, master_objekt:str, jahr:int, row:int, column:int ) -> None:
        #print( "AnlageV clicked: %s, %d, %d, %d" % (master_objekt, jahr, row, column ) )
        col = self._tmlist[0].getDetailLinkColumnIndex()
        if col == column:
            tm = self._getAnlageVTableModel( master_objekt )
            linkvalue = tm.getValue( row, column )
            if linkvalue:
                if linkvalue == DetailLink.ALLGEMEINE_KOSTEN.value[0]:
                    tm:AusgabenModel = self._busi.getAllgemeineAusgabenModel( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Allgemeine Hauskosten" )
                elif linkvalue == DetailLink.ERHALTUNGSKOSTEN.value[0]:
                    tm:AusgabenModel = self._busi.getReparaturausgabenNichtVerteilt( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Voll abzuziehende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.ZU_VERTEIL_GESAMTKOSTEN_VJ.value[0]:
                    # Aufwände, die im VJ entstanden und zu verteilen sind
                    tm:AusgabenModel = self._busi.getZuVerteilendeAufwaende( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Im VJ zu verteilende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.ERHALTUNGSKOSTEN_VERTEILT.value[0]:
                    # Anzusetzende Teilbeträge der Aufwände, die im VJ und den vergangenen 4 Jahren entstanden sind
                    tm:AusgabenModel = self._busi.getReparaturausgabenVerteilt( master_objekt, jahr )
                    self._showAusgabenDialog( tm, "Anteilig anzusetzende Erhaltungsaufwendungen" )
                elif linkvalue == DetailLink.SONSTIGE_KOSTEN.value[0]:
                    pass

    def _showAusgabenDialog( self, tm:AusgabenModel, title:str ):
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


def testPreview():
    app = QApplication()
    ctrl = AnlageVController( )
    # tm:AusgabenModel = ctrl._busi.getAusgabenModel( "ILL_Eich", 2021 )
    # ctrl._showAusgabenDialog( tm )
    win = ctrl.createView()
    win.show()

    app.exec_()

if __name__ == "__main__":
    testPreview()