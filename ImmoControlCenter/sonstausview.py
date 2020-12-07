from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit
from typing import List, Dict

from treeview import TreeTableModel, TreeView
from tableviewext import TableViewExt

class SonstigeAusgabenView( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._gridLayout = QtWidgets.QGridLayout( self )
        self._gridLayout.setObjectName( "gridLayout" )
        self._cboBuchungsjahr = QtWidgets.QComboBox( self )
        self._gridLayout.addWidget( self._cboBuchungsjahr, 1, 1, 1, 1 )
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
        self._gridLayout.addWidget( self.treeView, 2, 0, 1, 3 )
        self._btnUebernehmen = QtWidgets.QPushButton( self )
        self._btnUebernehmen.setDefault( True )
        self._btnUebernehmen.setText( "Übernehmen" )
        self._gridLayout.addWidget( self._btnUebernehmen, 9, 0, 1, 1 )
        self._btnReset = QtWidgets.QPushButton( self )
        self._btnReset.setText( "Reset" )
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
        self._gridLayout.addWidget( self._bemerkung, 8, 0, 1, 3 )
        self._cboRechnungsjahr = QtWidgets.QComboBox( self )
        self._cboRechnungsjahr.setObjectName( "_cboRechnungsjahr" )
        self._gridLayout.addWidget( self._cboRechnungsjahr, 4, 2, 1, 1 )
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
        self._gridLayout.addWidget( self.tableView, 1, 3, 9, 1 )

    def setJahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr- und die Rechnungsjahr-Combobox
        :param jahre:
        :return:
        """
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
    sav.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()