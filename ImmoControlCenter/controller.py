from typing import List, Dict
from mainwindow import MainWindow
from business import BusinessLogic
from models import KontrollModel

class Controller:
    def __init__(self, win:MainWindow, businessLogic:BusinessLogic):
        self._mainwin:MainWindow = win
        self._busilogic:BusinessLogic = businessLogic

    def startWork(self):
        self._busilogic.prepare()
        view = self._mainwin.getView()
        kontrollzeitraum = self._mainwin.getKontrollzeitraum()
        if view == "Mieten":
            rowlist = self._busilogic.getMietzahlungen( kontrollzeitraum["jahr"] )
            for r in rowlist:
                r["ok"] = ""
                r["nok"] = ""
            model = KontrollModel( self._mainwin, rowlist, kontrollzeitraum["monat"] )
            self._mainwin.setMieteModel( model )
        return
