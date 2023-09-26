import datehelper
from base.baseqtderivates import YearComboBox
from v2.anlagev.anlagevlogic import AnlageVLogic
from v2.anlagev.anlagevtablemodel import AnlageVTableModel, XAnlageV
from v2.anlagev.anlagevview import AnlageVView, AnlageVTabs, AnlageVDialog
from v2.icc.icccontroller import IccController


class AnlageVController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._avTabs: AnlageVTabs = None
        self._vj = 0

    def createGui( self ) -> AnlageVTabs:
        jahre = AnlageVLogic.getAvailableVeranlagungsjahre()
        vj = AnlageVLogic.getDefaultVeranlagungsjahr()
        self._avTabs = AnlageVTabs( vj )
        logic = AnlageVLogic( vj )
        self._vj = vj
        tmlist = logic.getAnlageVTableModels()
        for tm in tmlist:
            v = AnlageVView()
            v.addAndSetVeranlagungsjahre( jahre, vj )
            v.setModel( tm )
            v.year_changed.connect( self.onYearChanged )
            self._avTabs.addAnlageV( v )
        self._avTabs.setPreferredSize()
        return self._avTabs

    def showAnlagenV( self ):
        self.createGui().show()

    def onYearChanged( self, master_name:str, newYear:int ):
        print( master_name, newYear )
        avview = self._avTabs.getAnlageVView( master_name )
        logic = AnlageVLogic( newYear )
        tm = logic.getAnlageVTableModel( master_name )
        avview.setModel( tm )

##################################################
def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ctrl = AnlageVController()
    avtabs = ctrl.createGui()
    #avtabs.show()
    dlg = AnlageVDialog( avtabs )
    dlg.setPreferredSize()
    dlg.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    from v2.anlagev.anlagevlogic import AnlageVLogic
    app = QApplication()
    avTabs = AnlageVTabs()
    jahre = AnlageVLogic.getAvailableVeranlagungsjahre()
    vj = AnlageVLogic.getDefaultVeranlagungsjahr()
    log = AnlageVLogic( vj )
    tmlist = log.getAnlageVTableModels()
    for tm in tmlist:
        v = AnlageVView()
        v.addAndSetVeranlagungsjahre( jahre, vj )
        v.setModel( tm )
        avTabs.addAnlageV( v )
    avTabs.setPreferredSize()
    avTabs.show()
    app.exec_()