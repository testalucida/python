from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget, QHBoxLayout, QTabWidget

from base.baseqtderivates import BaseGridLayout, BaseLabel
from base.basetableview import BaseTableView
from v2.anlagev.anlagevtablemodel import AnlageVTableModel, XAnlageV


class AnlageVTableView( BaseTableView ):
    def __init__( self ):
        BaseTableView.__init__( self )
        #self.horizontalHeader().hide()

    def setModel( self, tm:AnlageVTableModel ):
        super().setModel( tm, selectRows=True, singleSelection=False )
        # for r in range( 0, tm.rowCount() ):
        #     self.setRowHeight( r, 25 )

################################################
class AnlageVView( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._lblAdresse = BaseLabel()
        self._tv = AnlageVTableView()
        self._createGui()

    def _createGui( self ):
        self._layout.addWidget( self._tv )

    def setModel( self, tm:AnlageVTableModel, title:str ):
        self._tv.setModel( tm )
        self.setWindowTitle( title )

    def setPreferredSize( self ):
        w = self._tv.getPreferredWidth()
        h = self._tv.getPreferredHeight() + 25
        self.resize( QSize(w,h) )

#################################################
class AnlagenVTabs( QTabWidget ):
    def __init__( self ):
        QTabWidget.__init__( self )

    def addAnlageV( self, view:AnlageVView ):
        self.addTab( view, view.windowTitle() )

##################################################
def test():
    from PySide2.QtWidgets import QApplication
    def createModel() -> AnlageVTableModel:
        x = XAnlageV()
        x.vj = 2022
        x.bruttoMiete = 4904
        x.nettoMiete = 3100
        x.nkv = 1804
        x.nka = -104
        x.afa = -786
        x.erhaltg_voll = -1234
        x.verteil_aufwand_im_vj_angefallen = -6000
        x.erhaltg_anteil_vj = -2000
        x.erhaltg_anteil_vjminus1 = -3344
        x.entnahme_rue = -5000
        x.grundsteuer = -234
        x.hgv_netto = -2000
        x.hga = 297
        x.reisen = -260
        x.sonstige = -111
        tm = AnlageVTableModel( x )
        return tm
    app = QApplication()
    tm = createModel()
    v = AnlageVView()
    v.setModel( tm, "N-Mendel7" )
    v.setPreferredSize()
    v.show()
    app.exec_()