import numbers
from typing import Any, List, Tuple, Callable, Iterable

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QDate, Qt, QAbstractTableModel, QRect, Signal, QSize
from PySide2.QtGui import QDoubleValidator, QIntValidator, QFont, QGuiApplication, QStandardItemModel, QStandardItem, \
    QMouseEvent, QTextDocument, QIcon, QFontMetrics
from PySide2.QtWidgets import QDialog, QCalendarWidget, QVBoxLayout, QBoxLayout, QLineEdit, QGridLayout, QPushButton, \
    QHBoxLayout, QApplication, QListView, QComboBox, QLabel, QTextEdit, QCheckBox, QFrame, QWidget, QAction, QTabWidget, \
    QToolBar, QMenuBar, QStatusBar

from base.directories import BASE_IMAGES_DIR
from base.interfaces import XAttribute
#from definitions import ICON_DIR

from datehelper import isValidIsoDatestring, isValidEurDatestring, getRelativeQDate, getQDateFromIsoString
#################  BaseAction  ########################
class BaseAction( QAction ):
    def __init__( self, text:str, tooltip:str="", ident:Any=None, icon:QIcon=None, parent=None ):
        QAction.__init__( self )
        if icon: self.setIcon( icon )
        self.setText( text )
        self.setToolTip( tooltip )
        self.setParent( parent )
        self.ident = ident
        #self.callback = callback

#################  BaseWidget  ########################
class BaseWidget( QWidget ):
    def __init__( self, parent=None, flags=Qt.WindowFlags() ):
        QWidget.__init__( self, parent, flags )
        self._isChanged = False
        self.ident = None

    def setChanged( self, changed:bool ) -> None:
        self._isChanged = changed

    def isChanged( self ) -> bool:
        return self._isChanged

##################  BaseTabbedWindow  #################
class BaseTabWidget( QTabWidget ):
    def __init__( self, parent=None ):
        QTabWidget.__init__( self, parent )

#################  BaseToolBar  #######################
class BaseToolBar( QToolBar ):
    def __init__( self, parent=None ):
        QToolBar.__init__( self, parent )

#################  BaseMenuBar  #######################
class BaseMenuBar( QMenuBar ):
    def __init__( self, parent=None ):
        QMenuBar.__init__( self, parent )

#################  BaseStatusBar  #######################
class BaseStatusBar( QStatusBar ):
    def __init__( self, parent=None ):
        QStatusBar.__init__( self, parent )

#################  BaseDialog  ########################
class BaseComboBox( QComboBox ):
    def __init__(self, parent=None ):
        QComboBox.__init__( self )

#################  BaseDialog  ########################
class BaseDialog( QDialog ):
    def __init__(self, parent=None, flags=Qt.WindowFlags() ):
        QDialog.__init__( self, parent, flags )

###########################   BaseDialogWithButtons  etc.  #############################
class BaseButtonDefinition:
    def __init__( self, text, tooltip:str, callback:Callable, callbackData:Any=None, icon:QIcon=None ):
        self.text = text
        self.icon:QIcon = icon
        self.tooltip = tooltip
        self.callback:Callable = callback
        self.callbackData:Any = callbackData
        self.default = False
        self.width = -1 # autowidth
        self.height = -1 # autoheight

#########################
def getOkCancelButtonDefinitions( okCallback:Callable, cancelCallback:Callable ):
        ok = BaseButtonDefinition( "  OK  ", "Übernimmt die Änderungen und schließt das Fenster.",
                                        okCallback )
        cancel = BaseButtonDefinition( "Abbrechen", "Bricht die Änderungen ab, ohne sie zu übernehmen "
                                                    "und schließt das Fenster.",
                                        cancelCallback )
        return ( ok, cancel )

def getCloseButtonDefinition( callback: Callable ):
    defi = BaseButtonDefinition( "Schließen", "Schließt das Fenster.", callback )
    return (defi,)

#########################
class BaseDialogWithButtons( BaseDialog ):
    def __init__( self, title:str, buttonDefinitions:Iterable[BaseButtonDefinition], parent=None, flags=Qt.WindowFlags() ):
        BaseDialog.__init__( self, parent, flags )
        self.setWindowTitle( title )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._buttonList:List[BaseButton] = list()
        self._mainrow = 0
        self._buttonrow = 1
        self._createGui( buttonDefinitions )

    def _createGui( self, buttonDefinitions:[BaseButtonDefinition] ):
        col = 0
        for defi in buttonDefinitions:
            btn = BaseButton()
            if defi.text:
                btn.setText( defi.text )
            if defi.icon:
                btn.setIcon( defi.icon )
            btn.setToolTip( defi.tooltip )
            btn.setDefault( defi.default )
            if defi.width > -1:
                btn.setFixedWidth( defi.width )
            if defi.height > -1:
                btn.setFixedHeight( defi.height )
            if defi.callback:
                btn.setCallback( defi.callback, defi.callbackData )
            self._layout.addWidget( btn, self._buttonrow, col )
            col += 1

    def setMainWidget( self, widget:BaseWidget ):
        self._layout.addWidget( widget, self._mainrow, 0 )


################  BaseButton  ##########################
class BaseButton( QPushButton ):
    def __init__( self, text= "", parent=None, callback:Callable=None, callbackData:Any=None ):
        QPushButton.__init__( self, text=text, parent= parent )
        self._callback:Callable = None
        self._callbackData:Any = None
        if callback:
            self.setCallback( callback, callbackData )

    def setCallback( self, callback:Callable, callbackData:Any=None ):
        self._callback: Callable = callback
        self._callbackData: Any = callbackData
        self.clicked.connect( self._doCallback )

    def _doCallback( self ):
        if self._callbackData:
            self._callback( self._callbackData )
        else:
            self._callback()

################  BaseIconButton  #####################
class BaseIconButton( BaseButton ):
    def __init__( self, icon:QIcon, size=QSize(28, 28), parent=None ):
        BaseButton.__init__( self, "", parent )
        self.setIcon( icon )
        self.setFixedSize( size )

####################  BaseIconTextButton  ################
class BaseIconTextButton( BaseButton ):
    def __init__( self, icon:QIcon, text:str, parent=None ):
        BaseButton.__init__( self, text, parent )
        self.setText( text )

#################  NewIconButton  #########################
class NewIconButton( BaseIconButton ):
    def __init__( self, parent=None ):
        BaseIconButton.__init__( self, QIcon( BASE_IMAGES_DIR + "new.png" ), QSize(28, 28), parent )
        self.setToolTip( "Neues Element anlegen" )

#################  EditIconButton  ########################
class EditIconButton( BaseIconButton ):
    def __init__( self, parent=None ):
        BaseIconButton.__init__( self, QIcon( BASE_IMAGES_DIR + "edit_30x30.png" ), QSize(28, 28), parent )
        self.setToolTip( "Ausgewähltes Element bearbeiten" )

##################### DeleteIconButton  ####################
class DeleteIconButton( BaseIconButton ):
    def __init__( self, parent=None ):
        BaseIconButton.__init__( self, QIcon( BASE_IMAGES_DIR + "delete.png" ), QSize( 28, 28 ), parent )
        self.setToolTip( "Ausgewählte Elemente löschen" )

#################  SortIconButton  #####################
class SortIconButton( BaseIconButton ):
    def __init__( self, parent=None ):
        BaseIconButton.__init__( self, QIcon( BASE_IMAGES_DIR + "sort.png" ), QSize( 28, 28 ), parent )

#################  SettingsIconButton  #####################
class SettingsIconButton( BaseIconButton ):
    def __init__( self, parent=None ):
        BaseIconButton.__init__( self, QIcon( BASE_IMAGES_DIR + "settings.png" ), QSize( 28, 28 ), parent )
        self.setToolTip( "Öffnet den Einstellungen-Dialog" )

#################   BaseGridLayout  #########################
class BaseGridLayout( QGridLayout ):
    def __init__( self ):
        QGridLayout.__init__( self )

    def addPair( self, lbl:str, widget:QWidget, row:int, startCol:int=0, rowspan:int=1, colspan:int=1 ):
        self.addWidget( BaseLabel( lbl ), row, startCol )
        startCol += 1
        self.addWidget( widget, row, startCol, rowspan, colspan )

##################  CalenderDialog   #####################
class CalendarDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__(self, parent)
        self.setModal( True )
        self.setTitle( "Datum auswählen" )
        self._calendar:QCalendarWidget = None
        self._buchungsjahrChangedCallback = None

        self._buttonBox:QtWidgets.QDialogButtonBox = None
        self._callback = None
        self.createCalendar()

    def setTitle( self, title:str ) -> None:
        self.setWindowTitle( title )

    def setCallback( self, cbfnc ):
        self._callback = cbfnc

    def setMinimumDate( self, y:int, m:int, d:int ):
        self._calendar.setMinimumDate( QDate( y, m, d ) )

    def setMaximumDate( self, y:int, m:int, d:int ):
        self._calendar.setMaximumDate( QDate( y, m, d ) )

    def createCalendar(self):
        vbox = QVBoxLayout()
        self._calendar = QCalendarWidget()
        self._calendar.setGridVisible( True )
        self._calendar.setFirstDayOfWeek( Qt.Monday )
        vbox.addWidget( self._calendar )
        self.setLayout(vbox)

        self._buttonBox = QtWidgets.QDialogButtonBox( self )
        self._buttonBox.setOrientation( QtCore.Qt.Horizontal )
        self._buttonBox.setStandardButtons( QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel )
        self._buttonBox.layout().setDirection( QBoxLayout.RightToLeft )
        self._buttonBox.button( QtWidgets.QDialogButtonBox.Ok ).clicked.connect( self._onOk )
        self._buttonBox.button( QtWidgets.QDialogButtonBox.Cancel ).clicked.connect( self._onCancel )
        vbox.addWidget( self._buttonBox )

    def setSelectedDate( self, date:QDate ):
        self._calendar.setSelectedDate( date )

    def setSelectedDateFromString( self, datestring:str ):
        """
        datestring needs to be given as "yyyy-mm-dd" or "dd.mm.yyyy"
        day and month may be given one-digit.
        :param datestring:
        :return:
        """
        parts = datestring.split( "-" )
        if len( parts ) == 0:
            parts = datestring.split( "." )
        else: # yyyy-mm-dd
            dt = QDate( int(parts[0]), int(parts[1]), int(parts[2]) )
            self.setSelectedDate( dt )
        if len( parts ) == 0:
            raise Exception( "CalendarDialog.setSelectedDateFromString: wrong date format '%s'"
                             % (datestring) )
        else: # dd.mm.yyyy
            dt = QDate( int( parts[2] ), int( parts[1] ), int( parts[0] ) )
            self.setSelectedDate( dt )

    def _onOk( self ):
        date:QDate =  self._calendar.selectedDate()
        self.hide()
        if self._callback:
            self._callback( date )

    def _onCancel( self ):
        self.hide()

#########################  SmartDateEdit  #####################################
class SmartDateEdit( QLineEdit ):
    def __init__( self, parent=None ):
        QLineEdit.__init__( self, parent )

    def mouseDoubleClickEvent( self, event ):
        #print( "Double Click SmartDateEdit at pos: ", event.pos() )
        self.showCalendar()

    def setDate( self, year:int, month:int, day:int, format:str="yyyy-MM-dd" ):
        dt = QDate( year, month, day )
        ds = dt.toString( format )
        self.setText( ds )

    def setDateFromIsoString( self, isostring:str ):
        self.setText( isostring )

    def getDate( self ) -> str:
        """
        liefert das eingestellte Datum in dem Format, wie es im Feld zu sehen ist.
        Ist der Wert im Feld ungültig, wird ein Leerstring ("") zurückgegeben.
        :param format:
        :return:
        """
        ds = self.text()
        if ds.endswith( "\n" ): ds = ds[:-1]
        if isValidIsoDatestring( ds ) or isValidEurDatestring( ds ):
            return ds
        else:
            return ""

    def isDateValid( self ) -> bool:
        """
        Prüft, ob der String im Edit-Feld ein gültiges Datum darstellt (True) oder nicht (False).
        Ein leeres Feld gilt als "gültig" (True)
        :return:
        """
        ds = self.text()
        if ds.endswith( "\n" ): ds = ds[:-1]
        if ds == "": return True
        return ( isValidIsoDatestring( ds ) or isValidEurDatestring( ds ) )

    def showCalendar( self ):
        cal = CalendarDialog( self )
        text = self.text()
        d:QDate = None
        if text == "":
            d = getRelativeQDate( 0, 0 )
        else:
            if isValidIsoDatestring( text ):
                d = getQDateFromIsoString( text )

            else:
                d =getRelativeQDate( 0, 0 )
        cal.setSelectedDate( d )
        cal.setCallback( self.onDatumSelected )
        cal.show()

    def onDatumSelected( self, date:QDate ):
        self.setText( date.toString( "yyyy-MM-dd" ) )

###################  AutoWidth  ########################
class AutoWidth:
    def setTextAndAdjustWidth( self, text:str ):
        self.setText( text )
        width = self.getTextWidth( text )
        # font = self.font()
        # # ps = font.pixelSize()  # --> -1
        # font.setPixelSize( 0 )
        # fm = QFontMetrics( font )
        # width = fm.width( text )
        self.setFixedWidth( width + 6 )

    def getTextWidth( self, text:str ) -> int:
        font = self.font()
        # ps = font.pixelSize()  # --> -1
        font.setPixelSize( 0 )
        fm = QFontMetrics( font )
        width = fm.width( text )
        return width

######################  BaseLabel ##################################
class BaseLabel( QLabel, AutoWidth ):
    def __init__( self, text:str="", parent=None ):
        QLabel.__init__( self, parent )
        self.setText( text )

    def setBackground( self, color ):
        # color in der Form "solid white"
        self.setStyleSheet( "background: " + color + ";" )

#########################  BaseCheckBox  #############################
class BaseCheckBox( QCheckBox ):
    def __init__( self, parent = None ):
        QCheckBox.__init__( self, parent )

##########################  BoolSwitch  ################################
class BoolSwitch(QComboBox, AutoWidth):
    """
    Eine ComboBox mit 2 Werten True und False
    """
    def __init__( self, initBool:bool=True ):
        QComboBox.__init__( self )
        self.addItems( (str(True), str(False) ) )
        self.setCurrentText( str( initBool ) )

    def setBool( self, boolVal:bool ):
        self.setCurrentText( str( boolVal ) )

#######################  BaseEdit  ###################################
class BaseEdit( QLineEdit, AutoWidth ):
    key_pressed = Signal( int )
    def __init__( self, parent=None ):
        QLineEdit.__init__( self, parent )
        #self.textChanged.connect( self.on_change )

    def mousePressEvent(self, evt:QMouseEvent):
        self.setSelection( 0, len( self.text() ) )

    # def keyPressEvent( self, event ):
    #     super().keyPressEvent( event )
    #     self.key_pressed.emit( event.key() )

    # def on_change( self, s:str ):
    #     print( s )

    # def setTextAndAdjustWidth( self, text:str ):
    #     self.setText( text )
    #     font = self.font()
    #     # ps = font.pixelSize()  # --> -1
    #     font.setPixelSize( 0 )
    #     fm = QFontMetrics( font )
    #     width = fm.width( text )
    #     self.setFixedWidth( width + 6 )

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

#################################################################


class FixedWidth20Dummy( BaseLabel ):
    def __init__( self, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFixedWidth( 20 )

class FixedWidthDummy( BaseLabel ):
    def __init__( self, w:int, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFixedWidth( w )

class FixedHeightDummy( BaseLabel ):
    def __init__( self, height:int=20, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFixedHeight( height )

class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class VLine(QFrame):
    def __init__(self):
        super( VLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class FontTimesBold12( QFont ):
    def __init__( self ):
        QFont.__init__( self, "Times New Roman", 12, weight=QFont.Bold )

class FontArialBold12( QFont ):
    def __init__( self ):
        QFont.__init__( self, "Arial", 12, weight=QFont.Bold )


class BaseBoldEdit( BaseEdit ):
    def __init__( self, text:str="" ):
        BaseEdit.__init__( self, parent=None )
        if text:
            self.setText( text )
        self.setFont( FontArialBold12() )

class LabelTimes12( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, text, parent )
        self.setFont( QFont( "Times New Roman", 12 ) )
        if text:
            self.setText( text )


class LabelTimesBold12( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, text, parent )
        self.setFont( QFont( "Times New Roman", 12, weight=QFont.Bold ) )
        if text:
            self.setText( text )

class LabelArial12( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, text, parent )
        self.setFont( QFont( "Arial", 12 ) )

class LabelArialBold12( BaseLabel ):
    def __init__( self, text:str="", background:str=None, parent=None ):
        # background in der Form "solid white"
        BaseLabel.__init__( self, text. parent )
        self.setFont( QFont( "Arial", 12, weight=QFont.Bold ) )
        if background:
            self.setBackground( background )

class FatLabel( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, text, parent )
        self._font = QFont( "Arial", 12, weight=QFont.Bold )
        self.setFont( self._font )

class AttributeDialog( QDialog ):
    """
    Mit diesem Dialog können Attribute geändert werden.
    Ein Attribut ist zum Beispiel ein Datenbankwert oder ein Settings-Wert wie Höhe, Breite, Font, etc.
    Je Attribut wird im Dialog eine Zeile verwendet.
    Der Dialog wird mit einer Attributliste List[XAttribute] instanziert und enthält so viele Zeilen,
    wie Attribute in der Attributliste vorhanden sind.
    """
    def __init__( self, attributes:List[XAttribute], title:str= "SettingsDialog" ):
        QDialog.__init__( self )
        self._attributes = attributes
        self._btnOk = QPushButton( text="OK" )
        self._btnCancel = QPushButton( text="Abbrechen" )
        self.setWindowTitle( title )
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        r = 0
        for s in self._attributes:
            lbl = BaseLabel()
            lbl.setText( s.label + ": " )
            l.addWidget( lbl, r, 0 )
            l.addWidget( self._createEditWidget( s.type, s.value ), r, 1 )
            if len( s.options ) > 0:
                combo = QComboBox()
                combo.addItems( s.options )
                l.addWidget( combo, r, 2 )
            r += 1

        dummy = QLabel()
        dummy.setFixedHeight( 3 )
        l.addWidget( dummy, r, 0 )
        r += 1
        self._btnOk.setDefault( True )
        self._btnOk.clicked.connect( self.accept )
        self._btnCancel.clicked.connect( self.reject )
        l.addWidget( self._btnOk, r, 0 )
        l.addWidget( self._btnCancel, r, 1 )

    def _createEditWidget( self, type:str, value ) -> QWidget:
        if type == "int":
            e = IntEdit()
            if value:
                e.setIntValue( value )
            return e
        if type == "float":
            f = FloatEdit()
            if value:
                f.setFloatValue( value )
            return f
        if type == "str":
            e = LineEdit()
            if value:
                e.setText( value )
            return e
        if type == "bool":
            b = BoolSwitch()
            if value:
                b.setBool( value )
            return b
        else:
            raise ValueError( "AttributDialog._createEditWidget(): type " + type + " unbekannt." )


class SearchField( BaseEdit ):
    doSearch = Signal( str )
    searchTextChanged = Signal()

    def __init__( self ):
        BaseEdit.__init__( self )
        self.setMaximumWidth( 200 )
        self.setPlaceholderText( "Suchbegriff" )
        self.returnPressed.connect( self._onReturn )
        self.textChanged.connect( self._onTextChanged )
        self._textChangedAfterReturn = False
        self._backgroundColor = ""

    def _onReturn( self ):
        self._textChangedAfterReturn = False
        text = self.text()
        if len( text ) > 0:
            self.doSearch.emit( text )

    def _onTextChanged( self ):
        if not self._textChangedAfterReturn:
            self.searchTextChanged.emit()
            self._textChangedAfterReturn = True

    def setBackgroundColor( self, htmlColor:str ) -> None:
        if htmlColor != self._backgroundColor:
            self.setStyleSheet( "background-color: " + htmlColor + ";" )
            self._backgroundColor = htmlColor

class SearchWidget( BaseWidget ):
    doSearch = Signal( str )
    searchtextChanged = Signal()
    openSettings = Signal()

    def __init__( self ):
        BaseWidget.__init__( self )
        self._layout = QHBoxLayout()
        self._searchfield = SearchField()
        # forward signals from searchfield:
        self._searchfield.doSearch.connect( self.doSearch.emit )
        self._searchfield.searchTextChanged.connect( self.searchtextChanged.emit )
        self._btnSettings = SettingsIconButton()
        self._btnSettings.clicked.connect( self.openSettings.emit )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        self.setLayout( l )
        l.setContentsMargins( 0, 0, 0, 0 )
        l.addWidget( self._searchfield, alignment=Qt.AlignLeft )
        self._btnSettings.setFixedSize( QSize(25, 25) )
        self._btnSettings.setFlat( True )
        self._btnSettings.setToolTip( "Öffnet den Dialog zum Einstellen der Suchmethodik")
        l.addWidget( self._btnSettings, alignment=Qt.AlignLeft )

    def setSearchFieldBackgroundColor( self, htmlColor:str ) -> None:
        self._searchfield.setBackgroundColor( htmlColor )

    def setFocusToSearchField( self ):
        self._searchfield.setFocus()


##########################  TEST  TEST  TEST  ################################


def testBaseDialogWithButtons3():
    def onClose():
        print( "Close" )
        dlg.accept()

    app = QApplication()
    dlg = BaseDialogWithButtons( "Testdialog", getCloseButtonDefinition( onClose ) )
    dlg.exec_()

def testBaseDialogWithButtons2():
    def onOk( arg ):
        print( "OK: ", arg )
    def onCancel():
        print( "Brich ab" )

    app = QApplication()
    b1def = BaseButtonDefinition( "Na gut", "TT!", onOk, "Heavy Data" )
    b2def = BaseButtonDefinition( "War nix", "TTTTTT", onCancel )
    dlg = BaseDialogWithButtons( "Testdialog", (b1def, b2def) )
    dlg.exec_()

def testBaseDialogWithButtons():
    def onOk():
        print( "OK" )
    def onCancel():
        print( "Cancel" )

    app = QApplication()
    dlg = BaseDialogWithButtons( "Testdialog", getOkCancelButtonDefinitions( onOk, onCancel ) )
    dlg.exec_()
    #app.exec_()


def onSearch( txt ):
    print( "onSearch: ", txt )

def onSearchTextChanged():
    print( "search text changed" )

def onOpenSettings():
    print( "open settings" )

def testSearchWidget():
    app = QApplication()
    sw = SearchWidget()
    sw.doSearch.connect( onSearch )
    sw.searchtextChanged.connect( onSearchTextChanged )
    sw.openSettings.connect( onOpenSettings )
    sw.show()
    app.exec_()



def testSearchField():
    app = QApplication()
    sf = SearchField()
    sf.doSearch.connect( onSearch )
    sf.searchTextChanged.connect( onSearchTextChanged )
    sf.show()
    app.exec_()

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


def createAttributes() -> List[XAttribute]:
    l = list()
    s = XAttribute()
    s.key = "width"
    s.type = int.__name__
    s.label = "Breite"
    s.value = 400

    l.append( s )

    s = XAttribute()
    s.key = "height"
    s.type = int.__name__
    s.label = "Höhe"
    s.value = 300

    l.append( s
              )
    s = XAttribute()
    s.key = "case_sensitiv"
    s.type = bool.__name__
    s.label = "Case Sensitiv"
    s.value = False

    l.append( s )
    return l

def testAttributeDialog():
    app = QApplication()
    dlg = AttributeDialog( createAttributes(), "Einstellungen für die Suche" )
    if dlg.exec_() == QDialog.Accepted:
        print( "accepted" )
    else:
        print( "cancelled" )

    #app.exec_()

def testButtons():
    app = QApplication()
    #btn = BaseButton( "Click Me" )
    btn = NewIconButton()
    #btn = EditIconButton()
    #btn = DeleteIconButton()
    # btn.setText( "Edit")
    # btn.setFixedWidth( 100 )
    btn.show()
    app.exec_()

def test():
    app = QApplication()
    dlg = CheckableAuswahlDialog( ["SB_Kaiser", "ILL_Eich", "NK_Kleist"], title="Freie Auswahl!", checked=True )
    if dlg.exec_() == QDialog.Accepted:
        print( '\n'.join( [str( s ) for s in dlg.choices] ) )
    #app.exec_()

if __name__ == "__main__":
    #test()
    testAuswahlDialog()