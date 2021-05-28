from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QTabWidget, QApplication, QDialog

from anlage_v.anlagev_preview_logic import AnlageV_Preview_Logic
from anlage_v.anlagev_gui import AnlageVView, AnlageVTableView, AnlageVAuswahlDialog
from mdisubwindow import MdiSubWindow


class AnlageVController:
    def __init__( self ):
        self._master_objekte:List[str] = list()
        self._jahr:int = 0
        self._subwin:MdiSubWindow = MdiSubWindow()
        self._view:AnlageVView = AnlageVView()
        self._tabs:QTabWidget = QTabWidget()
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
            self.createSubwindow()

    def createSubwindow( self ):
        for obj in self._master_objekte:
            tm = self._busi.getAnlageVTableModel( obj, self._jahr )
            tv:AnlageVTableView = self._view.addAnlageV( tm )
            tv.cell_clicked.connect( self.onAnlageVLeftClick )
        self._subwin.setWidget( self._view )
        self._subwin.setWindowTitle( "Anlagen V ausgewählter Objekte" )
        #self._subwin.addQuitCallback( self.onCloseSubWindow )
        self._subwin.setMinimumSize( 1300, 1300 )
        self._subwin.show()

    def onAnlageVLeftClick( self, master_objekt:str, jahr:int, row:int, column:int ) -> None:
        print( "AnlageV clicked: %s, %d, %d, %d" % (master_objekt, jahr, row, column ) )

def testPreview():
    app = QApplication()
    ctrl = AnlageVController( )
    ctrl.startWork()
    # win = ctrl.createSubwindow()
    # win.show()
    app.exec_()

if __name__ == "__main__":
    testPreview()