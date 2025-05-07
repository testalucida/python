import os
from numbers import Number
from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import QAbstractTableModel, Qt, Signal, QModelIndex, QPoint
from PySide2.QtGui import QMouseEvent, QGuiApplication
from PySide2.QtWidgets import QDialog, QPushButton, QTableView, QGridLayout, QApplication, QHBoxLayout, \
    QAbstractItemView, QVBoxLayout, QLabel, QWidget, QAbstractScrollArea, QHeaderView, QTextEdit, QAction, QMenu

###################  EditableTableViewWidget  #########################
from customtable_stuff.customtableview import CustomTableView


class EditableTableViewWidget( QWidget ):
    createItem = Signal()
    editItem = Signal( QModelIndex )
    deleteItem = Signal( QModelIndex )

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

        self._tv = CustomTableView()
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

    def setTableModel( self, model:QAbstractTableModel,  selectRows:bool=True, singleSelection:bool=True  ):
        self._tv.setModel( model, selectRows, singleSelection )
        if self._isEditable:
            self._newButton.setFocus()

    def getModel( self ):
        return self._tv.model()

    def getTableView( self ) -> CustomTableView:
        return self._tv

    def _onNew( self ):
        self.createItem.emit()

    def _onEdit( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "EditableTableViewWidget: no item selected to edit" )
        self.editItem.emit( indexlist[0] )

    def _onDelete( self ):
        indexlist = self.getSelectedIndexes()
        if len( indexlist ) == 0:
            raise Exception( "EditableTableViewWidget: no item selected to delete" )
        self.deleteItem.emit( indexlist[0] )

    def getSelectedIndexes( self ) -> List[QModelIndex]:
        """
        returns an empty list if no item is selected
        :return:
        """
        sm = self._tv.selectionModel()
        if sm:
            return sm.selectedIndexes()
        return list()

    def getSelectedRows( self ) -> List[int]:
        indexes = self.getSelectedIndexes()
        l = list()
        for i in indexes:
            l.append( i.row() )
        return l

    def getFirstSelectedRow( self ) -> int:
        rowlist = self.getSelectedRows()
        return rowlist[0] if len( rowlist ) > 0 else -1
