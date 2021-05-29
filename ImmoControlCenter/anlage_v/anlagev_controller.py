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
        self._tmlist:List[AnlageVTableModel] = list()
        self._busi:AnlageV_Preview_Logic = AnlageV_Preview_Logic()

    def startWork( self ):
        self._master_objekte = self._busi.getObjektNamen()
        jahre = self._busi.getJahre()
        dlg = AnlageVAuswahlDialog( self._master_objekte, jahre, checked=False )
        if len( jahre ) > 1:
            dlg.setCurrentJahr( jahre[len(jahre)-2])
        dlg.setMinimumHeight( len( self._master_objekte * 30 ) )
        if dlg.exec_() == QDialog.Accepted:
            ausw = dlg.getAuswahl()
            self._jahr = ausw[0]
            self._master_objekte = ausw[1]
            #print( '\n'.join( [str( s ) for s in dlg.choices] ) )
            self._createSubwindow()

    def _createSubwindow( self ):
        for obj in self._master_objekte:
            tm = self._busi.getAnlageVTableModel( obj, self._jahr )
            self._tmlist.append( tm )
            tv:AnlageVTableView = self._view.addAnlageV( tm )
            tv.cell_clicked.connect( self.onAnlageVLeftClick )
        self._subwin.setWidget( self._view )
        self._subwin.setWindowTitle( "Anlagen V ausgewählter Objekte" )
        #self._subwin.addQuitCallback( self.onCloseSubWindow )
        self._subwin.setMinimumSize( 1300, 1300 )
        self._subwin.show()

    def onAnlageVLeftClick( self, master_objekt:str, jahr:int, row:int, column:int ) -> None:
        #print( "AnlageV clicked: %s, %d, %d, %d" % (master_objekt, jahr, row, column ) )
        col = self._tmlist[0].getDetailLinkColumnIndex()
        if col == column:
            tm = self._getAnlageVTableModel( master_objekt )
            linkvalue = tm.getValue( row, column )
            if linkvalue:
                if linkvalue == DetailLink.ALLGEMEINE_KOSTEN.value[0]:
                    tm:AusgabenModel = self._busi.getAusgabenModel( master_objekt, jahr )
                    self._showAusgabenDialog( tm )

    def _showAusgabenDialog( self, tm:AusgabenModel ):
        dlg = GenericTableViewDialog( tm )
        dlg.setWindowTitle( "Allgemeine Hauskosten für %s" % tm.getMasterName() )
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
    ctrl.startWork()
    # win = ctrl.createSubwindow()
    # win.show()
    app.exec_()

if __name__ == "__main__":
    testPreview()