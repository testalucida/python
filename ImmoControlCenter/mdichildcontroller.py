from abc import ABC, abstractmethod
from PySide2.QtWidgets import QWidget
from mdisubwindow import MdiSubWindow

class MdiChildController( ABC ):
    def __init__( self ):
        self._subwin:MdiSubWindow = None

    @abstractmethod
    def save( self ):
        pass

    def createSubwindow( self ) -> MdiSubWindow:
        view = self.createView()
        self._subwin = MdiSubWindow()
        self._subwin.addQuitCallback( self.onCloseSubWindow )
        self._subwin.setWidget( view )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )
        return self._subwin

    @abstractmethod
    def createView( self ) -> QWidget:
        pass

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def onCloseSubWindow( self, window: MdiSubWindow ) -> bool:
        pass