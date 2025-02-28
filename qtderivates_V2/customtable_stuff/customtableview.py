
from typing import List
from qt_imports import *
#####################  CellEvent  #################################
class CellEvent:
    def __init__(self, mouseX:int=-1, mouseY:int=-1, row:int=-1, column:int=-1 ):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.row = row
        self.column = column

#####################  CustomHeaderView  ####################
class CustomHeaderView( QHeaderView ):
    chvMouseMove = Signal( QMouseEvent )

    def __init__( self, orientation:Qt.Orientation=Qt.Orientation.Vertical, parent=None ):
        QHeaderView.__init__( self, orientation, parent )
        self.setMouseTracking( True )

    def mouseMoveEvent(self, evt:QMouseEvent):
        # super().mouseMoveEvent( evt )
        self.chvMouseMove.emit( evt )

#######################  CustomTableView  ##################
class CustomTableView( QTableView ):
    ctvLeftClicked = Signal( QModelIndex )
    ctvRightClicked = Signal( QPoint )
    ctvDoubleClicked = Signal( QModelIndex )
    ctvCellEnter = Signal( CellEvent )
    ctvCellLeave = Signal( CellEvent )

    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        # left mouse click
        self.clicked.connect( self.onLeftClick )
        self.pressed.connect( self.onPressed )
        self.doubleClicked.connect( self.onDoubleClick )
        # right mouse click
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.onRightClick )
        self.setMouseTracking( True )
        self._vheaderView = CustomHeaderView( Qt.Orientation.Vertical )
        self.setVerticalHeader( self._vheaderView )
        self._vheaderView.chvMouseMove.connect( self.onMouseMoveOutside )
        self._hheaderView = CustomHeaderView( Qt.Orientation.Horizontal )
        self._hheaderView.chvMouseMove.connect( self.onMouseMoveOutside )
        self._mouseOverCol = -1
        self._mouseOverRow = -1

    def setModel( self, model:QAbstractTableModel, selectRows:bool=True, singleSelection:bool=True  ) -> None:
        super().setModel( model )
        self.setSizeAdjustPolicy( QAbstractScrollArea.AdjustToContents )
        self.resizeColumnsToContents()
        self.setSelectionMode( QAbstractItemView.MultiSelection )
        if selectRows:
            self.setSelectionBehavior( QTableView.SelectRows )
        if singleSelection:
            self.setSelectionMode( QAbstractItemView.SingleSelection )

    def setSingleCellSelection( self ):
        self.setSelectionBehavior( QTableView.SelectItems )
        self.setSelectionMode( QAbstractItemView.SingleSelection )
        pass

    def setRowSelection( self ):
        self.setSelectionBehavior( QTableView.SelectRows )

    def mouseMoveEvent(self, event:QMouseEvent):
        super().mouseMoveEvent( event )
        p = event.pos()
        col = self.columnAt( p.x() )
        row = self.rowAt( p.y() )
        if row != self._mouseOverRow or col != self._mouseOverCol:
            if self._mouseOverRow > -1 and self._mouseOverCol > -1:
                self.ctvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
            if row > -1 and col > -1:
                self.ctvCellEnter.emit( CellEvent( p.x(), p.y(), row, col ) )
        self._mouseOverRow = row
        self._mouseOverCol = col

    def onMouseMoveOutside( self, event:QMouseEvent ):
        if self._mouseOverRow > -1 and self._mouseOverCol > -1:
            p = event.pos()
            self.ctvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
            self._mouseOverRow = -1
            self._mouseOverCol = -1

    def onRightClick( self, point:QPoint ):
        #selected_indexes = self.selectedIndexes()
        #print( "GenericTableView.onRightClick:", point )
        self.ctvRightClicked.emit( point )

    def onLeftClick( self, index:QModelIndex ):
        """
        Wird aufgerufen, wenn die Maustaste losgelassen wurde
        :param index:
        :return:
        """
        #print( "GenericTableView.onLeftClick: %d,%d" % ( index.row(), index.column() ) )
        self.ctvLeftClicked.emit( index )

    def onPressed( self, index:QModelIndex ):
        """
        Achtung: wenn mousePressEvent() überschrieben wird, ohne dass super().mousePressEvent aufgerufen wird,
        wird diese Methode nicht aufgerufen.
        :param index:
        :return:
        """
        pass

    def onDoubleClick( self, index:QModelIndex ):
        #print( "GenericTableView.onDoubleClick: %d,%d" % (index.row(), index.column()) )
        self.ctvDoubleClicked.emit( index )

    def getSelectedRows( self ) -> List[int]:
        sm = self.selectionModel()
        indexes:List[QModelIndex] = sm.selectedRows()  ## Achtung missverständlicher Methodenname
        l = list( indexes )
        print( indexes[0].row() )
        rows = [i.row() for i in l]
        return rows

    def getSelectedIndexes( self ) -> List[QModelIndex]:
        """
        returns an empty list if no item is selected
        :return:
        """
        return self.selectionModel().selectedIndexes()

    def getFirstSelectedRow( self ) -> int:
        rowlist = self.getSelectedRows()
        return rowlist[0] if len( rowlist ) > 0 else -1

    def getIndexFromPoint( self, point:QPoint ) -> QModelIndex:
        return self.indexAt( point )
