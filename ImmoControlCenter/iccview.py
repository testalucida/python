from abc import abstractmethod, ABC
from typing import Any, List

from PySide2.QtCore import Signal, Qt, QSize, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import QWidget, QTableView, QPushButton, QGridLayout, QHBoxLayout, QApplication, QComboBox

from definitions import ICON_DIR
from generictable_stuff.xbasetablemodel import XBaseTableModel
from icctableeditor import IccTableEditor
from interfaces import XBase
from qtderivates import HLine


class IccViewMeta( type(QWidget), type(ABC) ):
    pass

class IccView( QWidget, ABC, metaclass=IccViewMeta ):
    """
    Beim Entwurf dieser Klasse war das Hirn leider nicht beteiligt.
    """
    def __init__( self ):
        QWidget.__init__( self, None )


    @abstractmethod
    def getModel( self ) -> Any:
        pass

    @abstractmethod
    def setModel( self, model:Any ) ->None:
        pass

    @abstractmethod
    def addJahr( self, jahr:int ) -> None:
        pass

    @abstractmethod
    def getTableView( self ) -> QTableView:
        pass

######################   IccToolBarView   #################
class IccToolBarView( QWidget ):
    """
    Eine View, von QWidget abgeleitet, die eine Toolbar besitzt.
    Die Toolbar ist standardmäßig mit einem Save-Button ausgestattet.
    Wird dieser gedrückt, wird ein save-Signal gesendet.
    Mit der Methode setSaveButtonEnabled kann der Save-Button enabled/disabled werden.
    Mittels der addTool-Methode können der Toolbar weitere Widgets hinzugefügt werden.
    Mittels der addWidget-Methode können der View Widgets hinzugefügt werden.
    """
    save = Signal()
    def __init__( self ):
        QWidget.__init__( self, None )
        self._btnSave = QPushButton()
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._toolbarLayout = QHBoxLayout()
        self._layout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._addSaveButtonToToolBar()

    def _addSaveButtonToToolBar( self ):
        self._btnSave.setFixedSize( QSize( 30, 30 ) )
        #self._btnSave.setFlat( True )
        self._btnSave.setIcon( QIcon( ICON_DIR + "save.png" ) )
        self._btnSave.setIconSize( QSize( 22, 22 ) )
        self._btnSave.setToolTip( "Änderungen speichern." )
        self._btnSave.clicked.connect( self.save.emit )
        self.addTool( self._btnSave )

    def addTool( self, widget:QWidget ):
        """
        Fügt der Toolbar ein Tool hinzu
        :param widget:
        :return:
        """
        self._toolbarLayout.addWidget( widget )

    def addWidget( self, widget:QWidget, r:int, c:int, alignment=None, rowspan:int=1, colspan:int=1 ):
        """
        Fügt dem Layout an gewünschter Stelle <widget> hinzu.
        :param widget:
        :param r:
        :param c:
        :param alignment: todo: FUNKTIONIERT NICHT!! (Wird nicht verwendet)
        :param rowspan:
        :param colspan:
        :return:
        """
        if alignment is None:
            self._layout.addWidget( widget, r, c )
        else:
            self._layout.addWidget( widget, r, c, alignment=alignment )
        return self._layout.columnCount()

    def getLayout( self ) -> QGridLayout:
        return self._layout

    def getColumnCount( self ) -> int:
        return self._layout.columnCount()

    def createHLine( self, r:int, colspan:int ):
        line = HLine()
        self._layout.addWidget( line, r, 0, 1, colspan )

    def createDummyRow( self, r:int, h:int ):
        dummy = QWidget()
        dummy.setFixedHeight( h )
        self._layout.addWidget( dummy, r, 0 )

    def clear( self ):
        raise NotImplementedError( "IccView2.clear()" )

    def applyChanges( self ):
        raise NotImplementedError( "IccView2.applyChanges()" )

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

#####################   IccTableEditorView   ##############
class IccTableEditorView( IccToolBarView ):
    """
    Eine View mit Toolbar (durch die Ableitung von IccToolBarView) und einem IccTableEditor im Hauptfeld.
    Die Signale des IccTableEditor (createItem, editItem, deleteItem) werden von den Methoden
    onCreate(), onEdit, onDelete aufgefangen, wo zum übergebenen QModelIndex das entsprechende XBase-Objekt
    ermittelt wird. Damit werden eigene Signale createItem, editItem und deleteItem gesendet.
    Das save-Signal, das von IccToolBarView gesendet wird, wird hier nicht behandelt. Es muss von den
    Objekten aufgefangen werden, die diese IccTableEditorView instanzieren oder von ihr ableiten.
    """
    createItem = Signal()
    editItem = Signal( XBase )
    deleteItem = Signal( XBase )
    def __init__( self, model:XBaseTableModel=None ):
        IccToolBarView.__init__( self )
        self._tableEditor = IccTableEditor( model )
        self._tableEditor.createItem.connect( self.onCreate )
        self._tableEditor.editItem.connect( self.onEdit )
        self._tableEditor.deleteItem.connect( self.onDelete )
        self.addWidget( self._tableEditor, 1, 0 )

    def setTableModel( self, model:XBaseTableModel ):
        self._tableEditor.setTableModel( model )

    def getTableModel( self ) -> XBaseTableModel:
        return self._tableEditor.getTableModel()

    def getElement( self, indexrow:int ) -> XBase:
        x = self.getTableModel().getElement( indexrow )
        return x

    def onCreate( self ):
        self.createItem.emit()

    def onEdit( self, idx:QModelIndex ):
        x = self.getElement( idx.row() )
        self.editItem.emit( x )

    def onDelete( self, idx:QModelIndex ):
        x = self.getElement( idx.row() )
        self.deleteItem.emit( x )

######################   IccTableEditorYearSpecificView   ######################
class IccTableEditorYearSpecificView( IccTableEditorView ):
    """
    Eine von IccTableEditorView abgeleitete Klasse, die in der Toolbar neben dem Speichern-Button eine Jahr-Combobox
    hat. Sie wird mit den Methoden addJahr, addJahre, setCurrentJahr und clearJahre bedient.
    Wird das Jahr geändert, wird ein yearChanged-Signal gesendet.
    """
    yearChanged = Signal( int )
    def __init__(self, model:XBaseTableModel=None ):
        IccTableEditorView.__init__( self, model )
        self._cboYear = QComboBox()
        self._cboYear.setFont( QFont( "Arial", 14, weight=QFont.Bold ) )
        self._cboYear.currentTextChanged.connect( self.onCurrentYearChanged )
        self.addTool( self._cboYear )

    def addJahr( self, jahr:int ):
        self._cboYear.addItem( text=str(jahr) )

    def addJahre( self, jahre:List[int] ):
        self._cboYear.addItems( [str(j) for j in jahre] )

    def setCurrentJahr( self, jahr:int ):
        self._cboYear.setCurrentText( str(jahr) )

    def clearJahre( self ):
        self._cboYear.clear()

    def onCurrentYearChanged( self, sJahrNeu:str ):
        self.yearChanged.emit( int( sJahrNeu) )

########################   TESTS   #######################
class TestView( QWidget ):
    def __init__(self):
        QWidget.__init__( self )
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self.tableEditor = IccTableEditor()
        self._layout.addWidget( self.tableEditor, 0, 0 )

def test2():
    app = QApplication()
    v = TestView()
    v.setWindowTitle( "Test")
    v.show()
    app.exec_()

def test3():
    def yearChanged( year ):
        print( "year changed: ", year )
    def onSave():
        print( "onSave" )
        v.setSaveButtonEnabled( False )
    app = QApplication()
    v = IccTableEditorYearSpecificView()
    v.setWindowTitle( "Test zum Testen von Jahren" )
    v.addJahre( [2021, 2022] )
    v.yearChanged.connect( yearChanged )
    v.save.connect( onSave )
    v.show()
    app.exec_()

def test():
    app = QApplication()
    v = IccTableEditorView()
    v.setWindowTitle( "Test zum Testen")
    v.show()
    app.exec_()