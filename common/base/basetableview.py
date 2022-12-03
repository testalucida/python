from numbers import Number
from typing import List, Callable
from PySide2.QtCore import QAbstractTableModel, Qt, Signal, QModelIndex, QPoint
from PySide2.QtGui import QMouseEvent, QGuiApplication, QIcon
from PySide2.QtWidgets import QTableView, QAbstractItemView, QAbstractScrollArea, QHeaderView, QApplication, QMenu, \
    QAction, QComboBox

#####################  CellEvent  #################################
from base.interfaces import XBase, TestItem
from base.basetablemodel import BaseTableModel


class CellEvent:
    def __init__(self, mouseX:int=-1, mouseY:int=-1, row:int=-1, column:int=-1 ):
        self.mouseX = mouseX
        self.mouseY = mouseY
        self.row = row
        self.column = column

#####################  BaseHeaderView  ####################
class BaseHeaderView( QHeaderView ):
    bhvMouseMove = Signal( QMouseEvent )

    def __init__( self, orientation:Qt.Orientation=Qt.Orientation.Vertical, parent=None ):
        QHeaderView.__init__( self, orientation, parent )
        self.setMouseTracking( True )

    def mouseMoveEvent(self, evt:QMouseEvent):
        self.bhvMouseMove.emit( evt )

#####################  BaseTableView  ####################
class BaseTableView( QTableView ):
    """
    Eine TableView, die eine Liste von XBase-Objekten anzeigt.
    Wird mit der linken Maus in eine Zelle geklickt, wird ein btvLeftClicked-Signal gesendet.
    Wird mit der rechten Maus geklickt (Kontextmenü soll geöffnet werden), werden über eine Callback-Function
    die anzuzeigenden QActions geholt und angezeigt. Die ausgewählte Action wird über eine andere
    Callback-Function zurückgeliefert.
    Die Callback-Functions werden mit setContextMenuCallbacks() angemeldet.
    """
    btvLeftClicked = Signal( QModelIndex )
    btvRightClicked = Signal( QPoint )
    btvDoubleClicked = Signal( QModelIndex )
    # btvCellEnter = Signal( CellEvent )
    # btvCellLeave = Signal( CellEvent )

    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        # left mouse click
        self.clicked.connect( self.onLeftClick )
        self.doubleClicked.connect( self.onDoubleClick )
        # right mouse click
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.onRightClick )
        self.setMouseTracking( True )
        #self.horizontalHeader().sortIndicatorChanged.connect( self.afterSort )
        # self.btvCellEnter.connect( self._onCellEnter )
        # self.btvCellLeave.connect( self._onCellLeave )
        self._vheaderView = BaseHeaderView( Qt.Orientation.Vertical )
        self.setVerticalHeader( self._vheaderView )
        self._vheaderView.bhvMouseMove.connect( self.onMouseMoveOutside )
        # self._hheaderView = BaseHeaderView( Qt.Orientation.Horizontal )
        # self._hheaderView.bhvMouseMove.connect( self.onMouseMoveOutside )
        #self.setHorizontalHeader( self._hheaderView )  # mit dem CustomHeaderView funktioniert das Sortieren nicht
        self._mouseOverCol = -1
        self._mouseOverRow = -1
        # callback mit der Signatur indexrow:int, indexcolumn:int, point:QPoint.
        # Liefert die QAction-Objekte zurück, die im Kontextmenü angezeigt werden sollen.
        self._contextMenuActionsProvider:Callable = None
        self._contextMenuActionActor:Callable = None
        self.showSortIndicator( False )

    def showSortIndicator( self, show=True ):
        model:BaseTableModel = self.model()
        if model:
            self.horizontalHeader().setSortIndicator( model.getSortColumn(), model.getSortOrder() )
        self.horizontalHeader().setSortIndicatorShown( show )

    def setContextMenuCallbacks( self, provider:Callable, onSelected:Callable ) -> None:
        """
        Registriert zwei callback-functions:
        Die eine, provider, wird von BaseTableView nach einem rechten Mausklick mit relevanten Paramtern
         (siehe param provider) aufgerufen.
        Dieser callback muss eine Liste von QActions zurückgeben, die dann im Kontextmenü angezeigt werden.
        Die andere, onSelected (siehe param onSelected), wird von BaseTableView nach Auswahl
        eines Kontextmenüpunktes aufgerufen.
        :param provider: callback function, die folgende Argumente akzeptieren muss:
                index:QModelIndex, point:QPoint, selectedIndexes
                Zurückgeben muss sie eine List[QAction] oder None
        :param onSelected: callback function, die folgende Argumente akzeptieren muss:
                action:QAction
        :return: None
        """
        self._contextMenuActionsProvider = provider
        self._contextMenuActionActor = onSelected

    def setModel( self, model:BaseTableModel,
                  selectRows:bool=True, singleSelection:bool=True, sortable:bool=True  ) -> None:
        super().setModel( model )
        self.resizeRowsAndColumns()
        # self.setSizeAdjustPolicy( QAbstractScrollArea.AdjustToContents )
        # self.resizeColumnsToContents()
        self.resizeRowsToContents()
        if selectRows:
            self.setSelectionBehavior( QTableView.SelectRows )
        else:
            self.setSelectionBehavior( QTableView.SelectItems )
        if singleSelection:
            self.setSelectionMode( QAbstractItemView.SingleSelection )
        else:
            self.setSelectionMode( QTableView.SelectionMode.ContiguousSelection )
        self.setSortingEnabled( True ) # Sortieren soll grundsätzlich möglich sein...
        self.showSortIndicator( False ) # ...aber wir wollen noch keinen Sort-Indicator sehen, weil noch nicht sortiert ist.
        model.layoutChanged.emit()
        model.setSortable( sortable )
        model.sorting_finished.connect( self.showSortIndicator )
        #model.layoutChanged.connect( self.resizeRowsAndColumns )   FUNKTIONIERT NICHT - ROWS BEHALTEN IHRE HÖHE BEI
        model.rowsAddedSignal.connect( self.onRowsAdded )

    def onRowsAdded( self ):
        self.resizeRowsToContents()

    def resizeRowsAndColumns( self ):
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    def mouseMoveEvent(self, event:QMouseEvent):
        super().mouseMoveEvent( event )
        # p = event.pos()
        # col = self.columnAt( p.x() )
        # row = self.rowAt( p.y() )
        # if row != self._mouseOverRow or col != self._mouseOverCol:
        #     if self._mouseOverRow > -1 and self._mouseOverCol > -1:
        #         self.btvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
        #     if row > -1 and col > -1:
        #         self.btvCellEnter.emit( CellEvent( p.x(), p.y(), row, col ) )
        # self._mouseOverRow = row
        # self._mouseOverCol = col
        #print( "x = %d, y=%d, row = %d, col = %d" % ( p.x(), p.y(), row, col ) )

    # def _onCellEnter( self, evt:CellEvent ):
    #     print( "onCellEnter: %d, %d" % (evt.row, evt.column ) )

    # def _onCellLeave( self, evt: CellEvent ):
    #     print( "onCellLeave: %d, %d" % (evt.row, evt.column) )

    def onMouseMoveOutside( self, event:QMouseEvent ):
        if self._mouseOverRow > -1 and self._mouseOverCol > -1:
            p = event.pos()
            self.btvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
            self._mouseOverRow = -1
            self._mouseOverCol = -1

    def onRightClick( self, point:QPoint ):
        #selected_indexes = self.selectedIndexes()
        #print( "BaseTableView.onRightClick:", point )
        if self._contextMenuActionsProvider:
            index = self.indexAt( point )
            if index.isValid():
                selectedIndexes = self.selectedIndexes()
                actions = self._contextMenuActionsProvider( index, point, selectedIndexes )
                if actions and len( actions ) > 0:
                    menu = QMenu()
                    for action in actions:
                        menu.addAction( action )
                    selectedAction = menu.exec_( self.viewport().mapToGlobal( point ) )
                    if selectedAction:
                        self._contextMenuActionActor( selectedAction )

    def onLeftClick( self, index:QModelIndex ):
        # wird aufgerufen, wenn die Maustaste losgelassen wird
        #print( "BaseTableView.onLeftClick: %d,%d" % ( index.row(), index.column() ) )
        self.btvLeftClicked.emit( index )

    def onDoubleClick( self, index:QModelIndex ):
        #print( "GenericTableView.onDoubleClick: %d,%d" % (index.row(), index.column()) )
        self.btvDoubleClicked.emit( index )

    def getPreferredHeight( self ) -> int:
        rowcount = self.model().rowCount()
        h = self._toolbar.height()
        for row in range( 0, rowcount ):
            h += self.rowHeight( row )
        return h + 25

    def getPreferredWidth( self ) -> int:
        colcount = self.model().columnCount()
        w = 0
        for col in range( 0, colcount ):
            w += self.columnWidth( col )
        return w + 25

    def getSelectedRows( self ) -> List[int]:
        sm = self.selectionModel()
        indexes:List[QModelIndex] = sm.selectedRows()  ## Achtung missverständlicher Methodenname
        l = list( indexes )
        #print( indexes[0].row() )
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

    def copySelectionToClipboard( self ) -> None:
        values: str = ""
        indexes = self.selectedIndexes()
        row = -1
        for idx in indexes:
            if row == -1: row = idx.row()
            if row != idx.row():
                values += "\n"
                row = idx.row()
            elif len( values ) > 0:
                values += "\t"
            val = self.model().data( idx, Qt.DisplayRole )
            val = "" if not val else val
            if isinstance( val, Number ):
                values += str( val )
            else:
                values += val
        clipboard = QGuiApplication.clipboard()
        clipboard.setText( values )

####################################################  T  E  S  T  S  #################################################

def makeTestModel() -> BaseTableModel:
    nachnamen = ("Kendel", "Knabe", "Verhoeven", "Adler", "Strack-Zimmermann")
    vornamen = ("Martin", "Gudrun", "Paul", "Henriette", "Marie-Agnes")
    plzn = ("91077", "91077", "77654", "88954", "66538")
    orte = ("Kleinsendelbach", "Kleinsendelbach", "Niederstetten", "Oberhimpflhausen", "Neunkirchen")
    strn = ("Birnenweg 2", "Birnenweg 2", "Rebenweg 3", "Hubertusweg 22", "Wellesweilerstr. 56")
    alter = ( 67, 65, 54, 49, 60)
    groessen = (180, 170, 179, 185, 161.5)
    itemlist = list()
    for n in range( 0, len(nachnamen) ):
        i = TestItem()
        i.nachname = nachnamen[n]
        i.vorname = vornamen[n]
        i.plz = plzn[n]
        i.ort = orte[n]
        i.str = strn[n]
        i.alter = alter[n]
        i.groesse = groessen[n]
        itemlist.append( i )
    tm = BaseTableModel( itemlist )
    return tm


def actor( action:QAction ):
    print( "selected action: ", str( action ) )

def provideActions( index, point, selectedIndexes ) -> List[QAction]:
    print( "context menu for column ", index.column(), ", row ", index.row() )
    l = list()
    l.append( QAction( "Action 1" ) )
    l.append( QAction( "Action 2" ) )
    sep = QAction()
    sep.setSeparator( True )
    l.append( sep )
    l.append( QAction( "Action 3" ) )
    return l

def prepareTableView() -> BaseTableView:
    tm = makeTestModel()
    tv = BaseTableView()
    tv.setContextMenuCallbacks( provideActions, actor )
    tv.setModel( tm, selectRows=True, singleSelection=False )
    return tv

def test():
    app = QApplication()
    tv = prepareTableView()
    tv.show()
    #tv.setProperty( 'hideSortIndicatorColumn', 1 )
    tv.horizontalHeader().setSortIndicatorShown( False )
    #tv.setSortingEnabled( True )
    app.exec_()
