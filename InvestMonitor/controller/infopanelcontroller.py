from typing import List

from PySide2.QtCore import QSize
from pandas import Series

from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView
from data.finance.tickerhistory import Period, Interval, SeriesName
from generictable_stuff.okcanceldialog import OkDialog
from gui.infopanel import InfoPanel
from interface.interfaces import XDepotPosition, XDelta
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
        tm:BaseTableModel = self._logic.getOrders( self._x.wkn )
        tv = BaseTableView()
        tv.setModel( tm )
        w = tv.getPreferredWidth()
        h = tv.getPreferredHeight()
        dlg = OkDialog( title="Orderhistorie für WKN '%s', '%s' " % (self._x.wkn, self._x.name) )
        dlg.addWidget( tv, 0 )
        dlg.resize( QSize(w+25, h+25) )
        dlg.exec_()

    def onUpdateKurs( self ):
        print( "onUpdateKurs" )
        self._x.kurs_aktuell, dummy = self._logic.getKursAktuellInEuro( self._x.ticker )
        self._infoPanel.updateKursAktuell( self._x.kurs_aktuell )

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    logic = InvestMonitorLogic( isTest=False )
    deppos = logic.getDepotPosition( "IBCG.DE", Period.oneYear, Interval.oneWeek )
    ipanel = ipc.createInfoPanel( deppos )
    ipanel.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    ticker = "IBCG.DE"  #IEFV.L" #"HMWD.L"
    hist: Series = InvestMonitorLogic.getHistory( ticker, SeriesName.Close )
    log = InvestMonitorLogic( isTest=True )
    poslist = log.getDepotPositions()
    for pos in poslist:
        if pos.ticker == ticker:
            pos.history = hist
            ip = ipc.createInfoPanel( pos )
            ip.show()
    app.exec_()


