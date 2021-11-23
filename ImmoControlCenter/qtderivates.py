import numbers
from typing import Any, List, Tuple

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QDate, Qt, QAbstractTableModel, QRect, Signal, QSize
from PySide2.QtGui import QDoubleValidator, QIntValidator, QFont, QGuiApplication, QStandardItemModel, QStandardItem, \
    QMouseEvent, QTextDocument, QIcon, QFontMetrics
from PySide2.QtWidgets import QDialog, QCalendarWidget, QVBoxLayout, QBoxLayout, QLineEdit, QGridLayout, QPushButton, \
    QHBoxLayout, QApplication, QListView, QComboBox, QLabel, QTextEdit, QCheckBox, QFrame

from definitions import ICON_DIR

from datehelper import isValidIsoDatestring, isValidEurDatestring, getRelativeQDate, getQDateFromIsoString

class EditButton( QPushButton ):
    def __init__( self, size:QSize=None, parent=None ):
        QPushButton.__init__( self, parent )
        thissize = size if size else QSize( 28, 28 )
        self.setFixedSize( thissize )
        self.setIcon( QIcon( ICON_DIR + "edit_30x30.png" ) )

##################  CalendarWindow  ###########################
from tableviewext import TableViewExt


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

######################  BaseLabel ##################################
class BaseLabel( QLabel ):
    def __init__( self, parent=None ):
        QLabel.__init__( self, parent )

    def setBackground( self, color ):
        # color in der Form "solid white"
        self.setStyleSheet( "background: " + color + ";" )


#######################  BaseEdit  ###################################
class BaseEdit( QLineEdit ):
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

    def setTextAndAdjustWidth( self, text:str ):
        self.setText( text )
        font = self.font()
        # ps = font.pixelSize()  # --> -1
        font.setPixelSize( 0 )
        fm = QFontMetrics( font )
        width = fm.width( text )
        self.setFixedWidth( width + 6 )

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

################ TableViewDialog ##################
class TableViewDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self._selectedCallback = None

        self._tv = TableViewExt( self )
        self._btnOk = QPushButton( self, text = "Übernehmen zur Bearbeitung" )
        self._btnOk.clicked.connect( self._onOk )
        self._btnClose = QPushButton( self, text="Schließen" )
        self._btnClose.clicked.connect( self._onClose )

        vlayout = QVBoxLayout( self )
        vlayout.addWidget( self._tv )
        hlayout = QHBoxLayout()
        hlayout.addWidget( self._btnOk )
        hlayout.addWidget( self._btnClose )
        vlayout.addLayout( hlayout )

        self.setLayout( vlayout )

    def getTableView( self ) -> TableViewExt:
        return self._tv

    def setSelectedCallback( self, cbfnc ):
        """
        Callback function must accept a list of QModelIndex representing the selected rows/columns
        :param cbfnc:
        :return:
        """
        self._selectedCallback = cbfnc

    def setTableModel( self, model:QAbstractTableModel ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()

    def _onOk( self ):
        if self._selectedCallback:
            sel_list = self._tv.selectedIndexes()
            self._selectedCallback( sel_list )
        self._onClose()

    def _onClose( self ):
        self.close()

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
    def __init__( self, text:str=None ):
        BaseEdit.__init__( self, parent=None )
        if text:
            self.setText( text )
        self.setFont( FontArialBold12() )

class LabelTimes12( BaseLabel ):
    def __init__( self, text:str=None, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFont( QFont( "Times New Roman", 12 ) )
        if text:
            self.setText( text )


class LabelTimesBold12( BaseLabel ):
    def __init__( self, text:str=None, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFont( QFont( "Times New Roman", 12, weight=QFont.Bold ) )
        if text:
            self.setText( text )

class LabelArial12( BaseLabel ):
    def __init__( self, text:str=None, parent=None ):
        BaseLabel.__init__( self, parent )
        self.setFont( QFont( "Arial", 12 ) )
        if text:
            self.setText( text )

class LabelArialBold12( BaseLabel ):
    def __init__( self, text:str=None, background:str=None, parent=None ):
        # background in der Form "solid white"
        BaseLabel.__init__( self, parent )
        self.setFont( QFont( "Arial", 12, weight=QFont.Bold ) )
        if text:
            self.setText( text )
        if background:
            self.setBackground( background )

class FatLabel( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, parent )
        self._font = QFont( "Arial", 12, weight=QFont.Bold )
        self.setFont( self._font )


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
    testAuswahlDialog()