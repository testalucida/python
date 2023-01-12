from PySide2.QtCore import QSize
from PySide2.QtWidgets import QMenu

import datehelper
from base.dynamicattributeui import DynamicAttributeDialog
from v2.abrechnungen.abrechnungdialogcontroller import AbrechnungDialogController
from v2.abrechnungen.abrechnungenview import HGAbrechnungTableView, NKAbrechnungTableView, HGAbrechnungTableViewFrame, \
    NKAbrechnungTableViewFrame, AbrechnungTableViewFrame, AbrechnungTableView
from v2.abrechnungen.abrechnunglogic import HGAbrechnungLogic, HGAbrechnungTableModel, AbrechnungTableModel, \
    AbrechnungLogic, NKAbrechnungLogic
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XAbrechnung

################   AbrechnungenController   ####################

class AbrechnungController( IccController ):
    def __init__( self, logic:AbrechnungLogic ):
        IccController.__init__( self )
        self.abrechJahr = datehelper.getCurrentYear() - 1 # Abrechnungen liegen zum laufenden Jahr nicht vor
        self.tv:AbrechnungTableView = None
        self.tvframe:AbrechnungTableViewFrame = None
        self.logic = logic

    def createGui( self ) -> HGAbrechnungTableViewFrame:
        tm: AbrechnungTableModel = self.logic.getAbrechnungTableModel( self.abrechJahr )
        self.tv.setModel( tm )
        self.tv.setAlternatingRowColors( True )
        tb = self.tvframe.getToolBar()
        jahre = [self.abrechJahr, self.abrechJahr - 1, self.abrechJahr - 2]
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( self.abrechJahr )
        self.tvframe.editItem.connect( self.onOpenAbrechnungDialog )
        return self.tvframe

    def getMenu( self ) -> QMenu or None:
        pass

    def onOpenAbrechnungDialog( self, row: int ):
        """
        In der Tabelle der Abrechnungen wurde eine Zeile ausgewählt und der Edit-Button der TableView gedrückt.
        Die Verarbeitung wird an den AbrechnungDialogController übergeben.
        :param row: in der Tabelle markierte Abrechnung (Zeile)
        :return:
        """
        model: AbrechnungTableModel = self.tv.model()
        x: XAbrechnung = model.getElement( row )
        if not x.ab_jahr:
            # neue Abrechnung, existiert noch nicht in der DB
            x.ab_jahr = self.abrechJahr
        abrdlgctrl = AbrechnungDialogController( x, self.logic )
        abrdlgctrl.processAbrechnung()

    def onYearChanged( self, newYear: int ):
        tm: AbrechnungTableModel = self.logic.getAbrechnungTableModel( newYear )
        self.tv.setModel( tm )
        self.abrechJahr = newYear

################  HGAbrechnungController   ####################
class HGAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self, HGAbrechnungLogic() )
        self.tv = HGAbrechnungTableView()
        self.tvframe = HGAbrechnungTableViewFrame( self.tv )

################  NKAbrechnungController   ####################
class NKAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self, NKAbrechnungLogic() )
        self.tv = NKAbrechnungTableView()
        self.tvframe = NKAbrechnungTableViewFrame( self.tv )


########################   TEST  TEST  TEST  TEST  TEST  ######################

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = NKAbrechnungController()
    tvf = c.createGui()
    tvf.show()
    tvf.resize( QSize(1600, 200) )
    app.exec_()
