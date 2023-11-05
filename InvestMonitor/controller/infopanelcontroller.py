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
        infopanel.show_details.connect( self.onShowDetails )
        infopanel.update_graph.connect( self.onUpdateGraph )
        infopanel.enter_bestand_delta.connect( self.onEnterBestandDelta )
        infopanel.show_kauf_historie.connect( self.onShowKaufHistorie )
        infopanel.update_kurs.connect( self.onUpdateKurs )
        self._infoPanel = infopanel
        return infopanel

    def getInfoPanel( self ) -> InfoPanel:
        return self._infoPanel

    def onShowDetails( self ):
        print( "onShowDetails" )

    def onUpdateGraph( self, period:Period, interval:Interval ):
        #print( "onUpdateGraph: ", period.value, " / ", interval.value )
        self._logic.updateDepotPositionData( self._x, period, interval )
        self._infoPanel.changeModel( self._x )

    def onEnterBestandDelta( self ):
        print( "onEnterBedrstandElta" )

    def onShowKaufHistorie( self ):
        print( "onShowKaufHistorie" )

    def onUpdateKurs( self ):
        print( "onUpdateKurs" )


def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    logic = InvestMonitorLogic( isTest=False )
    deppos = logic.getDepotPosition( "QDVX.DE", Period.oneYear, Interval.oneWeek )
    ipanel = ipc.createInfoPanel( deppos )
    ipanel.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    ticker = "IEFV.L" #"HMWD.L"
    hist: Series = InvestMonitorLogic.getHistory( ticker, SeriesName.Close )
    log = InvestMonitorLogic( isTest=True )
    poslist = log.getDepotPositions()
    for pos in poslist:
        if pos.ticker == ticker:
            pos.history = hist
            ip = ipc.createInfoPanel( pos )
            ip.show()
    app.exec_()



