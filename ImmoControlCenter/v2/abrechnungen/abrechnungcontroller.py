import datehelper
from v2.abrechnungen.abrechnungenview import HGAbrechnungTableView, NKAbrechnungTableView, HGAbrechnungTableViewFrame, \
    NKAbrechnungTableViewFrame
from v2.abrechnungen.abrechnunglogic import HGAbrechnungLogic, HGAbrechnungTableModel
from v2.icc.icccontroller import IccController

################   AbrechnungenController   #####################
class AbrechnungController( IccController ):
    def __init__( self ):
        IccController.__init__( self )

################  HGAbrechnungController   ####################
class HGAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self )
        self._logic = HGAbrechnungLogic()
        self._tv = HGAbrechnungTableView()
        self._tvframe = HGAbrechnungTableViewFrame( self._tv )
        self._abrechJahr = datehelper.getCurrentYear() - 1 # Abrechnungen liegen zum laufenden Jahr nicht vor

    def createGui( self ) -> HGAbrechnungTableViewFrame:
        # todo
        tm:HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( self._abrechJahr )
        self._tv.setModel( tm )
        self._tv.setAlternatingRowColors( True )
        tb = self._tvframe.getToolBar()
        jahre = [self._abrechJahr, self._abrechJahr - 1, self._abrechJahr - 2]
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( self._abrechJahr )
        self._tvframe.editItem.connect( self.onEditAbrechnung )
        return self._tvframe

    def onYearChanged( self, newYear:int ):
        tm: HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( newYear )
        self._tv.setModel( tm )
        self._abrechJahr = newYear

    def onEditAbrechnung( self, row:int ):
        print( "onEditAbrechnung", row )

################  NKAbrechnungController   ####################
class NKAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self )
        self._tv = NKAbrechnungTableView()
        self._tvframe = NKAbrechnungTableViewFrame( self._tv )

    def createGui( self ) -> NKAbrechnungTableViewFrame:
        # todo
        return self._tvframe

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = HGAbrechnungController()
    tvf = c.createGui()
    tvf.show()
    app.exec_()
