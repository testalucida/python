from enum import Enum

from PyQt5.QtWidgets import QWidget
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QDialog, QPushButton, QGridLayout, QApplication, QHBoxLayout, QLabel, QMessageBox

class CloseType( Enum ):
    OK_CLOSE = 1,
    OK_KEEP_OPEN = 2,
    CANCEL = 3,
    X = 4  # X in Schließebox

class OkCancelDialog2( QDialog ):
    """
    Alle Versuche, den Dialog zu schließen (OK, OK and keep open, Cancel, Schließebox) münden in einen Aufruf der
    Methode mayClose( CloseType ).
    Um das gewünschte Verhalten des Dialogs zu erzielen, muss diese Methode überschrieben oder umgeleitet werden.
    """
    def __init__( self, title=None, showOkKeepOpenButton:bool=False, parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self._showOkKeepOpenButton = showOkKeepOpenButton
        self._layout = QGridLayout()
        self._okButton = QPushButton( "OK" )
        self._okAndKeepOpenButton = None
        self._cancelButton = QPushButton( "Abbrechen" )
        self._createGui()
        self.closeEvent = self._closeUsingXBox

    def _createGui( self ):
        self.setLayout( self._layout )

        hbox = QHBoxLayout()
        #hbox.addStretch( 1 )
        hbox.addWidget( self._okButton )
        if self._showOkKeepOpenButton:
            self._okAndKeepOpenButton = QPushButton( "Übernehmen" )
            hbox.addWidget( self._okAndKeepOpenButton )
        hbox.addWidget( self._cancelButton )

        self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft | Qt.AlignBottom )

        self._okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "OkCancelDialog" )

        self._okButton.clicked.connect( self._onOkClicked )
        if self._okAndKeepOpenButton:
            self._okAndKeepOpenButton.clicked.connect( self._onOkAndKeepOpenClicked )
        self._cancelButton.clicked.connect( self._onCancelClicked )

    def _closeUsingXBox( self, event ):
        if not self.mayClose( CloseType.X ):
            event.ignore()

    def _onOkClicked( self ):
        if self.mayClose( CloseType.OK_CLOSE ):
            self.accept()

    def _onCancelClicked( self ):
        if self.mayClose( CloseType.CANCEL ):
            self.reject()

    def _onOkAndKeepOpenClicked( self ):
        if self.mayClose( CloseType.OK_KEEP_OPEN ):
            pass

    def mayClose( self, closeType:CloseType ) -> bool:
        """
        Überschreibe diese Methode oder leite sie um, um das gewünschte Verhalten zu erzielen
        Wenn der CloseType OK_KEEP_OPEN ist, bleibt der Dialog auf jeden Fall offen, egal ob die überschriebene
        (umgeleitete) Methode True oder False zurückgibt.
        :param closeType:
        :return:
        """
        return True

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def setCancelButtonText( self, text:str ):
        self._cancelButton.setText( text )

    def setOkAndKeepOpenButtonText( self, text:str ):
        if not self._okAndKeepOpenButton:
            raise Exception( "OkCancelDialog.setOkAndKeepOpenButtonText(..) called but button is not installed.\n"
                             "Did you set showOkKeepOpenButton to True when instantiating OkCancelDialog?")
        self._okAndKeepOpenButton.setText( text )

    def addLayout( self, layout, row:int, alignment=Qt.AlignLeft ):
        """
        Fügt der gewünschten Zeile in Spalte 0 ein Layout hinzu.
        :param layout:
        :param row:
        :return:
        """
        self._layout.addLayout( layout, row, 0, alignment=alignment )

    def addWidget( self, w:QWidget, row:int ) -> None:
        if row > 2: raise Exception( "OkCancelDialog.addWidget() -- invalid row index: %d" % ( row ) )
        self._layout.addWidget( w, row, 0 )

    def showErrorMessage( self, title:str, msg:str ):
        mb = QMessageBox( QMessageBox.Critical, title, msg )
        mb.exec_()

###################################################################

class OkCancelDialog( QDialog ):
    def __init__( self, title=None, showOkKeepOpenButton:bool=False, parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self._showOkKeepOpenButton = showOkKeepOpenButton
        self._layout = QGridLayout()
        self._okButton = QPushButton( "OK" )
        self._okAndKeepOpenButton = None
        self._cancelButton = QPushButton( "Abbrechen" )
        self._createGui()
        self._validationFnc = None
        self._cancellationFnc = None
        self.closeEvent = self._onClose # Schließebox X gedrückt

    def _createGui( self ):
        self.setLayout( self._layout )

        hbox = QHBoxLayout()
        #hbox.addStretch( 1 )
        hbox.addWidget( self._okButton )
        if self._showOkKeepOpenButton:
            self._okAndKeepOpenButton = QPushButton( "Übernehmen" )
            hbox.addWidget( self._okAndKeepOpenButton )
        hbox.addWidget( self._cancelButton )

        self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft | Qt.AlignBottom )

        self._okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "OkCancelDialog" )

        self._okButton.clicked.connect( self.onAccepted )
        if self._okAndKeepOpenButton:
            self._okAndKeepOpenButton.clicked.connect( self.onOkAndKeepOpenClicked )
        self._cancelButton.clicked.connect( self.onRejected )

    def _onClose( self, event ):
        self.onRejected()

    def onOkAndKeepOpenClicked( self ):
        self._validationFnc()

    def onAccepted(self):
        ok = True
        if self._validationFnc:
            ok = self._validationFnc()
        if ok:
            self.accept()

    def onRejected( self ):
        rc = True
        if self._cancellationFnc:
            rc = self._cancellationFnc()
        if rc:
            self.reject()

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def setCancelButtonText( self, text:str ):
        self._cancelButton.setText( text )

    def setOkAndKeepOpenButtonText( self, text:str ):
        if not self._okAndKeepOpenButton:
            raise Exception( "OkCancelDialog.setOkAndKeepOpenButtonText(..) called but button is not installed.\n"
                             "Did you set showOkKeepOpenButton to True when instantiating OkCancelDialog?")
        self._okAndKeepOpenButton.setText( text )

    def addLayout( self, layout, row:int, alignment=Qt.AlignLeft ):
        """
        Fügt der gewünschten Zeile in Spalte 0 ein Layout hinzu.
        :param layout:
        :param row:
        :return:
        """
        self._layout.addLayout( layout, row, 0, alignment=alignment )

    def addWidget( self, w:QWidget, row:int ) -> None:
        if row > 2: raise Exception( "OkCancelDialog.addWidget() -- invalid row index: %d" % ( row ) )
        self._layout.addWidget( w, row, 0 )

    def setValidationFunction( self, fnc ):
        self._validationFnc = fnc

    def setCancellationFunction( self, fnc ):
        self._cancellationFnc = fnc

    def showErrorMessage( self, title:str, msg:str ):
        mb = QMessageBox( QMessageBox.Critical, title, msg )
        mb.exec_()

def cancellationFunc():
    print( "on cancellation")
    return False

def onMayClose( closeType:CloseType ) -> bool:
    print( "Slot onMayClose", " closeType = ", closeType )
    if closeType == CloseType.OK_CLOSE: return True
    if closeType == CloseType.OK_KEEP_OPEN: return False
    if closeType == CloseType.CANCEL: return True
    if closeType == CloseType.X:
        print( "Mit dem X!!" )
        return True

def testOkCancelDialog2():
    app = QApplication()
    dlg = OkCancelDialog2( showOkKeepOpenButton=True )
    dlg.mayClose = onMayClose
    dlg.setWindowTitle( "testdialog" )
    dlg.setOkButtonText( "Speichern" )
    lbl = QLabel( "Man beachte diesen erstaunlichen Dialog" )
    dlg.addWidget( lbl, 0 )
    lbl = QLabel( "Did you?" )
    dlg.addWidget( lbl, 2 )
    dlg.show()
    app.exec_()

def testOkCancelDialog():
    app = QApplication()
    dlg = OkCancelDialog()
    dlg.setWindowTitle( "testdialog" )
    dlg.setOkButtonText( "Speichern" )
    dlg.setCancellationFunction( cancellationFunc )
    lbl = QLabel( "Man beachte diesen erstaunlichen Dialog" )
    dlg.addWidget( lbl, 0 )
    lbl = QLabel( "Did you?" )
    dlg.addWidget( lbl, 2 )
    dlg.show()
    app.exec_()

if __name__ == "__main__":
    testOkCancelDialog2()