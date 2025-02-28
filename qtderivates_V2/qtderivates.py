import numbers
import os
from typing import Any, List, Tuple

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QDate, Qt, QAbstractTableModel, Signal, QPoint, QModelIndex
from PySide2.QtGui import QDoubleValidator, QIntValidator, QFont, QGuiApplication, QStandardItemModel, QStandardItem, \
    QMouseEvent, QTextDocument
from PySide2.QtWidgets import QDialog, QCalendarWidget, QVBoxLayout, QBoxLayout, QLineEdit, QGridLayout, QPushButton, \
    QHBoxLayout, QApplication, QListView, QLabel, QTextEdit, QCheckBox, QTableView, QWidget, \
    QAbstractItemView, QAction, QMenu

from datehelper import isValidIsoDatestring, isValidEurDatestring, getRelativeQDate, getQDateFromIsoString
from iconfactory import IconFactory


#####################  Cell  #################################
# class CellEvent:
#     def __init__(self, mouseX:int=-1, mouseY:int=-1, row:int=-1, column:int=-1 ):
#         self.mouseX = mouseX
#         self.mouseY = mouseY
#         self.row = row
#         self.column = column
#
# #####################  CustomHeaderView  ####################
# class CustomHeaderView( QHeaderView ):
#     chvMouseMove = Signal( QMouseEvent )
#
#     def __init__( self, orientation:Qt.Orientation=Qt.Orientation.Vertical, parent=None ):
#         QHeaderView.__init__( self, orientation, parent )
#         self.setMouseTracking( True )
#
#     def mouseMoveEvent(self, evt:QMouseEvent):
#         # super().mouseMoveEvent( evt )
#         self.chvMouseMove.emit( evt )
#
# ######################  CustomTableView ##################################
# class CustomTableView( QTableView ):
#     ctvLeftClicked = Signal( QModelIndex )
#     ctvRightClicked = Signal( QPoint )
#     ctvDoubleClicked = Signal( QModelIndex )
#     ctvCellEnter = Signal( CellEvent )
#     ctvCellLeave = Signal( CellEvent )
#
#     def __init__( self, parent=None ):
#         QTableView.__init__( self, parent )
#         # left mouse click
#         self.clicked.connect( self.onLeftClick )
#         self.doubleClicked.connect( self.onDoubleClick )
#         # right mouse click
#         self.setContextMenuPolicy( Qt.CustomContextMenu )
#         self.customContextMenuRequested.connect( self.onRightClick )
#         self.setMouseTracking( True )
#         # self.ctvCellEnter.connect( self._onCellEnter )
#         # self.ctvCellLeave.connect( self._onCellLeave )
#         self._vheaderView = CustomHeaderView( Qt.Orientation.Vertical )
#         self.setVerticalHeader( self._vheaderView )
#         self._vheaderView.chvMouseMove.connect( self.onMouseMoveOutside )
#         self._hheaderView = CustomHeaderView( Qt.Orientation.Horizontal )
#         self._hheaderView.chvMouseMove.connect( self.onMouseMoveOutside )
#         #self.setHorizontalHeader( self._hheaderView )  # mit dem CustomHeaderView funktioniert das Sortieren nicht
#         self._mouseOverCol = -1
#         self._mouseOverRow = -1
#
#     def setModel( self, model:QAbstractTableModel, selectRows:bool=True, singleSelection:bool=True  ) -> None:
#         super().setModel( model )
#         self.setSizeAdjustPolicy( QAbstractScrollArea.AdjustToContents )
#         self.resizeColumnsToContents()
#         if selectRows:
#             self.setSelectionBehavior( QTableView.SelectRows )
#         if singleSelection:
#             self.setSelectionMode( QAbstractItemView.SingleSelection )
#
#     def mouseMoveEvent(self, event:QMouseEvent):
#         p = event.pos()
#         col = self.columnAt( p.x() )
#         row = self.rowAt( p.y() )
#         if row != self._mouseOverRow or col != self._mouseOverCol:
#             if self._mouseOverRow > -1 and self._mouseOverCol > -1:
#                 self.ctvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
#             if row > -1 and col > -1:
#                 self.ctvCellEnter.emit( CellEvent( p.x(), p.y(), row, col ) )
#         self._mouseOverRow = row
#         self._mouseOverCol = col
#         #print( "x = %d, y=%d, row = %d, col = %d" % ( p.x(), p.y(), row, col ) )
#
#     # def _onCellEnter( self, evt:CellEvent ):
#     #     print( "onCellEnter: %d, %d" % (evt.row, evt.column ) )
#
#     # def _onCellLeave( self, evt: CellEvent ):
#     #     print( "onCellLeave: %d, %d" % (evt.row, evt.column) )
#
#     def onMouseMoveOutside( self, event:QMouseEvent ):
#         if self._mouseOverRow > -1 and self._mouseOverCol > -1:
#             p = event.pos()
#             self.ctvCellLeave.emit( CellEvent( p.x(), p.y(), self._mouseOverRow, self._mouseOverCol ) )
#             self._mouseOverRow = -1
#             self._mouseOverCol = -1
#
#     def onRightClick( self, point:QPoint ):
#         #selected_indexes = self.selectedIndexes()
#         #print( "GenericTableView.onRightClick:", point )
#         self.ctvRightClicked.emit( point )
#
#     def onLeftClick( self, index:QModelIndex ):
#         #print( "GenericTableView.onLeftClick: %d,%d" % ( index.row(), index.column() ) )
#         self.ctvLeftClicked.emit( index )
#
#     def onDoubleClick( self, index:QModelIndex ):
#         #print( "GenericTableView.onDoubleClick: %d,%d" % (index.row(), index.column()) )
#         self.ctvDoubleClicked.emit( index )
#
#     def getSelectedRows( self ) -> List[int]:
#         sm = self.selectionModel()
#         indexes:List[QModelIndex] = sm.selectedRows()  ## Achtung missverständlicher Methodenname
#         l = list( indexes )
#         #print( indexes[0].row() )
#         rows = [i.row() for i in l]
#         return rows
#
#     def getSelectedIndexes( self ) -> List[QModelIndex]:
#         """
#         returns an empty list if no item is selected
#         :return:
#         """
#         selmodel = self.selectionModel()
#         if selmodel:
#             return selmodel.selectedIndexes()
#         return list()
#
#     def getFirstSelectedRow( self ) -> int:
#         rowlist = self.getSelectedRows()
#         return rowlist[0] if len( rowlist ) > 0 else -1

#####################  TableViewContextMenuHandler  #########
# class TableViewContextMenuHandler:
#     def __init__( self, tv: CustomTableView ):
#         tv.setMouseTracking( True )
#         tv.setContextMenuPolicy( Qt.CustomContextMenu )
#         tv.customContextMenuRequested.connect( self.onRightClick )
#         #tv.setCopyCallback( self._onCopy )  # wenn der User Ctrl+c drückt
#         self._tv = tv
#         self._actionList:List[List] = list() #Liste, die eine Liste mit Paaren action / callback enthält.
#         self._actionList.append( ( QAction( "Kopiere" ), self._onCopy) ) # für Kontextmenü
#
#     def addAction( self, action:QAction, callback ):
#         self._actionList.append( ( action, callback ) )
#
#     def onRightClick( self, point: QPoint ):
#         index = self._tv.indexAt( point )
#         row = index.row()
#         if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
#         selectedIndexes = self._tv.selectedIndexes()
#         if selectedIndexes is None or len( selectedIndexes ) < 1: return
#         menu = QMenu( self._tv )
#         for pair in self._actionList:
#             menu.addAction( pair[0] )
#         action = menu.exec_( self._tv.viewport().mapToGlobal( point ) )
#         if action:
#             sel = [pair[1] for pair in self._actionList if pair[0] == action]
#             sel[0]( action, point )
#
#     def _onCopy( self, action:QAction, point:QPoint ):
#         values:str = ""
#         indexes = self._tv.selectedIndexes()
#         row = -1
#         for idx in indexes:
#             if row == -1: row = idx.row()
#             if row != idx.row():
#                 values += "\n"
#                 row = idx.row()
#             elif len( values ) > 0:
#                 values += "\t"
#             val = self._tv.model().data( idx, Qt.DisplayRole )
#             val = "" if not val else val
#             if isinstance( val, numbers.Number ):
#                 values += str( val )
#             else:
#                 values += val
#             #print( idx.row(), "/", idx.column(), ": ", val )
#         #print( "valuestring: ",  values )
#         clipboard = QGuiApplication.clipboard()
#         clipboard.setText( values )
#
# ###################  EditableTableViewWidget  #########################
# class EditableTableViewWidget( QWidget ):
#     createItem = Signal()
#     editItem = Signal( QModelIndex )
#     deleteItem = Signal( QModelIndex )
#
#     def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
#         QWidget.__init__( self, parent )
#         self._isEditable = isEditable
#         self._layout = QGridLayout()
#         if isEditable:
#             self._newButton = QPushButton()
#             icon = ImageFactory.inst().getPlusIcon()
#             self._newButton.setIcon( icon )
#             self._newButton.setToolTip( "Neuen Tabelleneintrag anlegen" )
#
#             self._editButton = QPushButton()
#             icon = ImageFactory.inst().getEditIcon()
#             self._editButton.setIcon( icon )
#             self._editButton.setToolTip( "Ausgewählten Tabelleneintrag bearbeiten" )
#
#             self._deleteButton = QPushButton()
#             icon = ImageFactory.inst().getDeleteIcon()
#             self._deleteButton.setIcon( icon )
#             self._deleteButton.setToolTip( "Ausgewählten Tabelleneintrag löschen" )
#
#         self._tv = CustomTableView()
#         self._createGui()
#         if model:
#             self.setTableModel( model )
#
#     def _createGui( self ):
#         if self._isEditable:
#             self._createEditButtons()
#
#         self._tv.horizontalHeader().setStretchLastSection( True )
#         self._layout.addWidget( self._tv, 1, 0)
#         self.setLayout( self._layout )
#
#     def _createEditButtons( self ):
#         self._newButton.clicked.connect( self._onNew )
#         self._editButton.clicked.connect( self._onEdit )
#         self._deleteButton.clicked.connect( self._onDelete )
#         hbox = QHBoxLayout()
#         hbox.addWidget( self._newButton )
#         hbox.addWidget( self._editButton )
#         hbox.addWidget( self._deleteButton )
#         self._layout.addLayout( hbox, 2, 0, alignment=Qt.AlignLeft )
#
#     def setTableModel( self, model:QAbstractTableModel,  selectRows:bool=True, singleSelection:bool=True  ):
#         self._tv.setModel( model, selectRows, singleSelection )
#         if self._isEditable:
#             self._newButton.setFocus()
#
#     def getModel( self ):
#         return self._tv.model()
#
#     def getTableView( self ) -> CustomTableView:
#         return self._tv
#
#     def _onNew( self ):
#         self.createItem.emit()
#
#     def _onEdit( self ):
#         indexlist = self.getSelectedIndexes()
#         if len( indexlist ) == 0:
#             raise Exception( "GenericTableViewDialog: no item selected to edit" )
#         self.editItem.emit( indexlist[0] )
#
#     def _onDelete( self ):
#         indexlist = self.getSelectedIndexes()
#         if len( indexlist ) == 0:
#             raise Exception( "GenericTableViewDialog: no item selected to delete" )
#         self.deleteItem.emit( indexlist[0] )
#
#     def getSelectedIndexes( self ) -> List[QModelIndex]:
#         """
#         returns an empty list if no item is selected
#         :return:
#         """
#         sm = self._tv.selectionModel()
#         if sm:
#             return sm.selectedIndexes()
#         return list()
#
#     def getSelectedRows( self ) -> List[int]:
#         indexes = self.getSelectedIndexes()
#         l = list()
#         for i in indexes:
#             l.append( i.row() )
#         return l
#
#     def getFirstSelectedRow( self ) -> int:
#         rowlist = self.getSelectedRows()
#         return rowlist[0] if len( rowlist ) > 0 else -1

###################  GenericTableViewDialog  ##############################
# class CustomTableViewDialog( QDialog ):
#     """
#     Dialog für eine CustomTableView.
#     Wenn die TableView editierbar sein soll (isEditable=True), werden unterhalb der View
#     3 Buttons zur Neunanlage, Bearbeitung bzw. Löschung einer Tabellenzeile angeboten.
#     Bei Drücken von OK oder Cancel wird ein entsprechendes Signal gesendet.
#     Die Methoden accept() und reject() müssen nach der Signalbehandlung explizit aufgerufen werden.
#     """
#     createItem = Signal()
#     editItem = Signal( QModelIndex )
#     deleteItem = Signal( QModelIndex )
#     okPressed = Signal()
#     cancelPressed = Signal()
#
#     def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
#         QDialog.__init__( self, parent )
#         self._isEditable = isEditable
#         self._layout = QGridLayout( self )
#         #self._imagePath =
#         self._okButton = QPushButton( "OK" )
#         self._cancelButton = QPushButton( "Abbrechen" )
#         if isEditable:
#             #path = ROOT_DIR
#             iconpath = os.getcwd() + "/images/"
#             iconfactory = IconFactory()
#             self._newButton = QPushButton()
#             icon = iconfactory.getIcon( iconpath + "plus_30x30.png" )
#             self._newButton.setIcon( icon )
#             self._newButton.setToolTip( "Neuen Tabelleneintrag anlegen" )
#
#             self._editButton = QPushButton()
#             icon = iconfactory.getIcon( iconpath + "edit.png" )
#             self._editButton.setIcon( icon )
#             self._editButton.setToolTip( "Ausgewählten Tabelleneintrag bearbeiten" )
#
#             self._deleteButton = QPushButton()
#             icon = iconfactory.getIcon( iconpath + "cancel.png" )
#             self._deleteButton.setIcon( icon )
#             self._deleteButton.setToolTip( "Ausgewählten Tabelleneintrag löschen" )
#
#         self._tv = CustomTableView( self )
#         self._createGui()
#         self.setModal( True )
#         if model:
#             self.setTableModel( model )
#
#     def _createGui( self ):
#         if self._isEditable:
#             self._createEditButtons()
#         self._okButton.clicked.connect( self.okPressed.emit )
#         self._cancelButton.clicked.connect( self.cancelPressed.emit )
#         hbox = QHBoxLayout()
#         hbox.addWidget( self._okButton )
#         hbox.addWidget( self._cancelButton )
#
#         self._tv.horizontalHeader().setStretchLastSection( True )
#         self._layout.addWidget( self._tv, 1, 0)
#         self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft )
#         self.setLayout( self._layout )
#
#     def _createEditButtons( self ):
#         self._newButton.clicked.connect( self._onNew )
#         self._editButton.clicked.connect( self._onEdit )
#         self._deleteButton.clicked.connect( self._onDelete )
#         hbox = QHBoxLayout()
#         hbox.addWidget( self._newButton )
#         hbox.addWidget( self._editButton )
#         hbox.addWidget( self._deleteButton )
#         self._layout.addLayout( hbox, 2, 0, alignment=Qt.AlignLeft )
#
#     def setCancelButtonVisible( self, visible:bool=True ):
#         self._cancelButton.setVisible( False )
#
#     def setOkButtonText( self, text:str ):
#         self._okButton.setText( text )
#
#     def setTableModel( self, model:QAbstractTableModel, selectRows:bool=True, singleSelection:bool=True ):
#         self._tv.setModel( model )
#         # self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
#         # self._tv.resizeColumnsToContents()
#         self._tv.setSelectionBehavior( QTableView.SelectRows )
#         self._tv.setSelectionMode( QAbstractItemView.SingleSelection )
#         if self._isEditable:
#             self._newButton.setFocus()
#         else:
#             self._okButton.setFocus()
#
#     def _onNew( self ):
#         self.createItem.emit()
#
#     def _onEdit( self ):
#         indexlist = self._tv.getSelectedIndexes()
#         if len( indexlist ) > 0:
#             self.editItem.emit( indexlist[0] )
#
#     def _onDelete( self ):
#         indexlist = self._tv.getSelectedIndexes()
#         if len( indexlist ) > 0:
#             self.deleteItem.emit( indexlist[0] )
#
#     def getTableView( self ) -> CustomTableView:
#         return self._tv

####################  ZoomView  #######################################
class ZoomView( QDialog ):
    def __init__( self, text:str, parent=None ):
        QDialog.__init__( self, parent )
        self.setWindowFlags( Qt.FramelessWindowHint )
        self.layout = QHBoxLayout()
        self.zoom = QTextEdit()
        self.layout.addWidget( self.zoom )
        self.setLayout( self.layout )
        self.zoom.setText( text )

# ######################  CalendarDialog ##################################
# class CalendarDialog( QDialog ):
#     def __init__( self, parent ):
#         QDialog.__init__(self, parent)
#         self.setModal( True )
#         self.setTitle( "Datum auswählen" )
#         self._calendar:QCalendarWidget = None
#         self._buchungsjahrChangedCallback = None
#
#         self._buttonBox:QtWidgets.QDialogButtonBox = None
#         self._callback = None
#         self.createCalendar()
#
#     def setTitle( self, title:str ) -> None:
#         self.setWindowTitle( title )
#
#     def setCallback( self, cbfnc ):
#         self._callback = cbfnc
#
#     def setMinimumDate( self, y:int, m:int, d:int ):
#         self._calendar.setMinimumDate( QDate( y, m, d ) )
#
#     def setMaximumDate( self, y:int, m:int, d:int ):
#         self._calendar.setMaximumDate( QDate( y, m, d ) )
#
#     def createCalendar(self):
#         vbox = QVBoxLayout()
#         self._calendar = QCalendarWidget()
#         self._calendar.setGridVisible( True )
#         self._calendar.setFirstDayOfWeek( Qt.Monday )
#         vbox.addWidget( self._calendar )
#         self.setLayout(vbox)
#
#         self._buttonBox = QtWidgets.QDialogButtonBox( self )
#         self._buttonBox.setOrientation( QtCore.Qt.Horizontal )
#         self._buttonBox.setStandardButtons( QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel )
#         self._buttonBox.layout().setDirection( QBoxLayout.RightToLeft )
#         self._buttonBox.button( QtWidgets.QDialogButtonBox.Ok ).clicked.connect( self._onOk )
#         self._buttonBox.button( QtWidgets.QDialogButtonBox.Cancel ).clicked.connect( self._onCancel )
#         vbox.addWidget( self._buttonBox )
#
#     def setSelectedDate( self, date:QDate ):
#         self._calendar.setSelectedDate( date )
#
#     def setSelectedDateFromString( self, datestring:str ):
#         """
#         datestring needs to be given as "yyyy-mm-dd" or "dd.mm.yyyy"
#         day and month may be given one-digit.
#         :param datestring:
#         :return:
#         """
#         parts = datestring.split( "-" )
#         if len( parts ) == 0:
#             parts = datestring.split( "." )
#         else: # yyyy-mm-dd
#             dt = QDate( int(parts[0]), int(parts[1]), int(parts[2]) )
#             self.setSelectedDate( dt )
#         if len( parts ) == 0:
#             raise Exception( "CalendarDialog.setSelectedDateFromString: wrong date format '%s'"
#                              % (datestring) )
#         else: # dd.mm.yyyy
#             dt = QDate( int( parts[2] ), int( parts[1] ), int( parts[0] ) )
#             self.setSelectedDate( dt )
#
#     def _onOk( self ):
#         date:QDate =  self._calendar.selectedDate()
#         self.hide()
#         if self._callback:
#             self._callback( date )
#
#     def _onCancel( self ):
#         self.hide()
#
# #########################  SmartDateEdit  #####################################
# class SmartDateEdit( QLineEdit ):
#     def __init__( self, parent=None ):
#         QLineEdit.__init__( self, parent )
#
#     def mouseDoubleClickEvent( self, event ):
#         #print( "Double Click SmartDateEdit at pos: ", event.pos() )
#         self.showCalendar()
#
#     def setDate( self, year:int, month:int, day:int, format:str="yyyy-MM-dd" ):
#         dt = QDate( year, month, day )
#         ds = dt.toString( format )
#         self.setText( ds )
#
#     def setDateFromIsoString( self, isostring:str ):
#         self.setText( isostring )
#
#     def getDate( self ) -> str:
#         """
#         liefert das eingestellte Datum in dem Format, wie es im Feld zu sehen ist.
#         Ist der Wert im Feld ungültig, wird ein Leerstring ("") zurückgegeben.
#         :param format:
#         :return:
#         """
#         ds = self.text()
#         if ds.endswith( "\n" ): ds = ds[:-1]
#         if isValidIsoDatestring( ds ) or isValidEurDatestring( ds ):
#             return ds
#         else:
#             return ""
#
#     def isDateValid( self ) -> bool:
#         """
#         Prüft, ob der String im Edit-Feld ein gültiges Datum darstellt (True) oder nicht (False).
#         Ein leeres Feld gilt als "gültig" (True)
#         :return:
#         """
#         ds = self.text()
#         if ds.endswith( "\n" ): ds = ds[:-1]
#         if ds == "": return True
#         return ( isValidIsoDatestring( ds ) or isValidEurDatestring( ds ) )
#
#     def showCalendar( self ):
#         cal = CalendarDialog( self )
#         text = self.text()
#         d:QDate = None
#         if text == "":
#             d = getRelativeQDate( 0, 0 )
#         else:
#             if isValidIsoDatestring( text ):
#                 d = getQDateFromIsoString( text )
#
#             else:
#                 d =getRelativeQDate( 0, 0 )
#         cal.setSelectedDate( d )
#         cal.setCallback( self.onDatumSelected )
#         cal.show()
#
#     def onDatumSelected( self, date:QDate ):
#         self.setText( date.toString( "yyyy-MM-dd" ) )

######################  BaseLabel ##################################
class BaseLabel( QLabel ):
    def __init__( self, parent=None ):
        QLabel.__init__( self, parent )


#######################  BaseEdit  ###################################
class BaseEdit( QLineEdit ):
    def __init__( self, parent=None ):
        QLineEdit.__init__( self, parent )

    def mousePressEvent(self, evt:QMouseEvent):
        self.setSelection( 0, len( self.text() ) )

#########################  FloatEdit  ################################
class FloatEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        floatval = QDoubleValidator()
        self.setValidator( floatval )
        self.setAlignment( Qt.AlignRight )

    def getFloatValue( self ) -> float:
        val = self.text()
        if not val:
            val = "0.0"
        else:
            val = val.replace( ",", "." )
        return float( val )

    def setFloatValue( self, val:float ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def setFloatStringValue( self, val:str ):
        try:
            floatval = float( val )
            self.setFloatValue( floatval )
        except:
            self.setText( "" )

#########################  FloatEdit  ################################
class IntEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()
        self.setValidator( intval )
        self.setAlignment( Qt.AlignRight )

    def getIntValue( self ) -> int:
        val = self.text()
        if not val:
            val = "0"
        return int( val )

    def setIntValue( self, val:int ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def setIntStringValue( self, val:str ):
        try:
            intval = int( val )
            self.setIntValue( intval )
        except:
            self.setText( "" )

######################## Int Display  #############################
class IntDisplay( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()
        self.setValidator( intval )
        font = QFont( "Times New Roman", 12, QFont.Bold )
        self.setFont( font )
        # self.setStyleSheet( "color: red;" )
        self.setAlignment( Qt.AlignRight )

    def setIntValue( self, val:int ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def getIntValue( self ) -> int:
        val = self.text()
        if not val: val = "0"
        return int( val )

################ TextDocument #####################
class TextDocument( QTextDocument ):
    def __init__( self, text ):
        QTextDocument.__init__( self, text )

################ LineEdit #########################
class LineEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()

    def setValue( self, value:Any ) -> None:
        self.setText( value )
        if value is None or value == "": return
        if isinstance( value, numbers.Number ):
            self.setAlignment( Qt.AlignRight )
        else:
            self.setAlignment( Qt.AlignLeft )

    def getValue( self ) -> Any:
        return self.text()

################  MultiLineEdit  ##################
class MultiLineEdit( QTextEdit ):
    def __init__( self, parent=None ):
        QTextEdit.__init__( self, parent )

# ################ TableViewDialog ##################
# class TableViewDialog( QDialog ):
#     def __init__( self, parent=None ):
#         QDialog.__init__( self, parent )
#         self.setModal( True )
#         self._selectedCallback = None
#
#         self._tv = TableView( self )
#         self._btnOk = QPushButton( self, text = "Übernehmen zur Bearbeitung" )
#         self._btnOk.clicked.connect( self._onOk )
#         self._btnClose = QPushButton( self, text="Schließen" )
#         self._btnClose.clicked.connect( self._onClose )
#
#         vlayout = QVBoxLayout( self )
#         vlayout.addWidget( self._tv )
#         hlayout = QHBoxLayout()
#         hlayout.addWidget( self._btnOk )
#         hlayout.addWidget( self._btnClose )
#         vlayout.addLayout( hlayout )
#
#         self.setLayout( vlayout )
#
#     def getTableView( self ) -> TableView:
#         return self._tv
#
#     def setSelectedCallback( self, cbfnc ):
#         """
#         Callback function must accept a list of QModelIndex representing the selected rows/columns
#         :param cbfnc:
#         :return:
#         """
#         self._selectedCallback = cbfnc
#
#     def setTableModel( self, model:QAbstractTableModel ):
#         self._tv.setModel( model )
#         self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
#         self._tv.resizeColumnsToContents()
#
#     def _onOk( self ):
#         if self._selectedCallback:
#             sel_list = self._tv.selectedIndexes()
#             self._selectedCallback( sel_list )
#         self._onClose()
#
#     def _onClose( self ):
#         self.close()

###############  CheckBox  ########################
class CheckBox( QCheckBox ):
    def __init__( self, parent=None ):
        QCheckBox.__init__( self, parent )

################ SumDialog ########################
class SumDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Summe der selektierten Zahlen" )
        layout = QGridLayout( self )
        self.label = QtWidgets.QLabel( self )
        self.label.setText( "Summe:" )
        layout.addWidget( self.label, 0, 0 )

        self._sumLabel = QtWidgets.QLabel( self )
        layout.addWidget( self._sumLabel, 0, 1 )

        self._btnCopyToClipboard = QPushButton( self, text="Kopieren" )
        layout.addWidget( self._btnCopyToClipboard, 1, 0 )
        self._btnCopyToClipboard.clicked.connect( self._copy2clipboard )

        self._btnClose = QPushButton( self, text="Schließen" )
        layout.addWidget( self._btnClose, 1, 1 )
        self._btnClose.clicked.connect( self._onClose )
        self.setLayout( layout )

    def _copy2clipboard( self ):
        """
        kopiert die angezeigte Zahl ins Clipboard
        :return:
        """
        clipboard = QGuiApplication.clipboard()
        clipboard.setText( self._sumLabel.text() )

    def _onClose( self ):
        self.close()

    def setSum( self, sum:int or float ) -> None:
        self._sumLabel.setText( str( sum ) )

####################################################################

class CustomItem( QStandardItem ):
    def __init__( self, text:str, userdata:Any=None ):
        QStandardItem.__init__( self, text )
        self.userdata = userdata

#####################################################################

class AuswahlDialog( QDialog ):
    def __init__( self, title=None,  parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self.listView = QListView()
        self.font = QFont( "Arial", 14 )
        self.okButton = QPushButton( "OK" )
        self.cancelButton = QPushButton( "Abbrechen" )
        self.model = QStandardItemModel()
        self.listView.setModel( self.model )
        self._selectedIndexes = ""
        self._createGui()

    def _createGui( self ):
        hbox = QHBoxLayout()
        hbox.addStretch( 1 )
        hbox.addWidget( self.okButton )
        hbox.addWidget( self.cancelButton )

        vbox = QVBoxLayout( self )
        vbox.addWidget( self.listView, stretch=1 )
        # vbox.addStretch(1)
        vbox.addLayout( hbox )

        self.okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "Auswahl" )

        self.okButton.clicked.connect( self.onAccepted )
        self.cancelButton.clicked.connect( self.reject )

    def appendItemList( self, itemlist:List[str] ):
        for i in itemlist:
            self.appendItem( i, None )

    def appendItem( self, text:str, userdata:Any=None ):
        item = CustomItem( text )
        if userdata:
            item.userdata = userdata
        item.setFont( self.font )
        self.model.appendRow( item )
        if self.model.rowCount() == 1:
            self.listView.setCurrentIndex( self.model.index( 0, 0 ) )

    def onAccepted(self):
        self._selectedIndexes = self.listView.selectedIndexes()
        self.accept()

    def getSelectedIndexes( self ):
        return self._selectedIndexes

    def getSelection( self ) -> List[Tuple]:
        sel = self.getSelectedIndexes()
        l = list()
        for idx in sel:
            item:CustomItem = self.model.item( idx.row(), idx.column() )
            t = ( item.text(), item.userdata )
            l.append( t )

        return l

#####################################################################

class CheckableAuswahlDialog( QDialog ):
    def __init__( self, stringlist:List[str], checked=False, title=None, icon=None, parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self.icon = icon
        self.listView = QListView()
        self.okButton = QPushButton( "OK" )
        self.cancelButton = QPushButton( "Abbrechen" )
        self.selectButton = QPushButton( "Alle auswählen" )
        self.unselectButton = QPushButton( "Auswahl aufheben" )
        self.font = QFont( "Arial", 14 )
        self.model = QStandardItemModel()
        self.choices:List[str] = list()
        self._createGui()
        self._createModel( stringlist, checked )

    def _createGui( self ):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        h2box = QHBoxLayout()
        h2box.addStretch( 1 )
        h2box.addWidget(self.selectButton)
        h2box.addWidget(self.unselectButton)

        vbox = QVBoxLayout(self)
        vbox.addLayout( h2box )
        vbox.addWidget(self.listView, stretch=1)
        #vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "Auswahl" )

        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def _createModel( self, masterobjektList:List[str], checked:bool ):
        for obj in masterobjektList:
            item = QStandardItem( obj )
            item.setCheckable(True)
            item.setFont( self.font )
            check = (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)
        self.listView.setModel( self.model )


    def onAccepted(self):
        self.choices = [self.model.item(i).text() for i in  range(self.model.rowCount() )
                        if self.model.item(i).checkState() == QtCore.Qt.Checked]
        self.accept()

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)


def testCustomTableViewDialog():
    def onOkOrCancel( ):
        print( "onOkOrCancel" )
    app = QApplication()
    dlg = CustomTableViewDialog( None, True )
    dlg.okPressed.connect( onOkOrCancel )
    dlg.cancelPressed.connect( onOkOrCancel )
    dlg.exec_()


def testAuswahlDialog():
    app = QApplication()
    dlg = AuswahlDialog( title="Eine Auswahl" )
    dlg.appendItem( "dear me", 1 )
    dlg.appendItem( "dear you", 2 )
    if dlg.exec_() == QDialog.Accepted:
        l = dlg.getSelection()
        for t in l:
            print( "selected: ", t[0], t[1] )
        # indexes = dlg.getSelectedIndexes()
        # for i in indexes:
        #     print( "Selected: ", i.row() )

def onClick( l:List[str] ):
    print( l )

def test():
    app = QApplication()
    dlg = CheckableAuswahlDialog( ["SB_Kaiser", "ILL_Eich", "NK_Kleist"], title="Freie Auswahl!", checked=True )
    if dlg.exec_() == QDialog.Accepted:
        print( '\n'.join( [str( s ) for s in dlg.choices] ) )
    #app.exec_()

if __name__ == "__main__":
    #test()
    #testAuswahlDialog()
    testCustomTableViewDialog()