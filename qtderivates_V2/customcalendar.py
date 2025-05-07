import datehelper
from qt_imports import *

######################  CalendarDialog ##################################

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
        if datehelper.isValidIsoDatestring( ds ) or datehelper.isValidEurDatestring( ds ):
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
        return ( datehelper.isValidIsoDatestring( ds ) or datehelper.isValidEurDatestring( ds ) )

    def showCalendar( self ):
        cal = CalendarDialog( self )
        text = self.text()
        d:QDate = None
        if text == "":
            d = datehelper.getRelativeQDate( 0, 0 )
        else:
            if datehelper.isValidIsoDatestring( text ):
                d = datehelper.getQDateFromIsoString( text )

            else:
                d = datehelper.getRelativeQDate( 0, 0 )
        cal.setSelectedDate( d )
        cal.setCallback( self.onDatumSelected )
        cal.show()

    def onDatumSelected( self, date:QDate ):
        self.setText( date.toString( "yyyy-MM-dd" ) )