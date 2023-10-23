from PySide2.QtWidgets import QMainWindow, QScrollArea


class AllInfoPanelsScrollArea( QScrollArea ):
    def __init__(self):
        QScrollArea.__init__( self )

class MainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self._panelsScroll = AllInfoPanelsScrollArea()
        self.setCentralWidget( self._panelsScroll )