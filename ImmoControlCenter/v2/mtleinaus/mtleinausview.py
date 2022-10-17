
##################  MieteTableView  ##############
from abc import abstractmethod
from typing import List, Callable

from PySide2 import QtWidgets
from PySide2.QtCore import Signal, QModelIndex, Qt
from PySide2.QtGui import QDoubleValidator
from PySide2.QtWidgets import QDialog, QGridLayout, QPushButton, QApplication, QWidget, QHBoxLayout

from base.baseqtderivates import BaseEdit, BaseDialog, BaseDialogWithButtons, getOkCancelButtonDefinitions, \
    getCloseButtonDefinition
from v2.einaus.einausview import EinAusTableView, EinAusTableViewFrame
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

################   MtlZahlungEditDialog   ###########
class MtlZahlungEditDialog( BaseDialogWithButtons ):
    def __init__( self, tv:EinAusTableView, title="Ändern von Zahlungen für einen Monat" ):
        BaseDialogWithButtons.__init__( self, title,
                                        getCloseButtonDefinition( self.onClose ) )
        self._tv:EinAusTableView = tv
        self._tvframe:EinAusTableViewFrame = EinAusTableViewFrame( self._tv, withEditButtons=True )
        self.setMainWidget( self._tvframe )

    def getTableViewFrame( self ) -> EinAusTableViewFrame:
        return self._tvframe

    def onClose( self ):
            self.accept()

    # def onCancel( self ):
    #     print( "onCancel")
    #     self.close()

################ ValueDialog ########################
class ValueDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self._callback:Callable = None
        self.setModal( True )
        self.setWindowTitle( "Neue Monatszahlung erfassen" )
        layout = QGridLayout( self )
        row = 0

        self._numEntry = QtWidgets.QLineEdit( self )
        self._numEntry.setPlaceholderText( "Betrag" )
        layout.addWidget( self._numEntry, row, 0 )
        self._numEntry.setAlignment( Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter )
        self._numEntry.setValidator( QDoubleValidator( -9999, 9999, 2, self ) )
        self._numEntry.setFocus()

        # self.btnAdd = QPushButton( self, text="+" )
        # layout.addWidget( self.btnAdd, row, 1 )
        # self.btnAdd.clicked.connect( self._add )
        #
        row += 1
        self._txtEntry = BaseEdit()
        self._txtEntry.setPlaceholderText( "Bemerkung" )
        layout.addWidget( self._txtEntry, row, 0 )
        #
        # self.btnSub = QPushButton( self, text="-" )
        # layout.addWidget( self.btnSub, row, 1 )
        # self.btnSub.clicked.connect( self._sub )
        #
        # row += 1
        # self.btnRepl = QPushButton( self, text="=" )
        # layout.addWidget( self.btnRepl, row, 1 )
        # self.btnRepl.clicked.connect( self._replace )

        row += 1
        self._hboxLayout = QHBoxLayout()
        self.btnOk = QPushButton( self, text="OK" )
        self.btnOk.clicked.connect( self._ok )
        self._hboxLayout.addWidget( self.btnOk )

        self.btnCancel = QPushButton( self, text="Cancel" )
        self.btnCancel.clicked.connect( self._cancel )
        self._hboxLayout.addWidget( self.btnCancel )

        layout.addLayout( self._hboxLayout, row, 0 )
        self.setLayout( layout )

        #QWidget.setTabOrder( self._txtEntry, self.btnAdd )

    def setCallback( self, fnc ):
        """
        Callback nach Button-Click "+", "-", "-"
        Die Callback-Function muss folgende Signatur haben: value:float, command:str, text:str
        :param fnc:
        :return:
        """
        self._callback = fnc

    def setLabelText( self, text:str ) -> None:
        self.label.setText( text )

    def _doCallback( self ):
        if self._callback:
            num = self._numEntry.text()
            if num is None or num == '': num = "0"
            num = num.replace( ",", "." )
            self._callback( float( num ), self._txtEntry.text() )
        self.close()

    # def _add(self):
    #     self._doCallback( "add" )
    #
    # def _sub(self):
    #     self._doCallback( "sub" )
    #
    # def _replace(self):
    #     self._doCallback( "replace" )

    def _cancel( self ):
        self.close()

    def _ok( self ):
        self._doCallback()

###################  TEST   TEST   TEST   #################

def test2():
    # def validation() -> bool:
    #     #return True
    #     return False

    app = QApplication()
    dlg = MtlZahlungEditDialog( EinAusTableView() )
    if dlg.exec_() == QDialog.Accepted:
        print( "storing modifications")

def test():
    app = QApplication()
    dlg = ValueDialog()
    dlg.exec_()
