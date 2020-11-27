from typing import List, Dict
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from checkcontroller import MietenController, HGVController
from business import BusinessLogic
from models import KontrollModel

class MainController:
    def __init__(self, win:ImmoCenterMainWindow ):
        self._mainwin:ImmoCenterMainWindow = win
        win.setActionCallback( self.onMainWindowAction )
        self._mietenCtrl:MietenController = MietenController()
        self._hgvCtrl:HGVController = HGVController()

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

    def _newWindow( self ):
        pass

    def _saveActiveView( self ):
        pass

    def _saveAll( self ):
        pass

    def _printActiveView( self ):
        pass

    def _openMieteView( self ):
        subwin = self._mietenCtrl.createSubwindow()
        mainsize = self._mainwin.size()
        subsize = subwin.size()

        self._mainwin.addMdiChild( subwin )
        #subwin.resize( 900, subsize.height() )
        #geom = subwin.geometry()
        #subwin.setGeometry( geom.x(), geom.y(), 900, 500 )

    def _openHGVView( self ):
        pass

    def _exit( self ):
        pass