from typing import List

from controller.infopanelcontroller import InfoPanelController
from data.finance.tickerhistory import Period, Interval
from gui.infopanel import InfoPanel
from gui.mainwindow import MainWindow
from interface.interfaces import XDepotPosition
from logic.investmonitorlogic import InvestMonitorLogic


class MainController:
    def __init__( self ):
        self._logic: InvestMonitorLogic = InvestMonitorLogic()
        self._mainWin:MainWindow = None

    def createMainWindow( self ) -> MainWindow:
        self._mainWin = MainWindow()
        poslist: List[XDepotPosition] = self._logic.getDepotPositions()
        # todo
        for xdepotpos in poslist:
            infopanelctrl = InfoPanelController()
            infopanel = infopanelctrl.createInfoPanel( xdepotpos )
            self._mainWin.addInfoPanel( infopanel )
        return self._mainWin


def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ctrl = MainController()
    win = ctrl.createMainWindow()
    win.show()
    app.exec_()