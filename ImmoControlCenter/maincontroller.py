from typing import List, Dict, Tuple
from mdisubwindow import MdiSubWindow
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from checkcontroller import MdiChildController, MietenController, HGVController
from sonstauscontroller import SonstAusController

class MainController:
    def __init__(self, win:ImmoCenterMainWindow ):
        self._mainwin:ImmoCenterMainWindow = win
        win.setActionCallback( self.onMainWindowAction )

        self._mietenCtrl:MietenController = MietenController()
        self._mietenCtrl.changedCallback = self.onViewChanged
        self._mietenCtrl.savedCallback = self.onViewSaved

        self._hgvCtrl:HGVController = HGVController()
        self._hgvCtrl.changedCallback = self.onViewChanged
        self._hgvCtrl.savedCallback = self.onViewSaved

        self._sonstAusCtrl:SonstAusController = SonstAusController()
        self._sonstAusCtrl.changedCallback = self.onViewChanged
        self._sonstAusCtrl.savedCallback = self.onViewSaved

        self._nChanges = 0  # zählt die Änderungen, damit nach Speichern-Vorgängen das Sternchen nicht zu früh entfernt wird.

        #TODO: _viewsandcontroller bereinigen, wenn ein View geschlossen wird
        self._viewsandcontroller:[Dict[MdiSubWindow, MdiChildController]] = {}
        self._someViewChanged:bool = False
        self._x, self._y = 0, 0

    def showStartViews( self ):
        self.showMieteView()
        self.showHGVView()
        self.showSonstAusView()

    def onMainWindowAction( self, action:MainWindowAction ):
        switcher = {
            MainWindowAction.NEW_WINDOW: self._newWindow,
            MainWindowAction.SAVE_ACTIVE_VIEW: self._saveActiveView,
            MainWindowAction.SAVE_ALL: self._saveAll,
            MainWindowAction.PRINT_ACTIVE_VIEW: self._printActiveView,
            MainWindowAction.OPEN_MIETE_VIEW: self.showMieteView,
            MainWindowAction.OPEN_HGV_VIEW: self.showHGVView
        }
        m = switcher.get( action, lambda: "Nicht unterstützte Action: " + str( action ) )
        m()

    def anyViewChanged( self ) -> bool:
        return self._someViewChanged

    def onViewChanged( self ):
        self._mainwin.setWindowTitle( "ImmoControlCenter *" )
        self._someViewChanged = True
        self._nChanges += 1

    def onViewSaved( self ):
        self._nChanges -= 1
        if self._nChanges == 0:
            self._mainwin.setWindowTitle( "ImmoControlCenter" )
            self._someViewChanged = False

    def arrange( self, *views ):
        print( views )

    def _newWindow( self ):
        pass

    def _saveActiveView( self ):
        child:MdiSubWindow = self._mainwin.mdiArea.activeSubWindow()
        #child.installEventFilter( self )
        ctrl:MdiChildController = self._viewsandcontroller[child]
        ctrl.save()
        self._mainwin.setWindowTitle( "ImmoControlCenter" )
        self._someViewChanged = False

    def _saveAll( self ):
        pass

    def _printActiveView( self ):
        pass

    def showMieteView( self ):
        #TODO prüfen, ob schon ein MieteView vorhanden ist. Wenn ja, diesen in den Vordergrund bringen.
        #     Nur wenn nein, einen anlegen.
        # if <exists miete view:
        #     bring to front
        # else:
        self.createMieteViewAndShow()

    def createMieteViewAndShow( self ):
        subwin = self._mietenCtrl.createSubwindow()
        self._installView( subwin, self._mietenCtrl )
        w, h = self.getMainWindowSize()
        w2 = w/2
        subwin.setGeometry( 0, 0, w2, h-22 )
        # self._x += 20
        # self._y += 20
        subwin.show()

    def showHGVView( self ):
        # TODO prüfen, ob schon ein HGV-View vorhanden ist. Wenn ja, diesen in den Vordergrund bringen.
        #     Nur wenn nein, einen anlegen.
        # if <exists hgv view:
        #     bring to front
        # else:
        self.createHgvViewAndShow()

    def createHgvViewAndShow( self ):
        subwin = self._hgvCtrl.createSubwindow()
        self._installView( subwin, self._hgvCtrl )
        w, h = self.getMainWindowSize()
        w2 = w/2
        x = w2
        subwin.setGeometry( x, 0, w2, h/2 )
        self._x += 20
        self._y += 20
        subwin.show()

    # def createHgvViewAndShow( self ):
    #     subwin = self._hgvCtrl.createSubwindow()
    #     self._installView( subwin, self._hgvCtrl )
    #     w, h = self.getMainWindowSize()
    #     w2 = w / 2
    #     x = w2
    #     subwin.setGeometry( x, 0, w2, h / 2 )
    #     self._x += 20
    #     self._y += 20
    #     subwin.show()

    def showSonstAusView( self ):
        self.createSonstAusViewAndShow()

    def createSonstAusViewAndShow( self ):
        subwin = self._sonstAusCtrl.createSubwindow()
        self._installView( subwin, self._sonstAusCtrl )
        w, h = self.getMainWindowSize()
        w2 = w / 2
        x = w2
        hgvsubwin = self.getView( self._hgvCtrl )
        y = h - hgvsubwin.height()
        h2 = h - y - 25
        subwin.setGeometry( x, y, w2, h2 )
        subwin.show()

    def _installView( self, subwin:MdiSubWindow, ctrl:MdiChildController ):
        #subwin.addQuitCallback( self.onCloseSubWindow )
        self._viewsandcontroller[subwin] = ctrl
        self._mainwin.addMdiChild( subwin )

    def getMainWindowSize( self ) -> Tuple:
        geom = self._mainwin.mdiArea.geometry()
        return geom.width(), geom.height()

    def getView( self, ctrl:MdiChildController ) -> MdiSubWindow:
        for w, c in self._viewsandcontroller.items():
            if c == ctrl:
                return w
        raise Exception( "internal error: can't find MdiSubWindow for Controller " + ctrl.getViewTitle() )

    # def showSubWindow( self, subwin:MdiSubWindow, x:int, y:int, w:int, h:int ):
    #     subwin.setGeometry( self._x, self._y, 1200, geom.height() / 5 * 4 )
    #     self._x += 20
    #     self._y += 20
    #     subwin.show()

    def onCloseSubWindow( self, window:MdiSubWindow ) -> bool:
        self._viewsandcontroller.pop( window )
        return True

    def _exit( self ):
        pass

