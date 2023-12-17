from functools import cmp_to_key
from typing import List, Any

from PySide2.QtCore import QSize
# from PySide2.QtGui import QScreen
from PySide2.QtWidgets import QDesktopWidget

from controller.infopanelcontroller import InfoPanelController
from generictable_stuff.okcanceldialog import OkDialog
from gui.infopanel import InfoPanel
from gui.mainwindow import MainWindow
from imon.definitions import DEFAULT_PERIOD, DEFAULT_INTERVAL, DEFAULT_INFOPANEL_ORDER
from imon.enums import InfoPanelOrder, Period, Interval
from interface.interfaces import XDepotPosition
from logic.investmonitorlogic import InvestMonitorLogic


class MainController:
    def __init__( self ):
        self._logic: InvestMonitorLogic = InvestMonitorLogic()
        self._mainWin:MainWindow = None
        self._infoPanelCtrlList:List[InfoPanelController] = list()
        self._selectedInfoPanel:InfoPanel = None
        self._sortOrder:InfoPanelOrder = DEFAULT_INFOPANEL_ORDER
        self._sortKeys:List[str] = None
        self._dlgSelected:OkDialog = None

    def createMainWindow( self ) -> MainWindow:
        self._mainWin = MainWindow()
        self._mainWin.setWindowTitle( "Investment-Monitor" )
        self._mainWin.period_interval_changed.connect( self.onPeriodIntervalChanged )
        self._mainWin.getSearchField().doSearch.connect( self.onSearchInfoPanel )
        self._mainWin.getSearchField().searchTextChanged.connect( self.onSearchInfoPanelTextChanged )
        self._mainWin.change_infopanel_order.connect( self.onChangeSortOrder )
        self._mainWin.undock_infopanel.connect( self.onUndock )
        poslist = self._logic.getDepotPositions( DEFAULT_PERIOD, DEFAULT_INTERVAL )
        for xdepotpos in poslist:
            infopanelctrl = InfoPanelController()
            infopanel = infopanelctrl.createInfoPanel( xdepotpos )
            sortfieldInfo = self._setSortKey( xdepotpos, self._sortOrder )
            infopanel.setSortInfo( sortfieldInfo )
            self._mainWin.addInfoPanel( infopanel )
            self._infoPanelCtrlList.append( infopanelctrl )
        rect = QDesktopWidget().screenGeometry()
        w = rect.right() - rect.left()
        h = rect.bottom() - rect.top()
        self._mainWin.resize( QSize( w, h ) )
        return self._mainWin

    def onSearchInfoPanel( self, wknOrIsinOrTicker:str ):
        """
        Sucht anhand wknOrIsinOrTicker das InfoPanel, das diese Depot-Position abbildet,
        bringt es in den sichtbaren Bereich und zeichnet den Namen in fett und rot
        :param wknOrIsinOrTicker:
        :return:
        """
        #print( "MainController.onSearchInfoPanel(). Suche nach ", wknOrIsinOrTicker )
        wknOrIsinOrTicker = wknOrIsinOrTicker.upper()
        if self._selectedInfoPanel:
            self._selectedInfoPanel.setSelected( False )
            self._selectedInfoPanel = None
        for infopanelctrl in self._infoPanelCtrlList:
            infopanel = infopanelctrl.getInfoPanel()
            model = infopanel.getModel()
            if wknOrIsinOrTicker in (model.wkn, model.isin, model.ticker):
                infopanel.setSelected( True )
                self._mainWin.ensureVisible( infopanel )
                self._selectedInfoPanel = infopanel
                break

    def onSearchInfoPanelTextChanged( self ):
        if self._selectedInfoPanel:
            self._selectedInfoPanel.setSelected( False )
            self._selectedInfoPanel = None

    def onUndock( self ):
        infopanels: List[InfoPanel] = [ctrl.getInfoPanel() for ctrl in self._infoPanelCtrlList]
        selected:List[InfoPanel] = [ip for ip in infopanels if ip.isSelected() ]
        if len( selected ) > 0:
            win = MainWindow()
            # vom bisherigen Parent lösen:
            for ip in selected:
                ip.setSelected( False )
                self._mainWin.removeInfoPanel( ip )
                win.addInfoPanel( ip )
            self._mainWin.repaint()
            win.show()

            #dlg = OkDialog( title="Ausgewählte Depotpositionen" )

    def onPeriodIntervalChanged( self, period:Period, interval:Interval ):
        poslist: List[XDepotPosition] = [ctrl.getModel() for ctrl in self._infoPanelCtrlList]
        self._logic.getTickerHistories( poslist, period, interval )
        for ctrl in self._infoPanelCtrlList:
            ctrl.refreshAfterPeriodIntervalHasChanged( period, interval )

    def onChangeSortOrder( self, order:InfoPanelOrder ):
        self._sortOrder = order
        infopanels:List[InfoPanel] = [ctrl.getInfoPanel() for ctrl in self._infoPanelCtrlList]
        ### debug ###
        #testlist = list()
        #############
        for ip in infopanels:
            deppos:XDepotPosition = ip.getModel()
            sortfieldInfo = self._setSortKey( deppos, order )
            ip.setSortInfo( sortfieldInfo )
            ### debug ###
            # sortfield = ip.getModel().__dict__["__sortfield__"]
            # testlist.append( sortfield )
            #############
        ### debug ###
        # testlist = sorted( testlist )
        #############
        try:
            infopanels = sorted( infopanels, key=cmp_to_key( self._compare ) )
        except Exception as ex:
            print( "MainController.onChangeSortOrder(): sorted() throws Exception\n%s" % str(ex) )
            for ip in infopanels:
                model = ip.getModel()
                if not model:
                    print( "found InfoPanel without model." )
                    continue
                try:
                    sortfield = model.__dict__["__sortfield__"]
                    if not sortfield:
                        print( "Sortfield von Model '%s' has no value" % model.wkn )
                        continue
                    print( "Wert Sortfield von Model ", model.wkn, ": ", sortfield )
                except Exception as ex:
                    print( "Model '%s' has no sortfield" % model.wkn )

        self._mainWin.clear()
        for ip in infopanels:
            self._mainWin.addInfoPanel( ip )

    @staticmethod
    def _setSortKey( x:XDepotPosition, order:InfoPanelOrder ) -> str:
        """
        Baut anhand des gewünschten Sortierkriteriums den SortKey auf und
        schiebt ihn <x> als neues Attribut unter.
        :return:
        """
        sortfield = ""
        sortfieldInfo = ""
        if order == InfoPanelOrder.Wkn:
            sortfield = x.wkn.lower()
            sortfieldInfo = "WKN: " + x.wkn
        elif order == InfoPanelOrder.Name:
            sortfield = x.name.lower()
            sortfieldInfo = "Name: " + x.name
        elif order == InfoPanelOrder.Index:
            sortfield = "" if not x.basic_index else x.basic_index.lower()
            sortfieldInfo = "Index: " + x.basic_index
        elif order == InfoPanelOrder.Depot:
            sortfield = x.depot_id + " / " + x.wkn
            sortfieldInfo = "Depot-ID: " + x.depot_id + " / WKN: " + x.wkn
        elif order == InfoPanelOrder.Wert:
            sortfield = str( x.gesamtwert_aktuell )
            sortfieldInfo = "Wert: " + str( x.gesamtwert_aktuell )
        elif order == InfoPanelOrder.AccLast:
            val = "0 / " if not x.flag_acc else "1 / "
            sortfield = val + x.wkn.lower()
            sortfieldInfo = "Acc.: " + ("Nein" if val.startswith("0") else "Ja" ) + " / WKN: " + x.wkn
        elif order == InfoPanelOrder.AccFirst:
            val = "0 / " if x.flag_acc else "1 / "
            sortfield = val + x.wkn.lower()
            sortfieldInfo = "Acc.: " + ("Ja" if x.flag_acc else "Nein" ) + " / WKN: " + x.wkn
        elif order == InfoPanelOrder.DeltaWert:
            # sortfield = '%07.3f' % x.delta_proz
            sortfield = x.delta_proz
            sortfieldInfo = "Wertentwicklg.: " + str( x.delta_proz )
        elif order == InfoPanelOrder.DividendYield:
            val = "0 / " if not x.flag_acc else "1 / "
            sortfield = val + '%07.3f' % x.dividend_yield
            sortfieldInfo = "Dividende: " + str( x.dividend_yield )
        else:
            raise Exception( "MainController._setSortKey(): unknown order:\n%s" % str(order) )
        x.__dict__["__sortfield__"] = sortfield
        return sortfieldInfo

    @staticmethod
    def _compare( ip1:InfoPanel, ip2:InfoPanel ) -> int:
        v1 = ip1.getModel().__dict__["__sortfield__"]
        v2 = ip2.getModel().__dict__["__sortfield__"]
        if v1 == v2: return 0
        else:
            if v1 > v2:  rc = 1
            else: rc = -1
            #print( "_compare: v1=", v1, "; v2=", v2, " -> returning rc=", rc )
            return rc


###############################################################################
def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ctrl = MainController()
    win = ctrl.createMainWindow()
    win.show()
    app.exec_()

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    x = XDepotPosition()
    ctrl = MainController()
    ctrl._setSortKey( x, InfoPanelOrder.Name )
    d = x.__dict__
    for key, value in d.items():
        print( key, ": ", value )
    app.exec_()