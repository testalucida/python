
##################  MieteTableView  ##############
from abc import abstractmethod
from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import Signal, QModelIndex, Qt
from PySide2.QtGui import QDoubleValidator
from PySide2.QtWidgets import QDialog, QGridLayout, QPushButton

from v2.icc.iccwidgets import IccTableView, IccCheckTableViewFrame
from v2.mtleinaus.mtleinauslogic import MieteTableModel


##############   MtlEinAusTableView   #################
class MtlEinAusTableView( IccTableView ):
    def __init__( self ):
        IccTableView.__init__( self )

##############   MieteTableView   #################
class MieteTableView( MtlEinAusTableView ):
    okClicked = Signal( QModelIndex )
    nokClicked = Signal( QModelIndex )
    def __init__( self ):
        MtlEinAusTableView.__init__( self )
        self.setAlternatingRowColors( True )
        #self.btvLeftClicked.connect( lambda idx: self.okClicked.emit(idx) )
        self.btvLeftClicked.connect( self.onLeftClicked )
        self._columnsWidth:List[int] = list()

    def setModel( self, model:MieteTableModel ):
        super().setModel( model, selectRows=False, singleSelection=False )
        if len( self._columnsWidth ) == 0:
            oknoksize = 30
            self.horizontalHeader().setMinimumSectionSize( oknoksize )
            self.setColumnWidth( model.getOkColumnIdx(), oknoksize )
            self.setColumnWidth( model.getNokColumnIdx(), oknoksize )
            for c in range( 0, model.columnCount() ):
                self._columnsWidth.append( self.columnWidth( c ) )
        else:
            for c in range( 0, model.columnCount() ):
                self.setColumnWidth( c, self._columnsWidth[c] )

    def onLeftClicked( self, index:QModelIndex ):
        isOkColumn, isNokColumn = False, False
        if index.column() == self.model().getOkColumnIdx():
            isOkColumn = True
            self.okClicked.emit( index )
        elif index.column() == self.model().getNokColumnIdx():
            isNokColumn = True
            self.nokClicked.emit( index )
        if True in ( isOkColumn, isNokColumn ):
            self.clearSelection()

###############  MieteTableViewFrame  #############
class MieteTableViewFrame( IccCheckTableViewFrame ):
    def __init__( self, tableView:MieteTableView ):
        IccCheckTableViewFrame.__init__( self, tableView )

################ ValueDialog ########################
class ValueDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Abweichender Betrag" )
        layout = QGridLayout( self )
        self.label = QtWidgets.QLabel( self )
        self.setLabelText( "Betrag eingeben:" )
        layout.addWidget( self.label, 0, 0 )

        self._numEntry = QtWidgets.QLineEdit( self )
        layout.addWidget( self._numEntry, 1, 0 )
        self._numEntry.setAlignment( Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter )
        self._numEntry.setValidator( QDoubleValidator( -9999, 9999, 2, self ) )
        self._numEntry.setFocus()

        self.btnAdd = QPushButton( self, text="+" )
        layout.addWidget( self.btnAdd, 0, 1 )
        self.btnAdd.clicked.connect( self._add )

        self.btnSub = QPushButton( self, text="-" )
        layout.addWidget( self.btnSub, 1, 1 )
        self.btnSub.clicked.connect( self._sub )

        self.btnRepl = QPushButton( self, text="=" )
        layout.addWidget( self.btnRepl, 2, 1 )
        self.btnRepl.clicked.connect( self._replace )

        self.btnCancel = QPushButton( self, text="Cancel" )
        layout.addWidget( self.btnCancel, 2, 0 )
        self.btnCancel.clicked.connect( self._cancel )

        self.setLayout( layout )

    def setCallback( self, fnc ):
        self._callback = fnc

    def setLabelText( self, text:str ) -> None:
        self.label.setText( text )

    def _doCallback( self, command:str ):
        if self._callback:
            num = self._numEntry.text()
            if num is None or num == '': num = "0"
            num = num.replace( ",", "." )
            self._callback( float( num ), command )
        self.close()

    def _add(self):
        self._doCallback( "add" )

    def _sub(self):
        self._doCallback( "sub" )

    def _replace(self):
        self._doCallback( "replace" )

    def _cancel( self ):
        self.close()