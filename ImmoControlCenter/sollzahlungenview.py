from typing import List

from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QApplication, QHBoxLayout, QPushButton, QComboBox

from interfaces import XSollzahlung
from sollzahlungentablemodel import SollzahlungenTableModel
from tableviewext import TableViewExt


class SollzahlungenView( QWidget ):
    """
    Ein View, der zweifach verwendet wird:
    - um die Soll-Mieten anzuzeigen
    - um die Soll-HGV anzuzeigen
    """
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        #self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._mainLayout = QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._btnFilter = QPushButton( self )
        self._btnSave = QPushButton( self )
        self._tvSoll = TableViewExt( self )
        self._editFieldsLayout = QHBoxLayout()
        self._cboMietverhaeltnisse = QComboBox( self )
        #callbacks
        self._saveActionCallback = None
        #TableModel für die anzuzeigenden Zahlungen
        self._tmSoll:SollzahlungenTableModel

        self._createGui()

    def _createGui( self ):
        self._assembleToolbar()
        self._toolbarLayout.addStretch( 50 )
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._mainLayout.addWidget( self._tvSoll, 1, 0, 1, 1 )
        self._assembleEditFields()
        self._mainLayout.addLayout( self._editFieldsLayout, 2, 0, alignment=Qt.AlignLeft )

    def _assembleToolbar( self ):
        btn = self._btnFilter
        btn.setFlat( True )
        btn.setEnabled( True )
        btn.setToolTip( "Alle Sollzahlungen anzeigen (nicht nur aktive)" )
        icon = QIcon( "./images/filter_20x28.png" )
        btn.setIcon( icon )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        self._toolbarLayout.addWidget( btn, stretch=0, alignment=Qt.AlignLeft )

        btn = self._btnSave
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
        self._toolbarLayout.addWidget( btn, stretch=0, alignment=Qt.AlignLeft )

    def _assembleEditFields( self ):
        cbo = self._cboMietverhaeltnisse
        cbo.setPlaceholderText( "Mieter auswählen" )
        self._editFieldsLayout.addWidget( cbo )

    def setSollzahlungen( self, tm:SollzahlungenTableModel ):
        self._tmSoll = tm

    def onSave( self ):
        if self._saveActionCallback:
            self._saveActionCallback()

    def setSaveActionCallback( self, cbfnc ) -> None:
        """
        Die callback-FUnktion braucht keine Parameter empfangen.
        :param cbfnc:
        :return:
        """
        self._saveActionCallback = cbfnc

def test():
    import sys
    app = QApplication( sys.argv )
    v = SollzahlungenView()

    #sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()