from PySide2.QtWidgets import QWidget, QApplication

from generictable_stuff.okcanceldialog import OkCancelDialog2
from qtderivates import BaseEdit, BaseGridLayout


class HandwerkerMiniView( QWidget ):
    def __init__(self):
        QWidget.__init__( self )
        self._edName = BaseEdit()
        self._edBranche = BaseEdit()
        self._edAdresse = BaseEdit()
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        r, c = 0, 0
        l.addPair( "Name/Firma: ", self._edName, r, c )
        r += 1
        l.addPair( "Branche: ", self._edBranche, r, c )
        r += 1
        l.addPair( "Ort/Adresse: ", self._edAdresse, r, c )


class HandwerkerMiniDialog( OkCancelDialog2 ):
    """

    """

def test():
    app = QApplication()
    v = HandwerkerMiniView()
    v.setMinimumWidth( 300 )
    v.setWindowTitle( "Erfassung Handwerker")
    v.show()
    app.exec_()