import os
from numbers import Number
from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import QAbstractTableModel, Qt, Signal, QModelIndex, QPoint
from PySide2.QtGui import QMouseEvent, QGuiApplication
from PySide2.QtWidgets import QDialog, QPushButton, QTableView, QGridLayout, QApplication, QHBoxLayout, \
    QAbstractItemView, QVBoxLayout, QLabel, QWidget, QAbstractScrollArea, QHeaderView, QTextEdit, QAction, QMenu



# #####################  Cell  #################################
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
#             if isinstance( val, Number ):
#                 values += str( val )
#             else:
#                 values += val
#             #print( idx.row(), "/", idx.column(), ": ", val )
#         #print( "valuestring: ",  values )
#         clipboard = QGuiApplication.clipboard()
#         clipboard.setText( values )


###################  GenericTableViewDialog  ##############################
# class GenericTableViewDialog( QDialog ):
#     createItem = Signal()
#     editItem = Signal( QModelIndex )
#     deleteItem = Signal( QModelIndex )
#     # okPressed = Signal()
#     # cancelled = Signal()
#
#     def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
#         QDialog.__init__( self, parent )
#         self._isEditable = isEditable
#         self._layout = QGridLayout( self )
#         #self._imagePath =
#         self._okButton = QPushButton( "OK" )
#         self._cancelButton = QPushButton( "Abbrechen" )
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
#         self._tv = CustomTableView( self )
#         self._createGui()
#         self.setModal( True )
#         if model:
#             self.setTableModel( model )
#
#     def _createGui( self ):
#         if self._isEditable:
#             self._createEditButtons()
#         self._okButton.clicked.connect( self._onOk )
#         self._cancelButton.clicked.connect( self._onCancel )
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
#         if len( indexlist ) == 0:
#             raise Exception( "GenericTableViewDialog: no item selected to edit" )
#         self.editItem.emit( indexlist[0] )
#
#     def _onDelete( self ):
#         indexlist = self._tv.getSelectedIndexes()
#         if len( indexlist ) == 0:
#             raise Exception( "GenericTableViewDialog: no item selected to delete" )
#         self.deleteItem.emit( indexlist[0] )
#
#     def _onOk( self ):
#         self.okPressed.emit()
#         self.accept()
#
#     def _onCancel( self ):
#         self.cancelled.emit()
#         self.reject()
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

#######################################################################
def doEdit( idx:QModelIndex ):
    print( "Edit %d/%d" % (idx.row(), idx.column() ) )

# def test():
#     def onCellEnter( evt:CellEvent ):
#         m = tv.model()
#         idx = m.index( evt.row, evt.column )
#         txt = m.data( idx, Qt.DisplayRole )
#         print( "onCellEnter. Text = %s" % ( txt ) )
#         z = ZoomView( txt )
#         #z.setModal( False )
#         #z.setGeometry( 1200, 100, 400, 100 )
#         z.exec_()

    class TestModel( QAbstractTableModel ):
        def __init__( self ):
            QAbstractTableModel.__init__( self )
            self._rows = [("00", "01", "02"),
                          ("10", "11", "12"),
                          ("20", "21", "22"),
                          ("30", "31", "32")]

        def rowCount( self, parent=None ):
            return 4

        def columnCount( self, parent=None ):
            return 3

        def data( self, index, role=None ):
            if not index.isValid():
                return None
            if role == Qt.DisplayRole:
                return self._rows[index.row()][index.column()]
            return None

        def headerData( self, col, orientation, role=None ):
            if orientation == Qt.Horizontal:
                if role == Qt.DisplayRole:
                    return "Spalte %d" % col
                if role == Qt.BackgroundRole:
                    pass
                    # if self.headerBrush:
                    #     return self.headerBrush
            return None

    app = QApplication()
    #os.chdir( "" )
    tm = TestModel()
    # dlg = GenericTableViewDialog( isEditable=True )
    # dlg.setWindowTitle( "testdialog" )
    # dlg.setTableModel( tm )
    # dlg.editItem.connect( doEdit )
    # #dlg.setCancelButtonVisible( False )
    # dlg.setOkButtonText( "Speichern" )
    # dlg.show()
    #v = EditableTableViewWidget( tm, True )
    # tv = v.getTableView()
    # tv.ctvCellEnter.connect( onCellEnter )
    # v.show()
    # v.getSelectedRows()
    app.exec_()


if __name__ == "__main__":
    pass
    #test()