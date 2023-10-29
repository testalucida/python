from typing import List

from PySide2.QtCore import QSize
from PySide2.QtGui import QScreen
from PySide2.QtWidgets import QDesktopWidget

from controller.infopanelcontroller import InfoPanelController
from gui.infopanel import InfoPanel
from gui.mainwindow import MainWindow
from interface.interfaces import XDepotPosition
from logic.investmonitorlogic import InvestMonitorLogic


class MainController:
    def __init__( self ):
        self._logic: InvestMonitorLogic = InvestMonitorLogic()
        self._mainWin:MainWindow = None
        # self._infoPanelList:List[InfoPanel] = list()
        self._infoPanelCtrlList:List[InfoPanelController] = list()
        self._selectedInfoPanel:InfoPanel = None

    def createMainWindow( self ) -> MainWindow:
        self._mainWin = MainWindow()
        self._mainWin.getSearchField().doSearch.connect( self.onSearchInfoPanel )
        self._mainWin.getSearchField().searchTextChanged.connect( self.onSearchInfoPanelTextChanged )
        poslist: List[XDepotPosition] = self._logic.getDepotPositions()
        for xdepotpos in poslist:
            infopanelctrl = InfoPanelController()
            infopanel = infopanelctrl.createInfoPanel( xdepotpos )
            #self._infoPanelList.append( infopanel )
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


def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    ctrl = MainController()
    win = ctrl.createMainWindow()
    win.show()
    app.exec_()