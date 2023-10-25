from typing import List

from pandas import Series

from data.finance.tickerhistory import Period, Interval, SeriesName
from gui.infopanel import InfoPanel
from interface.interfaces import XDepotPosition
from logic.investmonitorlogic import InvestMonitorLogic


class InfoPanelController:
    def __init__( self ):
        self._x:XDepotPosition = None
        self._logic:InvestMonitorLogic = InvestMonitorLogic()
        self._infoPanel:InfoPanel = None

    def createInfoPanel( self, xdepotpos:XDepotPosition ) -> InfoPanel:
        self._x = xdepotpos
        infopanel = InfoPanel()
        infopanel.setModel( xdepotpos )
        infopanel.period_changed.connect( self.onPeriodChanged )
        infopanel.interval_changed.connect( self.onIntervalChanged )
        self._infoPanel = infopanel
        return infopanel

    def onPeriodChanged( self, period:Period ):
        print( "onPeriodChanged: ", period.value )

    def onIntervalChanged( self, interval:Interval ):
        print( "onIntervalChanged: ", interval.value )

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    hist: Series = InvestMonitorLogic.getHistory( "WTEM.DE", SeriesName.Close )
    log = InvestMonitorLogic()
    poslist = log.getDepotPositions()
    for pos in poslist:
        if pos.ticker == "WTEM.DE":
            pos.history = hist
            ip = ipc.createInfoPanel( pos )
            ip.show()
    app.exec_()



