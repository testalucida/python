from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QApplication, QComboBox


class MietverhaeltnisView( QWidget ):
    def __init__(self):
        QWidget.__init__( self )
        self.setWindowTitle( "Monatswerte" )
        self._gridLayout:QtWidgets.QGridLayout = QtWidgets.QGridLayout( self )
        self._cboMietverhaeltnisse = QComboBox( self )
        self._createUI()

    def _createUI(self):
        lay = self._gridLayout
        lay.setContentsMargins(3, 3, 3, 3)
        self._cboMietverhaeltnisse.setPlaceholderText( "Mieter auswählen" )
        lay.addWidget( self._cboMietverhaeltnisse, 0, 0 )

def test():
    app = QApplication()
    win = MietverhaeltnisView()


    win.show()
    app.exec_()

if __name__ == "__main__":
    test()