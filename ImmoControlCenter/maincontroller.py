from typing import List, Dict
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from business import BusinessLogic
from models import KontrollModel

class MainController:
    def __init__(self, win:ImmoCenterMainWindow ):
        self._mainwin:ImmoCenterMainWindow = win
        win.setActionCallback( self.onMainWindowAction )

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
        print( "openMieteView" )

    def _openHGVView( self ):
        pass

    def _exit( self ):
        pass

    # def zeitraumChangedCallback( self, jahr:int, monat: int ):
    #     if self._currentYear == 0: self._currentYear = jahr
    #     else:
    #         if jahr == self._currentYear: return
    #
    #     sicht = self._mainwin.getSicht()
    #     if sicht == "Mieten":
    #         if not self._busilogic.existsEinAusArt( "miete", jahr ):
    #             self._busilogic.createMtlEinAusJahresSet( "miete", jahr )
    #         rowlist = self._busilogic.getMietzahlungen( jahr )
    #         if len(rowlist) == 0:
    #             self._mainwin.showException( "Zum gewählten Jahr sind keine Daten vorhanden.",
    #                                          'Daten sind für das aktuelle Jahr und für max. zwei zurückliegende Jahre vorhanden.' )
    #             return
    #
    #         for r in rowlist:
    #             r["ok"] = ""
    #             r["nok"] = ""
    #         model = KontrollModel( self._mainwin, rowlist, monat )
    #         self._mainwin.setMieteModel( model )
    #     self._currentYear = jahr
    #     return