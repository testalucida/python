from abc import abstractmethod
from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog

import datehelper
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccTableViewFrame, IccCheckTableViewFrame
from v2.mtleinaus.mtleinauslogic import MieteLogic, MtlEinAusTableModel
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, ValueDialog


#############  MtlEinAusController  #####################
class MtlEinAusController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        dic = datehelper.getCurrentYearAndMonth()
        self._year = dic["year"]
        self._month = dic["month"] - 1

    @abstractmethod
    def createGui( self ) -> IccCheckTableViewFrame:
        pass

    @abstractmethod
    def getTableViewFrame( self ) -> IccTableViewFrame:
        pass

    @abstractmethod
    def getModel( self ) -> MtlEinAusTableModel:
        pass

    @abstractmethod
    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        pass

    @abstractmethod
    def onSelected( self, action: QAction ):
        pass

    @abstractmethod
    def onYearChanged( self, newYear: int ):
        pass

    @abstractmethod
    def onMonthChanged( self, newMonthIdx: int, newMonthLongName: str ):
        pass

    def getCurrentYearAndMonth( self ):
        return self._year, self._month

    def onBetragOk( self, index:QModelIndex ):
        model:MtlEinAusTableModel = self.getModel()
        row = index.row()
        sollVal = model.getSollValue( row )
        editColIdx = model.getEditableColumnIdx()
        model.setValue( row, editColIdx, sollVal )

    def onBetragEdit( self, index: QModelIndex ):
        def editing_done( val:float, op:str ):
            model = self.getModel()
            editColIdx = model.getEditableColumnIdx()
            oldval = self.getModel().getValue( index.row(), editColIdx )
            if op == "add":
                oldval += val
            elif op == "sub":
                oldval -= val
            elif op == "replace":
                oldval = val
            model.setValue( index.row(), editColIdx, oldval )

        dlg = ValueDialog()
        crsr = QCursor.pos()
        dlg.setCallback( editing_done )
        dlg.move( crsr.x(), crsr.y() )
        dlg.exec_()


##############  MieteController  ####################
class MieteController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self )
        self._tv: MieteTableView = MieteTableView()
        self._tvframe: MieteTableViewFrame = MieteTableViewFrame( self._tv )
        self._logic:MieteLogic = MieteLogic.inst()

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr, monat = self.getCurrentYearAndMonth()
        tm = self._logic.getMietzahlungenModel( jahr, monat )
        tv = self._tv
        tv.setModel( tm )
        tb = self._tvframe.getToolBar()
        tb.addYearCombo( (self._logic.getJahre()) , self.onYearChanged )
        tb.setYear( jahr )
        tb.addMonthCombo( self.onMonthChanged )
        tb.setMonthIdx( monat )

        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        tv.okClicked.connect( self.onBetragOk )
        tv.nokClicked.connect( self.onBetragEdit )
        return self._tvframe

    def getTableViewFrame( self ) -> IccTableViewFrame:
        return self._tvframe

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        print( "context menu for column ", index.column(), ", row ", index.row() )
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

    def onYearChanged( self, newYear:int ):
        tm = self._logic.getMietzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
        model: MtlEinAusTableModel = self.getModel()
        model.setEditableMonth( newMonthIdx )

