from PySide6.QtWidgets import QMainWindow, QMenuBar, QApplication

from generictable_stuff.okcanceldialog import OkDialog
from gui.infopanel import InfoPanel
from gui.mainwindow import AllInfoPanelsScrollArea


class SubsetDialog( OkDialog ):
    def __init__( self ):
        OkDialog.__init__(self, title="Den Filterkriterien entsprechende Depot-Positionen")
        self._panelsScroll = AllInfoPanelsScrollArea()
        self.addWidget( self._panelsScroll, 1 )

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._panelsScroll.addInfoPanel( infopanel )

def test():
    app = QApplication()
    dlg = SubsetDialog()
    dlg.show()
    app.exec()

if __name__ == "__main__":
    test()