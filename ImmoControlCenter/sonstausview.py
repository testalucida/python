from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit, QPushButton, QCalendarWidget, QVBoxLayout, QDialog
from typing import List, Dict

from treeview import TreeTableModel, TreeView
from tableviewext import TableViewExt

##################  CalendarWindow  ###########################
class CalendarDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__(self, parent)
        self.setModal( True )
        self.setWindowTitle( "Datum auswählen" )
        #self.setWindowFlag( Qt.FramelessWindowHint )
        #self.setGeometry( 0, 0, 400, 300 )
        #self.setIcon()
        self.createCalendar()

    def setIcon(self):
        appIcon = QIcon("icon.png")
        self.setWindowIcon(appIcon)

    def createCalendar(self):
        vbox = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible( True )
        self.calendar.setFirstDayOfWeek( Qt.Monday )
        vbox.addWidget(self.calendar)
        self.setLayout(vbox)

    # def show( self, x:int, y:int ):
    #     #self.setGeometry( x, y, 400, 300 )
    #     super().show()


#########################  SonstigeAusgabenView  ##############################
class SonstigeAusgabenView( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self._calendarIcon = QIcon( "./images/calendar25x25.png" )
        self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._gridLayout = QtWidgets.QGridLayout( self )
        self._gridLayout.setObjectName( "gridLayout" )

        self._cboBuchungsjahr = QtWidgets.QComboBox( self )
        self._gridLayout.addWidget( self._cboBuchungsjahr, 1, 1, 1, 1 )

        btn = QPushButton( self )
        btn.setMaximumSize( QSize(25,25) )
        btn.setIcon( self._calendarIcon )
        btn.clicked.connect( self._onShowBuchungCalendar )
        self._gridLayout.addWidget( btn, 1, 2, 1, 1 )
        self._btnCalendarBuchung = btn

        self._kreditor = QtWidgets.QLineEdit( self )
        self._kreditor.setToolTip( "Kreditor: wie im Baum ausgewählt oder freie Eingabe" )
        self._kreditor.setPlaceholderText( "Kreditor" )
        self._gridLayout.addWidget( self._kreditor, 3, 0, 1, 1 )

        self._betrag = QtWidgets.QLineEdit( self )
        font = QtGui.QFont()
        font.setPointSize( 11 )
        font.setBold( True )
        font.setWeight( 75 )
        self._betrag.setFont( font )
        self._betrag.setPlaceholderText( "Betrag")
        self._gridLayout.addWidget( self._betrag, 7, 0, 1, 1 )

        self.treeView = TreeView( self )
        self.treeView.setStyleSheet( "gridline-color: rgb(94, 94, 94);" )
        self.treeView.setObjectName( "treeView" )
        self._gridLayout.addWidget( self.treeView, 2, 0, 1, 4 )

        self._btnUebernehmen = QtWidgets.QPushButton( self )
        self._btnUebernehmen.setDefault( True )
        self._btnUebernehmen.setText( "Übernehmen" )
        self._gridLayout.addWidget( self._btnUebernehmen, 9, 0, 1, 1 )

        self._btnReset = QtWidgets.QPushButton( self )
        self._btnReset.setText( "Felder leeren" )
        self._gridLayout.addWidget( self._btnReset, 9, 1, 1, 1 )

        self._ddmmBuchung = QtWidgets.QLineEdit( self )
        self._ddmmBuchung.setToolTip( "Buchungstag und -monat. Tag und Monat mit \',\' oder \'.\' trennen." )
        self._ddmmBuchung.setPlaceholderText( "Buchungstag u. -monat" )
        self._gridLayout.addWidget( self._ddmmBuchung, 1, 0, 1, 1 )

        self._cboMietobjekt = QtWidgets.QComboBox( self )
        self._cboMietobjekt.setEditable( True )
        self._cboMietobjekt.setToolTip( "Wohnung: wie im Baum ausgewählt oder freie Eingabe" )
        self._cboMietobjekt.setPlaceholderText( "Wohnung" )
        self._gridLayout.addWidget( self._cboMietobjekt, 3, 2, 1, 1 )

        self._cboMasterobjekt = QtWidgets.QComboBox( self )
        self._cboMasterobjekt.setEditable( True )
        self._cboMasterobjekt.setToolTip( "Haus: wie im Baum ausgewählt oder freie Eingabe" )
        self._cboMasterobjekt.setPlaceholderText( "Haus" )
        self._gridLayout.addWidget( self._cboMasterobjekt, 3, 1, 1, 1 )

        self._bemerkung = QtWidgets.QTextEdit( self )
        self._bemerkung.setMaximumSize( QtCore.QSize( 16777215, 50 ) )
        self._bemerkung.setPlaceholderText( "Erläuterungen zur Rechnung oder Abgabe")
        self._gridLayout.addWidget( self._bemerkung, 8, 0, 1, 4 )

        self._cboRechnungsjahr = QtWidgets.QComboBox( self )
        self._cboRechnungsjahr.setObjectName( "_cboRechnungsjahr" )
        self._gridLayout.addWidget( self._cboRechnungsjahr, 4, 2, 1, 1 )

        btn = QPushButton( self )
        btn.setMaximumSize( QSize( 25, 25 ) )
        btn.setIcon( self._calendarIcon )
        btn.clicked.connect( self._onShowRechnungCalendar )
        self._gridLayout.addWidget( btn, 4, 3, 1, 1 )
        self._btnCalendarRechnung = btn

        self._ddmmRechnung = QtWidgets.QLineEdit( self )
        self._ddmmRechnung.setToolTip( "Rechnungstag und -monat. Tag und Monat mit \',\' oder \'.\' trennen." )
        self._ddmmRechnung.setPlaceholderText( "Rechnungstag u. -monat" )
        self._gridLayout.addWidget( self._ddmmRechnung, 4, 1, 1, 1 )

        self._rgnr = QtWidgets.QLineEdit( self )
        self._rgnr.setPlaceholderText( "Rechnungsnummer" )
        self._gridLayout.addWidget( self._rgnr, 4, 0, 1, 1 )

        self.tableView = TableViewExt( self )
        sizePolicy = QtWidgets.QSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding )
        sizePolicy.setHorizontalStretch( 1 )
        sizePolicy.setVerticalStretch( 0 )
        self.tableView.setSizePolicy( sizePolicy )
        self._gridLayout.addWidget( self.tableView, 1, 4, 9, 1 )

    def _onShowBuchungCalendar( self, event ):
        print( "_onShowBuchungCalendar" )
        cal = CalendarDialog( self )
        # xme = self.x()
        # yme = self.y()
        # x = xme + self._ddmmBuchung.x()
        # y = yme + self._ddmmBuchung.y() + 70
        cal.show()

    def _onShowRechnungCalendar( self ):
        print( "_onShowRechnungCalendar" )

    def setJahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr- und die Rechnungsjahr-Combobox
        :param jahre:
        :return:
        """
        for jahr in jahre:
            self._cboBuchungsjahr.addItem( str( jahr ) )
            self._cboRechnungsjahr.addItem( str( jahr ) )

    def setBuchungsjahr( self, jahr:int ) -> None:
        """
        setzt das Jahr, das in der Buchungsjahr-Combobox anzuzeigen ist
        :param jahr:
        :return:
        """
        self._cboBuchungsjahr.setCurrentText( str( jahr ) )

    def setRechnungsjahr( self, jahr:int ) -> None:
        """
        setzt das Jahr, das in der Rechnungsjahr-Combobox anzuzeigen ist
        :param jahr:
        :return:
        """
        self._cboRechnungsjahr.setCurrentText( str( jahr ) )

def test():
    import sys
    app = QtWidgets.QApplication( sys.argv )
    sav = SonstigeAusgabenView()
    sav.setJahre( (2020,))
    sav.setBuchungsjahr( 2020 )
    sav.setRechnungsjahr( 2020 )
    sav.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()