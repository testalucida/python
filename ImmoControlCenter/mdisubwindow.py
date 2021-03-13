from PySide2.QtWidgets import QMdiSubWindow


class MdiSubWindow( QMdiSubWindow ):
    def __init__( self ):
        QMdiSubWindow.__init__(self)
        self._quitCallbackList = []

    def addQuitCallback( self, callbackFnc ) -> None:
        """
        callbackFnc muss ein Argument vom Typ MdiSubWindow akzeptieren.
        Das ist ein Pointer auf dieses (zu schließende) Window.
        Außerdem muss callbackFnc einen bool zurückgeben.
        True heißt: kann geschlossen werden, False: nicht schließen.
        """
        self._quitCallbackList.append( callbackFnc )

    def closeEvent( self, event ):
        #print( "closeEvent")
        for cb in self._quitCallbackList:
            if cb( self ) == False:
                event.ignore()

        # if self._quitCallback:
        #     self._quitCallback( self )
        #     event.ignore()
        # else:
        #     event.ignore()