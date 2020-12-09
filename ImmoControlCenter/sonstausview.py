from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSize, Qt, QDate
from PySide2.QtGui import QIcon, QDoubleValidator
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit, QCheckBox, QPushButton, QCalendarWidget, \
    QVBoxLayout, QDialog, QBoxLayout
from typing import List, Dict

from treeview import TreeTableModel, TreeView
from tableviewext import TableViewExt
from interfaces import XSonstAus
from servicetreemodel import ServiceTreeModel

##################  CalendarWindow  ###########################
class CalendarDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__(self, parent)
        self.setModal( True )
        self.setWindowTitle( "Datum auswählen" )
        self._calendar:QCalendarWidget = None
        self._buttonBox:QtWidgets.QDialogButtonBox = None
        self._callback = None
        self.createCalendar()

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

    def _onOk( self ):
        date:QDate =  self._calendar.selectedDate()
        self.hide()
        if self._callback:
            self._callback( date )

    def _onCancel( self ):
        self.hide()


#########################  SonstigeAusgabenView  ##############################
class SonstigeAusgabenView( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self._calendarIcon = QIcon( "./images/calendar25x25.png" )
        self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._gridLayout = QtWidgets.QGridLayout( self )
        self._gridLayout.setObjectName( "gridLayout" )

        #### save button
        btn = QPushButton()
        btn.clicked.connect( self.onSave )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen dieser View speichern" )
        icon = QIcon( "./images/save_30.png" )
        btn.setIcon( icon )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        self._gridLayout.addWidget( btn, 0, 0, 1, 1 )
        self._btnSave = btn

        self._cboBuchungsjahr = QtWidgets.QComboBox( self )
        font = QtGui.QFont()
        font.setPointSize( 12 )
        font.setBold( True )
        font.setWeight( 75 )
        self._cboBuchungsjahr.setFont( font )
        self._cboBuchungsjahr.setToolTip(
            "Das hier eingestellte Jahr bestimmt die Rechnungen, die in der Tabelle angezeigt werden." )
        self._cboBuchungsjahr.currentIndexChanged.connect( self._buchungsjahrChanged )
        self._gridLayout.addWidget( self._cboBuchungsjahr, 1, 0, 1, 1 )

        self._ddmmBuchung = QtWidgets.QLineEdit( self )
        self._ddmmBuchung.setToolTip( "Buchungstag und -monat. Tag und Monat mit \',\' oder \'.\' trennen." )
        self._ddmmBuchung.setPlaceholderText( "Buchungstag u. -monat" )
        self._gridLayout.addWidget( self._ddmmBuchung, 1, 1, 1, 1 )

        btn = QPushButton( self )
        btn.setMaximumSize( QSize(25,25) )
        btn.setIcon( self._calendarIcon )
        btn.clicked.connect( self._onShowBuchungCalendar )
        self._gridLayout.addWidget( btn, 1, 2, 1, 1 )
        self._btnCalendarBuchung = btn

        self._tableView = TableViewExt( self )
        sizePolicy = QtWidgets.QSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding )
        sizePolicy.setHorizontalStretch( 1 )
        sizePolicy.setVerticalStretch( 0 )
        self._tableView.setSizePolicy( sizePolicy )
        self._gridLayout.addWidget( self._tableView, 1, 4, 9, 1 )

        self._treeView = TreeView( self )
        self._treeView.setStyleSheet( "gridline-color: rgb(94, 94, 94);" )
        self._treeView.setObjectName( "treeView" )
        self._gridLayout.addWidget( self._treeView, 2, 0, 1, 4 )

        self._kreditor = QtWidgets.QLineEdit( self )
        self._kreditor.setToolTip( "Kreditor: wie im Baum ausgewählt oder freie Eingabe" )
        self._kreditor.setPlaceholderText( "Kreditor" )
        self._gridLayout.addWidget( self._kreditor, 3, 0, 1, 1 )

        self._cboMasterobjekt = QtWidgets.QComboBox( self )
        self._cboMasterobjekt.setEditable( True )
        self._cboMasterobjekt.setToolTip( "Haus: wie im Baum ausgewählt oder freie Eingabe" )
        self._cboMasterobjekt.setPlaceholderText( "Haus" )
        self._gridLayout.addWidget( self._cboMasterobjekt, 3, 1, 1, 1 )

        self._cboMietobjekt = QtWidgets.QComboBox( self )
        self._cboMietobjekt.setEditable( True )
        self._cboMietobjekt.setToolTip( "Wohnung: wie im Baum ausgewählt oder freie Eingabe" )
        self._cboMietobjekt.setPlaceholderText( "Wohnung" )
        self._gridLayout.addWidget( self._cboMietobjekt, 3, 2, 1, 1 )

        self._rgnr = QtWidgets.QLineEdit( self )
        self._rgnr.setPlaceholderText( "Rechnungsnummer" )
        self._gridLayout.addWidget( self._rgnr, 4, 0, 1, 1 )

        self._ddmmRechnung = QtWidgets.QLineEdit( self )
        self._ddmmRechnung.setToolTip( "Rechnungstag und -monat. Tag und Monat mit \',\' oder \'.\' trennen." )
        self._ddmmRechnung.setPlaceholderText( "Rechnungstag u. -monat" )
        self._gridLayout.addWidget( self._ddmmRechnung, 4, 1, 1, 1 )

        #self._cboRechnungsjahr = QtWidgets.QComboBox( self )
        #self._gridLayout.addWidget( self._cboRechnungsjahr, 4, 2, 1, 1 )

        btn = QPushButton( self )
        btn.setMaximumSize( QSize( 25, 25 ) )
        btn.setIcon( self._calendarIcon )
        btn.clicked.connect( self._onShowRechnungCalendar )
        self._gridLayout.addWidget( btn, 4, 2, 1, 1 )
        self._btnCalendarRechnung = btn

        cb = QCheckBox( self )
        cb.setText( "umlegbar" )
        self._gridLayout.addWidget( cb, 5, 0, 1, 1 )
        self._cbUmlegbar = cb

        cb = QCheckBox( self )
        cb.setText( "werterhaltend" )
        self._gridLayout.addWidget( cb, 5, 1, 1, 1 )
        self._cbWerterhaltend = cb

        self._betrag = QtWidgets.QLineEdit( self )
        font = QtGui.QFont()
        font.setPointSize( 11 )
        font.setBold( True )
        font.setWeight( 75 )
        self._betrag.setFont( font )
        self._betrag.setPlaceholderText( "Betrag")
        self._betrag.setAlignment( Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter )
        self._betrag.setValidator( QDoubleValidator( 0, 9999, 2, self ) )
        self._gridLayout.addWidget( self._betrag, 7, 0, 1, 1 )

        self._bemerkung = QtWidgets.QTextEdit( self )
        self._bemerkung.setMaximumSize( QtCore.QSize( 16777215, 50 ) )
        self._bemerkung.setPlaceholderText( "Erläuterungen zur Rechnung oder Abgabe")
        self._gridLayout.addWidget( self._bemerkung, 8, 0, 1, 4 )

        self._btnUebernehmen = QtWidgets.QPushButton( self )
        self._btnUebernehmen.setDefault( True )
        self._btnUebernehmen.setText( "Übernehmen" )
        self._gridLayout.addWidget( self._btnUebernehmen, 9, 0, 1, 1 )

        self._btnReset = QtWidgets.QPushButton( self )
        self._btnReset.setText( "Felder leeren" )
        self._gridLayout.addWidget( self._btnReset, 9, 1, 1, 1 )

        self._buchungsjahrChangedCallback = None
        #self._rechnungsjahrChangedCallback = None

        self._ddmmBuchung.setFocus()

    def onSave( self ):
        pass

    def setBuchungsjahrChangedCallback( self, cbfnc ):
        """
        Die callback-Funktion muss als Argument das neu eingestellte Jahr als integer akzeptieren
        :param cbfnc:
        :return:
        """
        self._buchungsjahrChangedCallback = cbfnc

    def _buchungsjahrChanged( self, newindex ):
        if self._buchungsjahrChangedCallback:
            jahr = int( self._cboBuchungsjahr.currentText() )
            self._buchungsjahrChangedCallback( jahr )

    def _onShowBuchungCalendar( self, event ):
        cal = CalendarDialog( self )
        cal.setCallback( self.onBuchungsdatumSelected )
        cal.show()

    def onBuchungsdatumSelected( self, date:QDate ):
        self._ddmmBuchung.setText( date.toString( "yyyy-MM-dd" ) )


    def _onShowRechnungCalendar( self ):
        cal = CalendarDialog( self )
        cal.setCallback( self.onRechnungsdatumSelected )
        cal.show()

    def onRechnungsdatumSelected( self, date:QDate ):
        self._ddmmRechnung.setText( date.toString( "yyyy-MM-dd" ) )

    def setJahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr- und die Rechnungsjahr-Combobox
        :param jahre:
        :return:
        """
        for jahr in jahre:
            self._cboBuchungsjahr.addItem( str( jahr ) )
            # self._cboRechnungsjahr.addItem( str( jahr ) )

    def setBuchungsjahr( self, jahr:int ) -> None:
        """
        setzt das Jahr, das in der Buchungsjahr-Combobox anzuzeigen ist
        :param jahr:
        :return:
        """
        self._cboBuchungsjahr.setCurrentText( str( jahr ) )

    # def setRechnungsjahr( self, jahr:int ) -> None:
    #     """
    #     setzt das Jahr, das in der Rechnungsjahr-Combobox anzuzeigen ist
    #     :param jahr:
    #     :return:
    #     """
    #     self._cboRechnungsjahr.setCurrentText( str( jahr ) )

    def setServiceTreeModel( self, treemodel:ServiceTreeModel ):
        self._treeView.setModel( treemodel )

def onChangeBuchungsjahr( jahr:int ):
    print( "neues Buchungsjahr: ", str( jahr ) )

def test():
    import sys
    app = QtWidgets.QApplication( sys.argv )
    sav = SonstigeAusgabenView()
    sav.setJahre( (2020,))
    sav.setBuchungsjahr( 2020 )
    # sav.setRechnungsjahr( 2020 )
    sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    sav.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()