from typing import List, Dict
from mainwindow import MainWindow
from business import BusinessLogic
from models import KontrollModel

class Controller:
    def __init__(self, win:MainWindow ):
        self._mainwin:MainWindow = win
        self._busilogic:BusinessLogic = BusinessLogic()
        try:
            self._busilogic.prepare()
        except Exception as x:
            win.showException( x )
        d = win.getKontrollzeitraum()
        self._currentYear:int = 0
        self._currentSicht = "Mieten"
        win.setZeitraumChangedCallback( self.zeitraumChangedCallback )
        win.doZeitraumChangedCallback() #start work

    def zeitraumChangedCallback( self, jahr:int, monat: int ):
        if self._currentYear == 0: self._currentYear = jahr
        else:
            if jahr == self._currentYear: return

        sicht = self._mainwin.getSicht()
        if sicht == "Mieten":
            if not self._busilogic.existsEinAusArt( "miete", jahr ):
                self._busilogic.createMtlEinAusJahresSet( "miete", jahr )
            rowlist = self._busilogic.getMietzahlungen( jahr )
            if len(rowlist) == 0:
                self._mainwin.showException( "Zum gewählten Jahr sind keine Daten vorhanden.",
                                             'Daten sind für das aktuelle Jahr und für max. zwei zurückliegende Jahre vorhanden.' )
                return

            for r in rowlist:
                r["ok"] = ""
                r["nok"] = ""
            model = KontrollModel( self._mainwin, rowlist, monat )
            self._mainwin.setMieteModel( model )
        self._currentYear = jahr
        return