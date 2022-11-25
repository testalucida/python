from PySide2.QtCore import Slot
from PySide2.QtWidgets import QDialog

from base.baseqtderivates import BaseEdit, FloatEdit, BaseComboBox
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from v2.icc.iccwidgets import IccTableView, IccTableViewFrame

##################   EinAusTableView   ###############
from v2.icc.interfaces import XEinAus


class EinAusTableView( IccTableView ):
    def __init__( self ):
        IccTableView.__init__( self )
        self.setAlternatingRowColors( True )

##################   EinAusTableViewFrame   ##############
class EinAusTableViewFrame( IccTableViewFrame ):
    def __init__( self, tableView:IccTableView, withEditButtons=False ):
        IccTableViewFrame.__init__( self, tableView, withEditButtons )


##################  XEinAusUI  #########################
class XEinAusUI( XBaseUI ):
    def __init__( self, x:XEinAus ):
        XBaseUI.__init__( self, x )

##################  EinAusDialog  ######################
class EinAusDialog( DynamicAttributeDialog ):
    def __init__( self, xui:XEinAusUI, title:str="Neue Zahlung anlegen" ):
        DynamicAttributeDialog.__init__( self, xui, title )


#################   TEST   TEST   TEST   TEST   #########################
def test():
    from PySide2.QtWidgets import QApplication
    def onMasterChanged( newMaster:str ):
        print( "onComboChanged ", newMaster )
        combo:BaseComboBox = dlg.getDynamicAttributeView().getWidget( "mobj_id" )
        combo.clear()
        combo.addItems( ["", "def1", "def2"] )

    app = QApplication()
    x = XEinAus()
    x.master_name = "ABC"
    x.mobj_id = "meine mobj_id"
    x.debi_kredi = "Debikredi"
    x.betrag = 111.11
    xui = XEinAusUI( x )
    vislist = (
                VisibleAttribute( "master_name", BaseComboBox, "Master: ",  nextRow=False,
                                  comboValues=["ABC", "DEF"], comboCallback=onMasterChanged),
                VisibleAttribute( "mobj_id", BaseComboBox, "Wohnung: ", comboValues=["abc1", "abc2"] ),
                VisibleAttribute( "debi_kredi", BaseEdit, "Debi/Kredi: "),
                VisibleAttribute( "betrag", FloatEdit, "Betrag: " )
              )
    xui.addVisibleAttributes( vislist )
    dlg = EinAusDialog( xui )
    if dlg.exec_() == QDialog.Accepted:
        print( "accepted" )
        dynattrview = dlg.getDynamicAttributeView()
        x = dynattrview.getXBase()
        x.print()
        xcopy = dynattrview.getModifiedXBaseCopy()
        xcopy.print()
        dynattrview.updateData()
        x = dynattrview.getXBase()
        x.print()
    else:
        print( "cancelled" )
