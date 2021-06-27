import os
from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import QAbstractTableModel, Qt, Signal, QModelIndex, QPoint
from PySide2.QtWidgets import QDialog, QPushButton, QTableView, QGridLayout, QApplication, QHBoxLayout, \
    QAbstractItemView, QVBoxLayout, QLabel, QWidget

from imagefactory import ImageFactory

##########################################################

class GenericTableView(QTableView):
    leftClicked = Signal( QModelIndex )
    rightClicked = Signal( [QModelIndex] )
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        # left mouse click
        self.clicked.connect( self.onLeftClick )
        # right mouse click
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.onRightClick )

    def onRightClick( self, point:QPoint ):
        selected_indexes = self.selectedIndexes()
        print( "GenericTableView.onRightClick:", selected_indexes )
        self.rightClicked.emit( selected_indexes )

    def onLeftClick( self, index:QModelIndex ):
        print( index.row(), index.column() )
        print( "GenericTableView.onLeftClick: %d,%d" % ( index.row(), index.column() ) )

########################################################

class GenericEditableTableView( QWidget ):
    createItem = Signal()
    editItem = Signal( QModelIndex )
    deleteItem = Signal( QModelIndex )
    okPressed = Signal()
    cancelled = Signal()

    def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
        QWidget.__init__( self, parent )
        self._isEditable = isEditable
        self._layout = QGridLayout()
        if isEditable:
            self._newButton = QPushButton()
            icon = ImageFactory.inst().getPlusIcon()
            self._newButton.setIcon( icon )
            self._newButton.setToolTip( "Neuen Tabelleneintrag anlegen" )

            self._editButton = QPushButton()
            icon = ImageFactory.inst().getEditIcon()
            self._editButton.setIcon( icon )
            self._editButton.setToolTip( "Ausgewählten Tabelleneintrag bearbeiten" )

            self._deleteButton = QPushButton()
            icon = ImageFactory.inst().getDeleteIcon()
            self._deleteButton.setIcon( icon )
            self._deleteButton.setToolTip( "Ausgewählten Tabelleneintrag löschen" )

        self._tv = GenericTableView()
        self._createGui()
        if model:
            self.setTableModel( model )

    def _createGui( self ):
        if self._isEditable:
            self._createEditButtons()

        self._tv.horizontalHeader().setStretchLastSection( True )
        self._layout.addWidget( self._tv, 1, 0)
        self.setLayout( self._layout )

    def _createEditButtons( self ):
        self._newButton.clicked.connect( self._onNew )
        self._editButton.clicked.connect( self._onEdit )
        self._deleteButton.clicked.connect( self._onDelete )
        hbox = QHBoxLayout()
        hbox.addWidget( self._newButton )
        hbox.addWidget( self._editButton )
        hbox.addWidget( self._deleteButton )
        self._layout.addLayout( hbox, 2, 0, alignment=Qt.AlignLeft )

    def setTableModel( self, model:QAbstractTableModel ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()
        self._tv.setSelectionBehavior( QTableView.SelectRows )
        self._tv.setSelectionMode( QAbstractItemView.SingleSelection )
        if self._isEditable:
            self._newButton.setFocus()
        else:
            self._okButton.setFocus()

    def getModel( self ):
        return self._tv.model()

    def _onNew( self ):
        self.createItem.emit()

    def _onEdit( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "GenericTableViewDialog: no item selected to edit" )
        self.editItem.emit( indexlist[0] )

    def _onDelete( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "GenericTableViewDialog: no item selected to delete" )
        self.deleteItem.emit( indexlist[0] )

    def getTableView( self ) -> GenericTableView:
        return self._tv

    def getSelectedIndexes( self ) -> List[QModelIndex]:
        """
        returns an empty list if no item is selected
        :return:
        """
        indexes = self._tv.selectionModel().selectedIndexes()
        return indexes

    def getSelectedRows( self ) -> List[int]:
        indexes = self.getSelectedIndexes()
        l = list()
        for i in indexes:
            l.append( i.row() )
        return l

    def getFirstSelectedRow( self ) -> int:
        rowlist = self.getSelectedRows()
        return rowlist[0] if len( rowlist ) > 0 else -1

########################################################

class GenericTableViewDialog( QDialog ):
    createItem = Signal()
    editItem = Signal( QModelIndex )
    deleteItem = Signal( QModelIndex )
    okPressed = Signal()
    cancelled = Signal()

    def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
        QDialog.__init__( self, parent )
        self._isEditable = isEditable
        self._layout = QGridLayout( self )
        #self._imagePath =
        self._okButton = QPushButton( "OK" )
        self._cancelButton = QPushButton( "Abbrechen" )
        if isEditable:
            self._newButton = QPushButton()
            icon = ImageFactory.inst().getPlusIcon()
            self._newButton.setIcon( icon )
            self._newButton.setToolTip( "Neuen Tabelleneintrag anlegen" )

            self._editButton = QPushButton()
            icon = ImageFactory.inst().getEditIcon()
            self._editButton.setIcon( icon )
            self._editButton.setToolTip( "Ausgewählten Tabelleneintrag bearbeiten" )

            self._deleteButton = QPushButton()
            icon = ImageFactory.inst().getDeleteIcon()
            self._deleteButton.setIcon( icon )
            self._deleteButton.setToolTip( "Ausgewählten Tabelleneintrag löschen" )

        self._tv = GenericTableView( self )
        self._createGui()
        self.setModal( True )
        if model:
            self.setTableModel( model )

    def _createGui( self ):
        if self._isEditable:
            self._createEditButtons()
        self._okButton.clicked.connect( self._onOk )
        self._cancelButton.clicked.connect( self._onCancel )
        hbox = QHBoxLayout()
        hbox.addWidget( self._okButton )
        hbox.addWidget( self._cancelButton )

        self._tv.horizontalHeader().setStretchLastSection( True )
        self._layout.addWidget( self._tv, 1, 0)
        self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft )
        self.setLayout( self._layout )

    def _createEditButtons( self ):
        self._newButton.clicked.connect( self._onNew )
        self._editButton.clicked.connect( self._onEdit )
        self._deleteButton.clicked.connect( self._onDelete )
        hbox = QHBoxLayout()
        hbox.addWidget( self._newButton )
        hbox.addWidget( self._editButton )
        hbox.addWidget( self._deleteButton )
        self._layout.addLayout( hbox, 2, 0, alignment=Qt.AlignLeft )

    def setCancelButtonVisible( self, visible:bool=True ):
        self._cancelButton.setVisible( False )

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def setTableModel( self, model:QAbstractTableModel ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()
        self._tv.setSelectionBehavior( QTableView.SelectRows )
        self._tv.setSelectionMode( QAbstractItemView.SingleSelection )
        if self._isEditable:
            self._newButton.setFocus()
        else:
            self._okButton.setFocus()

    def _onNew( self ):
        self.createItem.emit()

    def _onEdit( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "GenericTableViewDialog: no item selected to edit" )
        self.editItem.emit( indexlist[0] )

    def _onDelete( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "GenericTableViewDialog: no item selected to delete" )
        self.deleteItem.emit( indexlist[0] )

    def _onOk( self ):
        self.okPressed.emit()
        self.accept()

    def _onCancel( self ):
        self.cancelled.emit()
        self.reject()

    def getTableView( self ) -> GenericTableView:
        return self._tv

    def getSelectedIndexes( self ) -> List[QModelIndex]:
        """
        returns an empty list if no item is selected
        :return:
        """
        indexes = self._tv.selectionModel().selectedIndexes()
        return indexes

    def getSelectedRows( self ) -> List[int]:
        indexes = self.getSelectedIndexes()
        l = list()
        for i in indexes:
            l.append( i.row() )
        return l

    def getFirstSelectedRow( self ) -> int:
        rowlist = self.getSelectedRows()
        return rowlist[0] if len( rowlist ) > 0 else -1
###########################################################

def doEdit( idx:QModelIndex ):
    print( "Edit %d/%d" % (idx.row(), idx.column() ) )

def test():
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
    dlg = GenericTableViewDialog( isEditable=True )
    dlg.setWindowTitle( "testdialog" )
    dlg.setTableModel( tm )
    dlg.editItem.connect( doEdit )
    #dlg.setCancelButtonVisible( False )
    dlg.setOkButtonText( "Speichern" )
    dlg.show()
    app.exec_()


if __name__ == "__main__":
    test()