from typing import List, Dict
from PySide2.QtWidgets import QMdiSubWindow
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from checkcontroller import MdiChildController, MietenController, HGVController
from business import BusinessLogic
from models import KontrollModel

class MainController:
    def __init__(self, win:ImmoCenterMainWindow ):
        self._mainwin:ImmoCenterMainWindow = win
        win.setActionCallback( self.onMainWindowAction )
        self._mietenCtrl:MietenController = MietenController()
        self._mietenCtrl.changedCallback = self.onViewChanged
        self._mietenCtrl.savedCallback = self.onViewSaved
        self._hgvCtrl:HGVController = HGVController()
        self._viewsandcontroller:[Dict[QMdiSubWindow, MdiChildController]] = {}
        self._someViewChanged:bool = False
        self._x, self._y = 0, 0

    def onMainWindowAction( self, action:MainWindowAction ):
        switcher = {
            MainWindowAction.NEW_WINDOW: self._newWindow,
            MainWindowAction.SAVE_ACTIVE_VIEW: self._saveActiveView,
            MainWindowAction.SAVE_ALL: self._saveAll,
            MainWindowAction.PRINT_ACTIVE_VIEW: self._printActiveView,
            MainWindowAction.OPEN_MIETE_VIEW: self._openMieteView,
            MainWindowAction.OPEN_HGV_VIEW: self._openHGVView
        }
        m = switcher.get( action, lambda: "Nicht unterstützte Action: " + str( action ) )
        m()

    def anyViewChanged( self ) -> bool:
        return self._someViewChanged

    def onViewChanged( self ):
        self._mainwin.setWindowTitle( "ImmoControlCenter *" )
        self._someViewChanged = True

    def onViewSaved( self ):
        self._mainwin.setWindowTitle( "ImmoControlCenter" )
        self._someViewChanged = False

    def _newWindow( self ):
        pass

    def _saveActiveView( self ):
        child = self._mainwin.mdiArea.activeSubWindow()
        ctrl:MdiChildController = self._viewsandcontroller[child]
        ctrl.save()
        self._mainwin.setWindowTitle( "ImmoControlCenter" )
        self._someViewChanged = False

    def _saveAll( self ):
        pass

    def _printActiveView( self ):
        pass

    def _openMieteView( self ):
        subwin = self._mietenCtrl.createSubwindow()
        self._installView( subwin )

    def _openHGVView( self ):
        subwin = self._hgvCtrl.createSubwindow()
        self._installView( subwin )

    def _installView( self, subwin:QMdiSubWindow ):
        self._viewsandcontroller[subwin] = self._mietenCtrl
        self._mainwin.addMdiChild( subwin )
        geom = self._mainwin.geometry()
        subwin.setGeometry( self._x, self._y, 1200, geom.height() / 5 * 4 )
        self._x += 20
        self._y += 20
        subwin.show()

    def _exit( self ):
        pass