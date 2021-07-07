from PyQt5.QtWidgets import QWidget
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QDialog, QPushButton, QGridLayout, QApplication, QHBoxLayout, QLabel


class OkCancelDialog( QDialog ):
    def __init__( self, title=None, parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self._layout = QGridLayout()
        self._okButton = QPushButton( "OK" )
        self._cancelButton = QPushButton( "Abbrechen" )
        self._createGui()
        self._validationFnc = None
        self._cancellationFnc = None

    def _createGui( self ):
        self.setLayout( self._layout )

        hbox = QHBoxLayout()
        #hbox.addStretch( 1 )
        hbox.addWidget( self._okButton )
        hbox.addWidget( self._cancelButton )

        self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft | Qt.AlignBottom )

        self._okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "OkCancelDialog" )

        self._okButton.clicked.connect( self.onAccepted )
        self._cancelButton.clicked.connect( self.onRejected )

    def onAccepted(self):
        rc = True
        if self._validationFnc:
            rc = self._validationFnc()
        if rc:
            self.accept()

    def onRejected( self ):
        rc = True
        if self._cancellationFnc:
            rc = self._cancellationFnc
        if rc:
            self.reject()

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def addWidget( self, w:QWidget, row:int ) -> None:
        if row > 2: raise Exception( "OkCancelDialog.addWidget() -- invalid row index: %d" % ( row ) )
        self._layout.addWidget( w, row, 0 )

    def setValidationFunction( self, fnc ):
        self._validationFnc = fnc

    def setCancellationFunction( self, fnc ):
        self._cancellationFnc = fnc

def testOkCancelDialog():
    app = QApplication()
    dlg = OkCancelDialog()
    dlg.setWindowTitle( "testdialog" )
    dlg.setOkButtonText( "Speichern" )
    lbl = QLabel( "Man beachte diesen erstaunlichen Dialog" )
    dlg.addWidget( lbl, 0 )
    lbl = QLabel( "Did you?" )
    dlg.addWidget( lbl, 2 )
    dlg.show()
    app.exec_()

if __name__ == "__main__":
    testOkCancelDialog()