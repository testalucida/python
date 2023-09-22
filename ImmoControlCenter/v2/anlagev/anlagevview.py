from typing import List, Iterable

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QWidget, QHBoxLayout, QTabWidget

from base.baseqtderivates import BaseGridLayout, BaseLabel, YearComboBox
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
        self._vj = 0
        self._yearCombo = YearComboBox()
        self._lblAdresse = BaseLabel()
        self._tv = AnlageVTableView()
        self._createGui()

    def _createGui( self ):
        self._layout.addWidget( self._yearCombo, 0, 0 )
        self._layout.addWidget( self._tv, 1, 0 )

    def addAndSetVeranlagungsjahre( self, vjList:Iterable[int], currentVj:int ):
        self._yearCombo.addYears( vjList )
        self._yearCombo.setYear( currentVj )

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
    from v2.anlagev.anlagevlogic import AnlageVLogic
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
        # x.divAllgHk = 1000
        # x.versicherungen = 1000
        x.hgv_netto = -2000
        x.hga = 297
        x.reisen = -260
        x.sonstige = -111
        tm = AnlageVTableModel( x )
        return tm
    app = QApplication()
    v = AnlageVView()
    v.addAndSetVeranlagungsjahre( (2023, 2022, 2021), 2022 )
    log = AnlageVLogic( 2022 )
    # tm = createModel()
    master_name = "RI_Lampennester"
    tm = log.getAnlageVTableModel( master_name )
    v.setModel( tm, master_name )
    v.setPreferredSize()
    v.show()
    app.exec_()