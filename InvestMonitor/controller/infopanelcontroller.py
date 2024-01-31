from typing import List

from PySide2.QtCore import QSize, QObject, Signal
from PySide2.QtWidgets import QDialog
from pandas import Series

import datehelper
from base.baseqtderivates import BaseEdit, MultiLineEdit, SmartDateEdit, IntEdit, FloatEdit, SignedNumEdit, \
    PositiveSignedFloatEdit
from base.basetablemodel import BaseTableModel, SumTableModel
from base.basetableview import BaseTableView
from base.dynamicattributeui import DynamicAttributeView, DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from base.messagebox import ErrorBox, InfoBox
from data.finance.tickerhistory import Period, Interval, SeriesName
from generictable_stuff.okcanceldialog import OkDialog, OkCancelDialog
from gui.infopanel import InfoPanel
from interface.interfaces import XDepotPosition, XDelta, XDetail
from logic.investmonitorlogic import InvestMonitorLogic


class InfoPanelController( QObject ):
    order_inserted = Signal( int ) # parameter: Ordersumme (pos. oder neg.)

    def __init__( self ):
        QObject.__init__( self )
        self._x:XDepotPosition = None
        self._logic:InvestMonitorLogic = InvestMonitorLogic()
        self._infoPanel:InfoPanel = None
        self._detailDlg:DynamicAttributeDialog = None

    def createInfoPanel( self, xdepotpos:XDepotPosition ) -> InfoPanel:
        self._x = xdepotpos
        infopanel = InfoPanel()
        infopanel.setModel( xdepotpos )
        infopanel.show_details.connect( self.onShowDetails )
        infopanel.show_div_payments.connect( self.onShowDividendPayments )
        infopanel.show_simul_yield.connect( self.onShowSimulatedDividendYield )
        infopanel.update_graph.connect( self.onUpdateGraph )
        infopanel.enter_bestand_delta.connect( self.onEnterBestandDelta )
        infopanel.show_kauf_historie.connect( self.onShowKaufHistorie )
        infopanel.update_kurs.connect( self.onUpdateKurs )
        self._infoPanel = infopanel
        return infopanel

    def getInfoPanel( self ) -> InfoPanel:
        return self._infoPanel

    def getModel( self ) -> XDepotPosition:
        return self._x

    def onShowDetails( self ):
        details:XDetail = self._logic.getDetails( self._x )
        detailsUI = XBaseUI( details )
        vislist = (
            VisibleAttribute( "basic_index", BaseEdit, "Index: ", editable=False, nextRow=True ),
            VisibleAttribute( "beschreibung", MultiLineEdit, "", editable=False, nextRow=True ),
            VisibleAttribute( "toplaender", BaseEdit, "Top-Länder: ", editable=False, nextRow=True ),
            VisibleAttribute( "topsektoren", BaseEdit, "Top-Sektoren: ", editable=False, nextRow=True ),
            VisibleAttribute( "topfirmen", MultiLineEdit, "Top-Firmen: ", widgetHeight=60, editable=False, nextRow=True ),
            VisibleAttribute( "bank", BaseEdit, "Bank: ", editable=False, nextRow=True ),
            VisibleAttribute( "depot_nr", BaseEdit, "Depot-Nr.: ", editable=False, nextRow=True ),
            VisibleAttribute( "depot_vrrkto", BaseEdit, "Vrr.-Konto: ", editable=False, nextRow=True )
        )
        detailsUI.addVisibleAttributes( vislist )
        self._detailDlg = DynamicAttributeDialog( detailsUI, title="Details zur Depotposition '%s'" % self._x.name,
                                                  okButton=False, applyButton=False )
        self._detailDlg.resize( QSize(500, 500) )
        self._detailDlg.show()

    def onShowDividendPayments( self ):
        divs:Series = self._x.dividends
        tm = SumTableModel.fromSeries( divs, indexLen=10, jahr=0, colsToSum=("value",) )
        tm.setKeyHeaderMappings2( ("index", "value"), ("Datum", "Dividende") )
        tv = BaseTableView()
        tv.setModel( tm )
        tv.setAlternatingRowColors( True )
        dlg = OkCancelDialog( title="Dividendenzahlungen " + self._x.wkn )
        dlg.addWidget( tv, 0 )
        dlg.exec_()

    def onShowSimulatedDividendYield( self ):
        """
        Öffnet ein Infofenster, in dem die theoretische Dividendenrendite auf Basis des aktuellen Kurses und des Durchschnitts der
        Dividendenzahlungen in der eingestellten Periode angezeigt wird.
        :return: None
        """
        divyield:float = self._logic.getSimulatedDividendYield( self._x.kurs_aktuell, self._x.dividends )
        box = InfoBox( title="Theoretische Rendite " + self._x.wkn,
                       info="Auf Basis in der Vergangenheit (eingestellte Periode) gezahlter Dividenden "
                            "und des aktuellen Kurses\nergibt sich für das kommende Jahr rechnerisch eine Rendite von",
                       more=str(divyield) + "%" )
        box.exec_()

    def onUpdateGraph( self, period:Period, interval:Interval ):
        self._logic.updateWertpapierData( self._x, period, interval )
        self._infoPanel.changeModel( self._x )

    def refreshAfterPeriodIntervalHasChanged( self, period:Period, interval:Interval ):
        self._infoPanel.changeModel( self._x )
        self._infoPanel.setPeriodAndInterval( period, interval )

    def onEnterBestandDelta( self ):
        def validateDeltaData() -> str or None:
            view:DynamicAttributeView = deltaDlg.getDynamicAttributeView()
            w:SmartDateEdit = view.getWidget( "delta_datum" )
            if not datehelper.isValidIsoDatestring( w.getDate() ):
                return "Orderdatum muss mit gültigem ISO-Datum versorgt sein. "
            w:PositiveSignedFloatEdit = view.getWidget( "delta_stck" )
            if w.getValue() ==0:
                return "Stückzahl darf nicht 0 sein."
            # if view.getWidget( "order_summe" ).getValue() <= 0:
            if view.getWidget( "preis_stck" ).getValue() <= 0:
                return "Der Kurs muss immer positiv sein.\nDie Erkennung Kauf/Verkauf erfolgt über das " \
                       "Vorzeichen der Stückzahl (+ -> Kauf, - -> Verkauf)."

        delta = XDelta()
        delta.wkn = self._x.wkn
        delta.delta_datum = datehelper.getCurrentDateIso()
        deltaUI = XBaseUI( delta )
        vislist = (
            VisibleAttribute( "wkn", BaseEdit, "WKN: ", widgetWidth=100, editable=False, nextRow=True ),
            VisibleAttribute( "delta_datum", SmartDateEdit, "Order ausgeführt am: ", widgetWidth=100, editable=True,
                              nextRow=True ),
            VisibleAttribute( "delta_stck", PositiveSignedFloatEdit, "Anzahl Stück: ", widgetWidth=100,
                              tooltip="Bei Kauf Vorzeichen '+' verwenden, bei Verkauf '-'",
                              editable=True, nextRow=True ),
            VisibleAttribute( "preis_stck", FloatEdit, "Kurs (€): ", widgetWidth=100,
                              tooltip="Kurs, zu dem gekauft/verkauft wurde",
                              editable=True, nextRow=True ),
            # VisibleAttribute( "order_summe", FloatEdit, "Kauf-/Verkaufspreis (€): ", widgetWidth=100,
            #                   tooltip="Ordersumme inkl. Nebenkosten.\nVorzeichen muss immer '+' sein,\n"
            #                           "die Erkennung ob Kauf oder Verkauf erfolgt über das Vorzeichen der Stückzahl",
            #                   editable=True, nextRow=True ),
            VisibleAttribute( "bemerkung", MultiLineEdit, "Bemerkung: ", editable=True, widgetHeight=50, nextRow=True ),
        )
        deltaUI.addVisibleAttributes( vislist )
        deltaDlg = DynamicAttributeDialog( deltaUI, title="Orderdaten '%s'" % self._x.name,
                                                  okButton=True, applyButton=False )
        deltaDlg.setCallbacks( beforeAcceptCallback=validateDeltaData )
        if deltaDlg.exec_() == QDialog.Accepted:
            deltaDlg.getDynamicAttributeView().updateData()
            try:
                self._logic.insertOrderAndUpdateDepotData( delta, self._x )
                self._infoPanel.updateOrderRelatedData()
                self.order_inserted.emit( delta.order_summe )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Insert in die Datenbank", str( ex ) )
                box.exec_()

    def updateAnteilAnSummeGesamtwerte( self, anteil:int ):
        """
        Nach einer eingetragenen Order ändert sich der Anteil dieser DepotPosition an der Gesamtheit.
        Die DepotPosition muss geändert werden, danach die Anzeige aktualisiert werden.
        :return:
        """
        self._x.anteil_an_summe_gesamtwerte = anteil
        self._infoPanel.updateAnteilAnSummeGesamtwerte()

    def onShowKaufHistorie( self ):
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

    def isInfoPanelSelected( self ) -> bool:
        return self._infoPanel.isSelected()

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    logic = InvestMonitorLogic()
    ticker = "IEDY.L"
    deppos = logic.getDepotPosition( ticker, Period.twoYears, Interval.oneWeek )
    ipanel = ipc.createInfoPanel( deppos )
    ipanel.show()
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ipc = InfoPanelController()
    ticker = "DBXS.DE" # "IEDY.L" #"H4ZJ.DE" #"XSMI.SW" #"EUNY.DE" # "IEDY.L"  #IEFV.L" #"HMWD.L"
    #hist: Series = InvestMonitorLogic.getHistory( ticker, SeriesName.Close )
    log = InvestMonitorLogic( )
    pos:XDepotPosition = log.getDepotPosition( ticker )
    ip = ipc.createInfoPanel( pos )
    ip.show()
    app.exec_()



