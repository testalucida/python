from PySide2 import QtWidgets
from PySide2.QtCore import Signal
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QApplication, QComboBox, QDialog, QGridLayout, QPushButton, QLabel, QMessageBox

from qtderivates import SmartDateEdit


class MiniKuendigungDlg( QDialog ):
    kuendigeMietverhaeltnis = Signal( ( str, str) )
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Mietverhältnis beenden" )
        layout = QGridLayout( self )
        font = QFont( "Arial", 14, weight=QFont.Bold )
        # self.label = QtWidgets.QLabel( self )
        # self.label.setText( "Summe:" )
        # layout.addWidget( self.label, 0, 0 )
        r = 0
        lbl = QLabel( self, text="Mieter " )
        layout.addWidget( lbl, r, 0 )

        self._lblName = QLabel( self )
        self._lblName.setFont( font )
        layout.addWidget( self._lblName, r, 1 )

        r += 1
        lbl = QLabel( self, text="kündigen zum" )
        layout.addWidget( lbl, r, 0 )

        self._sdKuenddatum = SmartDateEdit( self )
        self._sdKuenddatum.setFont( font )
        self._sdKuenddatum.setMaximumWidth( 105 )
        layout.addWidget( self._sdKuenddatum, r, 1 )

        r += 1
        self._btnKuendigen = QPushButton( self, text="Kündigen" )
        layout.addWidget( self._btnKuendigen, r, 0 )
        self._btnKuendigen.clicked.connect( self._onKuendige )

        self._btnCancel = QPushButton( self, text="Abbrechen" )
        self._btnCancel.setMaximumWidth( 105 )
        layout.addWidget( self._btnCancel, r, 1 )
        self._btnCancel.clicked.connect( self._onClose )
        self.setLayout( layout )

    def setName( self, name:str ) -> None:
        self._lblName.setText( name )

    def setDatum( self, yyyy:int, mm:int, dd:int ) -> None:
        # setzt ein Kündigungsvorschlagsdatum
        self._sdKuenddatum.setDate( yyyy, mm, dd )

    def _onKuendige( self ):
        if not self._sdKuenddatum.isDateValid():
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle( "Datum ungültig" )
            msgbox.setIcon( QMessageBox.Critical )
            msgbox.setText( "Das eingegebene Datum ist ungültig." )
            msgbox.exec_()
            return
        self.kuendigeMietverhaeltnis.emit( self._lblName.text(), self._sdKuenddatum.getDate() )
        self._onClose()

    def _onClose( self ):
        self.close()

def test():
    app = QApplication()
    win = MiniKuendigungDlg()


    win.show()
    app.exec_()

if __name__ == "__main__":
    test()