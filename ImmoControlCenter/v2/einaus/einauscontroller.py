from typing import List
from PySide2.QtWidgets import QAction
from v2.einaus.einauslogic import EinAusLogic
from v2.einaus.einausview import EinAusTableView, EinAusTableViewFrame
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame

##############  EinAusController  ####################
class EinAusController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._tv: EinAusTableView = EinAusTableView()
        self._tvframe: EinAusTableViewFrame = EinAusTableViewFrame( self._tv, withEditButtons=True )
        self._logic = EinAusLogic()

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr = self.getYearToStartWith()
        tm = self._logic.getZahlungenModel( jahr )
        tv = self._tv
        tv.setModel( tm )
        tb = self._tvframe.getToolBar()
        jahre = self.getJahre()
        if len(jahre) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre , self.onYearChanged )
        tb.setYear( jahr )
        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        return self._tvframe

    def onYearChanged( self, newYear:int ):
        # tm = self._logic.getMietzahlungenModel( newYear )
        # self._tv.setModel( tm )
        pass

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        #print( "context menu for column ", index.column(), ", row ", index.row() )
        l = list()
        l.append( QAction( "Action 1" ) )
        l.append( QAction( "Action 2" ) )
        sep = QAction()
        sep.setSeparator( True )
        l.append( sep )
        l.append( QAction( "Action 3" ) )
        return l

    def onSelected( self, action: QAction ):
        print( "selected action: ", str( action ) )


#####################   TEST   TEST   TEST   ##################

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = EinAusController()
    frame = c.createGui()
    frame.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    tv = EinAusTableView()
    vf = EinAusTableViewFrame( tv, withEditButtons=True )
    vf.show()
    app.exec_()