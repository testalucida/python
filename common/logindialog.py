from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QApplication, \
    QLineEdit, QMessageBox, QDialog, QSizePolicy


class LoginDialog( QDialog ):
    ok_pressed = Signal()
    cancel_pressed = Signal()
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setWindowTitle( "Login" )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self.setLayout( self._mainLayout )
        # self._mainLayout.setVerticalSpacing( 0 )
        # self._mainLayout.setHorizontalSpacing( 0 )
        self._edUser = QLineEdit()
        self._edPwd = QLineEdit()
        self._edPwd.setEchoMode( QLineEdit.Password )
        self._btnOk = QPushButton( text="OK" )
        self._btnOk.pressed.connect( self.ok_pressed.emit )
        self._btnCancel = QPushButton( text="Cancel" )
        self._btnCancel.pressed.connect( self.cancel_pressed.emit )
        self._createGui()
        self._edUser.setFocus()

    def _createGui( self ):
        l = self._mainLayout
        r, c = 0, 0
        l.addWidget( QLabel( "User: " ), r, c )
        c = 1
        l.addWidget( self._edUser, r, c )
        r, c = 1, 0
        l.addWidget( QLabel( "Password: " ), r, c )
        c = 1
        l.addWidget( self._edPwd, r, c )
        r, c = 2, 0
        l.addWidget( self._btnOk, r, c )
        c = 1
        l.addWidget( self._btnCancel, r, c )
        # r, c = 3, 0
        # dummy = QWidget()
        # dummy.setSizePolicy( QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred )
        # l.addWidget( dummy, r, c, 1, 2 )
        #self.setSizePolicy( QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum )
        self.setFixedSize( QSize(250, 100 ) )

    def getUser( self ):
        return self._edUser.text()

    def getPwd( self ):
        return self._edPwd.text()


def test():
    def onOk():
        user = dlg.getUser()
        pwd = dlg.getPwd()
        if "" in (user, pwd):
            print( "You loser failed." )
            # box = QMessageBox()
            # box.setWindowTitle( "Login failed" )
            # box.setText( "You loser failed." )
            # box.exec_()
        else:
            dlg.close()
        print( user )
        print( pwd )

    def onCancel():
        dlg.reject()

    app = QApplication()
    dlg = LoginDialog()
    dlg.ok_pressed.connect( onOk )
    dlg.cancel_pressed.connect( onCancel )
    dlg.exec_()
    # dlg.show()
    # app.exec_()

if __name__ == '__main__':
    test()