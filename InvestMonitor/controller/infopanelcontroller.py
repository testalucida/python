from typing import List

from PySide2.QtCore import QSize
from pandas import Series

from base.baseqtderivates import BaseEdit, MultiLineEdit
from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView
from base.dynamicattributeui import DynamicAttributeView, DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from data.finance.tickerhistory import Period, Interval, SeriesName
from generictable_stuff.okcanceldialog import OkDialog
from gui.infopanel import InfoPanel
from interface.interfaces import XDepotPosition, XDelta, XDetail
from logic.investmonitorlogic import InvestMonitorLogic


class InfoPanelController:
    def __init__( self ):
        self._x:XDepotPosition = None
        self._logic:InvestMonitorLogic = InvestMonitorLogic()
        self._infoPanel:InfoPanel = None
        self._detailDlg:DynamicAttributeDialog = None

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
        details:XDetail = self._logic.getDetails( self._x )
        detailsUI = XBaseUI( details )
        vislist = (
            VisibleAttribute( "basic_index", BaseEdit, "Index: ", editable=False, nextRow=True ),
            VisibleAttribute( "beschreibung", MultiLineEdit, "", editable=False, nextRow=True ),
            VisibleAttribute( "bank", BaseEdit, "Bank: ", editable=False, nextRow=True ),
            VisibleAttribute( "depot_nr", BaseEdit, "Depot-Nr.: ", editable=False, nextRow=True ),
            VisibleAttribute( "depot_vrrkto", BaseEdit, "Vrr.-Konto: ", editable=False, nextRow=True )
        )
        detailsUI.addVisibleAttributes( vislist )
        self._detailDlg = DynamicAttributeDialog( detailsUI, title="Details zur Depotposition '%s'" % self._x.name,
                                                  okButton=False, applyButton=False )
        self._detailDlg.show()

    def onUpdateGraph( self, period:Period, interval:Interval ):
        #print( "onUpdateGraph: ", period.value, " / ", interval.value )
        self._logic.updateWertpapierData( self._x, period, interval )
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
        dlg.resize( QSize(w+25, h+35) )
        dlg.exec_()

    def onUpdateKurs( self ):
        self._logic.updateKursAndDivYield( self._x )
        self._infoPanel.updateKursAktuell( self._x.kurs_aktuell, self._x.dividend_yield )

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    logic = InvestMonitorLogic()
    deppos = logic.getDepotPosition( "HMWD.L", Period.oneYear, Interval.oneWeek )
    ipanel = ipc.createInfoPanel( deppos )
    ipanel.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    ticker = "IBCG.DE"  #IEFV.L" #"HMWD.L"
    hist: Series = InvestMonitorLogic.getHistory( ticker, SeriesName.Close )
    log = InvestMonitorLogic( )
    poslist = log.getDepotPositions()
    for pos in poslist:
        if pos.ticker == ticker:
            pos.history = hist
            ip = ipc.createInfoPanel( pos )
            ip.show()
    app.exec_()



