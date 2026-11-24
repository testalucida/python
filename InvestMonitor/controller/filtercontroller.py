import pickle
from math import ceil
from typing import List, Dict

from PySide6.QtCore import QSize

from base.messagebox import ErrorBox, InfoBox
from controller.infopanelcontroller import InfoPanelController
from gui.filtergui import FilterPanel, FilterAuswahlDialog, FilterResultWindow, AllocReportWindow, AllocTableView
from interface.interfaces import XDepotPosition
from logic.filterlogic import FilterLogic, FilterResultModel, FilterMatch, ReportTableModel


class FilterController:
    """
    Bringt den Dialog mit den Filterkriterien zur Anzeige.
    Nach erfolgter Auswahl wird der Subset-Dialog angezeigt mit den InfoPanels, die
    den Kriterien genügen.
    """
    def __init__( self, depposlist:List[XDepotPosition] ):
        self._depposlist = depposlist
        self._logic = FilterLogic(self._depposlist)
        self._filterPanel = FilterPanel()
        self._filterAuswahlDlg:FilterAuswahlDialog = None
        self._filterResultWindow:FilterResultWindow = None
        self._infoPanelControllerList:List[InfoPanelController] = None
        self._allocReportWindow:AllocReportWindow = None

    def filter( self, whatfilter:str ):
        """
        Steuert den Filtervorgang:
        Zeigt den Dialog zur FilterAuswahl, initiiert die Filterung nach Auswahl der
        Kriterien und zeigt letztlich den Subset-Dialog an mit den InfoPanels, die
        den Filterkriterien entsprechen.
        """
        if whatfilter == "gattunglandsektor":
            self._specifyGattungLandSektorFilter()
        elif whatfilter == "deppos":
            self._specifyDepposFilter()

    def _specifyGattungLandSektorFilter( self ):
        gattungen = self._logic.getGattungen()
        filtergrp = self._filterPanel.addFilterGroup( "Gattungen", "gattung", gattungen, 0, 0 )
        filtergrp.setChecked(0, True)
        laender = self._logic.getLaender()
        self._filterPanel.addFilterGroup( "Länder", "land", laender, 0, 1 )
        sektoren = self._logic.getSektoren()
        filtergrp = self._filterPanel.addFilterGroup( "Sektoren", "sektor", sektoren, 0, 2 )
        filtergrp.setCheckedAll()

        self._doFilter("gattunglandsektor")

    def _doFilter( self, whatfilter:str ):
        self._filterAuswahlDlg = FilterAuswahlDialog()
        self._filterAuswahlDlg.setBeforeAcceptFunction(self.check_selection)
        self._filterAuswahlDlg.okclosed.connect( lambda: self.showResult(whatfilter) )
        self._filterAuswahlDlg.setFilterPanel( self._filterPanel )
        self._filterAuswahlDlg.exec()

    def _specifyDepposFilter( self ):
        deppos_ident_list = self._logic.getDepposIdentList()
        filtergrp = self._filterPanel.addFilterGroup( "Depotpositionen", "deppos", deppos_ident_list, 0, 0 )
        self._doFilter("deppos")

    def check_selection( self ) -> bool:
        #filtergrp = self._filterPanel.getFilterGroup("gattung")
        grps = self._filterPanel.getFilterGroups()
        for grp in grps:
            if not grp.hasCheckedFilters():
                err = ErrorBox("Fehlerhafte Auswahl", "Mindestens 1 Filter in jeder Gruppe muss ausgewählt sein.")
                err.exec_()
                return False
        return True

    def showResult( self, whatfilter:str ):
        """
        Ermittelt die gecheckten FilterCheckBoxes, um damit die passenden XDepotPosition-Objekte zu ermitteln
        """
        di: Dict = self._filterPanel.getCheckedFilters()
        # for k, v in di.items():
        #     print(k, ": ", v)

        if whatfilter == "gattunglandsektor":
            model:FilterResultModel = self._logic.getFilterResult1( di )
        elif whatfilter == "deppos":
            model:FilterResultModel = self._logic.getFilterResult2( di )
        else: raise Exception("Ein Filter namens " + whatfilter + " ist unbekannt." )

        if not model.hasResults():
            box = InfoBox("Filter ohne Ergebnis", "Keine Depotpositionen gefunden, die den gewählten Filtern entsprechen.", "")
            box.exec()
            return

        self._filterResultWindow = FilterResultWindow()
        self._filterResultWindow.setWindowTitle("Filter nach Gattung, Land, Sektor" if whatfilter == "gattunglandsektor"
                                                else "Filter nach Depot-Position")
        self._infoPanelControllerList = list()
        matches = model.getMatches()

        w = h = 0
        for match in matches:
            dp = match.deppos
            infopanelctrl = InfoPanelController()
            self._infoPanelControllerList.append(infopanelctrl)
            infopanel = infopanelctrl.createInfoPanel( dp )
            self._filterResultWindow.addInfoPanel(infopanel)
            size = infopanel.sizeHint()
            w += size.width()
            h = size.height()

        rows = ceil(len(matches) / 3)
        h = h*rows + 50
        self._filterResultWindow.resize( QSize(w, h) )
        self._filterResultWindow.show()
        # Ergebnis tabellarisch darstellen:
        self._presentInTableForm(di, matches)

    def _presentInTableForm( self, checkedFiltersDict:Dict, matches:List[FilterMatch] ):
        """
        Ergebnis summarisch in SumTableModels darstellen:
        Es gibt 2 OkDialoge, der eine enthält die Verdichtung auf Länder (ohne Sektoren),
        der andere die Verdichtung auf Sektoren (ohne Länder).
        Jeder Dialog hat einen ScrollPane als Hauptwidget, jeder ScrollPane enthält
        soviele SumTableModels, wie es Länder bzw. Sektoren gibt.
        """
        def onCloseFilterResultWindow():
            self._allocReportWindow.close()

        self._allocReportWindow = AllocReportWindow()
        self._allocReportWindow.setWindowTitle("Tabellarische Darstellung der selektierten Allokationen")
        self._filterResultWindow.closingWindow.connect(onCloseFilterResultWindow)
        models:List[ReportTableModel] = self._logic.getReportTableModels(checkedFiltersDict, matches)
        row = col = w = 0
        for model in models:
            tv = AllocTableView()
            tv.setModel(model)
            self._allocReportWindow.addAllocTableView(tv, row, col)
            if col == 1:
                row += 1
                col = 0
            else:
                col += 1
        self._allocReportWindow.resizeToFitTables()
        #self._allocReportWindow.resize(QSize(2000,1000))
        self._allocReportWindow.show()



##########################################################################
def test2():
    f = {'gattung': ['ETF'], 'land': ['China'], 'sektor': ['Finanzen']}
    with open( "../controller/depposlist.pickle", "rb" ) as file:
        dplist = pickle.load( file )
    filtered_list = FilterLogic.getFilterResult1( dplist, f )
    print(filtered_list)

def test():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    with open( "../controller/depposlist.pickle", "rb" ) as file:
        dplist = pickle.load( file )
    ctrl = FilterController(dplist)
    ctrl.filter("gattunglandsektor")
    app.exec()

def test3():
    r = ceil(0/3)
    print(r)

def test4():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    win = FilterResultWindow()
    # handler = OnShutDownSignal( win, app )
    # win.installEventFilter(handler)
    win.show()
    app.exec()

if __name__ == "__main__":
    test4()