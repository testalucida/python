import copy
import pickle
from math import ceil
from typing import Any, List, Dict

import PySide6
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QMainWindow, QVBoxLayout, QSpacerItem, QSizePolicy

from base.baseqtderivates import BaseGridLayout, BaseCheckBox, BaseWidget, BaseLabel
from base.basetablemodel import SumTableModel
from base.messagebox import ErrorBox, InfoBox
from controller.infopanelcontroller import InfoPanelController
from data.db.investmonitordata import InvestMonitorData
from generictable_stuff.okcanceldialog import OkCancelDialog
from gui.infopanel import InfoPanel
from gui.mainwindow import AllInfoPanelsScrollArea
from imon.enums import FilterSpec, Land, Sektor
from interface.interfaces import XWpGattung, XDepotPosition, XAllocation


##########################################################################
class FilterMatch:
    def __init__( self ):
        self.deppos: XDepotPosition = None
        self.allokationen:List[XAllocation] = list()

    def addAllokation( self, allok_typ, allok_name, allok_prozent ):
        allok = XAllocation()
        allok.typ = allok_typ
        allok.name = allok_name
        allok.prozent = allok_prozent
        self.allokationen.append(allok)

##########################################################################
class FilterResultModel:
    def __init__( self ):
        self._matchList:List[FilterMatch] = list()

    def addMatch( self, dp:XDepotPosition, allok_typ:str=None, allok_name:str=None, allok_prozent=None ):
        for match in self._matchList:
            if match.deppos == dp:
                match.addAllokation(allok_typ, allok_name, allok_prozent)
                return
        # dp ist noch nicht in der Match-Liste enthalten, neuen Match anlegen
        match = FilterMatch()
        match.deppos = dp
        match.addAllokation( allok_typ, allok_name, allok_prozent )

        self._matchList.append(match)

    def removeMatches( self, dp:XDepotPosition ):
        self._matchList = [match for match in self._matchList if match.deppos != dp]

    def hasResults( self ) -> bool:
        return len(self._matchList) > 0

    def getDepotpositionen( self ) -> List[XDepotPosition]:
        """
        liefert alle Depotpositionen dieses FilterResultModels - also das Ergebnis eines Filtervorgangs.
        """
        return [match.deppos for match in self._matchList]

    def getMatches( self ) -> List[FilterMatch]:
        """
        liefert alle Matches dieses FilterResultModels - also das Ergebnis eines Filtervorgangs.
        """
        return self._matchList

##########################################################################
class FilterLogic:
    def __init__(self, depposlist:List[XDepotPosition]):
        self._db = InvestMonitorData()
        self._depposlist:List[XDepotPosition] = depposlist
        self._identSeparator = " ("

    def getGattungen( self ) -> List[str]:
        gattungen:List[XWpGattung] = self._db.getGattungen()
        return [g.gattung for g in gattungen]

    def getLaender( self ) -> List[str]:
        laender:List[str] = self._db.getLaender()
        return laender

    def getSektoren( self ) -> List[str]:
        sektoren:List[str] = self._db.getSektoren()
        return sektoren

    def getDepposIdentList( self ) -> List[str]:
        deppos_ident_list = list()
        for deppos in self._depposlist:
            deppos_ident = deppos.wkn + self._identSeparator + deppos.isin + "): " + deppos.name
            deppos_ident_list.append( deppos_ident )
        return sorted( deppos_ident_list )

    def getFilterResult1( self, dic: Dict ) -> FilterResultModel:
        """
        Liefert eine Liste von Depotpositionen, die den Filterkriterien entsprechen
        @param dic: Die vom Anwender gesetzten Filter.
                    Keys: gattung, land, sektor
        """
        model = FilterResultModel()
        for dp in self._depposlist:
            if not dp.gattung in dic["gattung"]:
                # dp.gattung: einer von (ETF, Anleihe, ...)
                continue
            if len( dp.allokationen ) == 0:
                continue
            allokationen = list()
            for allok in dp.allokationen:
                if allok.typ != "Firma":
                    allokcp = copy.deepcopy(allok)
                    allokcp.typ = allok.typ.lower()
                    allokationen.append( allokcp )
            allokationen = sorted( allokationen, key=lambda x: x.typ )
            typmemo = allokationen[0].typ
            nmatches = 0
            for allok in allokationen:
                # allok vom Typ XAllokation.
                # allok.typ *einer* von (Land, Sektor)
                # allok.name *einer* von ("USA", "Frankreich", ...)
                if allok.typ != typmemo:
                    # Gruppenwechsel
                    if nmatches == 0:
                        # die Namen (z.B. "USA", "China", "Italien") des Allokationstyp (z.B. "land") vor dem Grp.wechsel
                        # passen zu keinem gecheckten Filter (z.B. "Japan", "Frankreich"), dp verwerfen
                        model.removeMatches( dp )
                        break
                    nmatches = 0
                    typmemo = allok.typ
                if allok.name in dic[allok.typ]:
                    model.addMatch( dp, allok.typ, allok.name, allok.prozent )
                    nmatches += 1
            if nmatches == 0:
                # der gruppenletzte Allok.typ wird von keinem Filter erfasst
                model.removeMatches(dp)
        return model

    def getFilterResult2( self, deppos_ident_dic:Dict ) -> FilterResultModel:
        """
        Liefert ein FilterResultModel, die den Filterkriterien entsprechen
        @param deppos_ident_dict: Die vom Anwender gesetzten Filter in einem Dictionary.
                                  Key = "deppos", Value ist eine Liste mit Strings - bestehend aus WKN und Name -, die die gewünschten
                                  Depotpositionen identifizieren.
                                  Der Dictionary hat also genau 1 Key-Eintrag.
        """
        model = FilterResultModel()
        dp_ident_list = list(deppos_ident_dic.values())[0]
        for dp in self._depposlist:
            for dp_ident in dp_ident_list:
                reslist = dp_ident.split(self._identSeparator)
                wkn = reslist[0]
                if wkn == dp.wkn:
                    model.addMatch(dp)
                    break
        return model

#########################################################################
class FilterCheckBox(BaseCheckBox):
    # filterStateChanged = Signal( str, bool )

    def __init__( self, label:str, isChecked = False):
        """
        @param label: Text, der auf der GUI neben der CheckBox angezeigt wird
        @param isChecked: ob der Anfangsstatus gecheckt sein soll oder nicht
        Es darf nur ENTWEDER land ODER sektor angegeben werden
        """
        BaseCheckBox.__init__(self)
        self.setChecked(isChecked)
        self.setText(label)
        #self.stateChanged.connect(self.onFilterSpecChanged)

    # def onFilterSpecChanged( self, state ):
    #     #print("onFilterSpecChanged: ", state)
    #     isChecked = state == Qt.CheckState.Checked.value
    #     self.filterStateChanged.emit( self.text(), isChecked )


# class WknCheckBox(FilterCheckBox):
#     def __init__( self, text:str, wkn:str, isChecked:bool=False ):
#         FilterCheckBox.__init__(self, text, isChecked)
#         self._wkn = wkn

########################################################################

########################################################################
class FilterGroup( QFrame ):
    """
    Ein Widget, das *eine Spalte (Liste)* auswählbarer Filterkriterien
    einer bestimmten Filtergruppe (FilterSpec) enthält.
    Jedes Kriterium wird durch eine FilterCheckBox dargestellt.
    Außerdem kann eine Überschrift über die Gruppe von Filterkriterien platziert werden.
    Jede Änderung einer FilterCheckBox führt zu einem filterSpecChanged-Signal.
    """
    #filterSpecChanged = Signal(str, str, bool)
    """
        str: Identifikation dieser Gruppe (z.B. "land")
        str: Das Label, das bei der Instanzierung der betätigten FilterCheckBox übergeben wurde (z.B. "Singapur")
        bool: isChecked oder nicht
    """
    def __init__(self, caption:str, ident:str, labellist:List[str]):
        QFrame.__init__( self )
        self._caption = caption
        self._ident = ident
        self._labellist = labellist
        self._layout = QVBoxLayout() #BaseGridLayout()
        self.setLayout(self._layout)
        #self._r = 0
        self._cbList:List[FilterCheckBox] = list()
        self._createGui()
        self._borderthickness = "2px"
        self._bordercolor = "blue"
        self._borderstyle = "FilterGroup {border: " + self._borderthickness + " solid " + self._bordercolor + "; }"
        self.setStyleSheet( self._borderstyle )

    def _createGui( self ):
        l = self._layout
        lbl = BaseLabel(self._caption)
        font = lbl.font()
        font.setBold(True)
        lbl.setFont(font)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setTextAndBackgroundColor( "black", "lightgray")
        lbl.setFixedHeight(22)
        ####l.addWidget(lbl, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop )
        l.addWidget(lbl, stretch=0, alignment=Qt.AlignmentFlag.AlignTop )
        #self._r += 1
        l.addSpacerItem(QSpacerItem(1, 16))

        cb = FilterCheckBox("Alle wählen/abwählen")
        cb.checkStateChanged.connect(self.onCheckAll)
        #####l.addWidget( cb, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop )
        l.addWidget(cb, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        l.addSpacerItem( QSpacerItem( 1, 16 ) )
        #self._r += 1

        for label in self._labellist:
            cb = FilterCheckBox(label)
            self._cbList.append(cb)
            #cb.filterStateChanged.connect( self.onFilterSpecChanged )
            ####l.addWidget(cb, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
            l.addWidget(cb, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
            #self._r += 1

        l.addStretch()

    def getIdent( self ) -> str:
        return self._ident

    def setChecked( self, idx:int, val:bool ):
        self._cbList[idx].setChecked(val)

    def setCheckedAll( self, checked=True ):
        for cb in self._cbList:
            cb.setChecked(checked)

    def hasCheckedFilters( self ) -> bool:
        for cb in self._cbList:
            if cb.isChecked():
                return True
        return False

    def getCheckedFilters( self ) -> (str, List[str]):
        checked_items = list()
        for cb in self._cbList:
            if cb.isChecked():
                checked_items.append(cb.text())
        return self._ident, checked_items

    def onCheckAll( self, state ):
        checked = False
        if state == Qt.CheckState.Checked:
            checked = True
        for cb in self._cbList:
            cb.setChecked(checked)



##########################################################################
class FilterPanel(BaseWidget):
    """
    Ein Widget, das ein oder mehrere FilterGroups enthält.
    """
    def __init__( self ):
        BaseWidget.__init__(self)
        #QFrame.__init__(self)
        self._filterGroups:List[FilterGroup] = list()
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )

    def addFilterGroup( self, caption:str, ident:str, labellist:List[str], row:int, col:int ) -> FilterGroup:
        filtergrp = FilterGroup(caption, ident, labellist)
        self._filterGroups.append(filtergrp)
        self._layout.addWidget(filtergrp, row, col)
        return filtergrp

    def getFilterGroup( self, ident:str ) -> FilterGroup:
        for fg in self._filterGroups:
            if fg.getIdent() == ident:
                return fg
        raise Exception("Keine Filtergruppe mit ident " + ident + " gefunden.")

    def getFilterGroups( self ) -> List[FilterGroup]:
        return self._filterGroups

    def getCheckedFilters( self ) -> Dict:
        di = dict()
        for filtergrp in self._filterGroups:
            ident, checked_items = filtergrp.getCheckedFilters()
            di[ident] = checked_items
        return di

##########################################################################
class FilterAuswahlDialog( OkCancelDialog ):
    def __init__(self):
        OkCancelDialog.__init__(self, "Auswahl der Filterkriterien")
        self._filterPanel = None

    def setFilterPanel( self, filterPanel:FilterPanel ):
        self._filterPanel = filterPanel
        self.addWidget(filterPanel, 0)
        self.resize( self.sizeHint() )


##########################################################################
class FilterResultWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self._panelsScroll = AllInfoPanelsScrollArea()
        self.setCentralWidget(self._panelsScroll)

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._panelsScroll.addInfoPanel( infopanel )

    # def getPreferredSize( self ) -> QSize:
    #     size = self._panelsScroll.sizeHint()
    #     return size

##########################################################################
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
            print("size: ", size)
            w += size.width()
            h = size.height()

        rows = ceil(len(matches) / 3)
        h = h*rows + 50
        self._filterResultWindow.resize( QSize(w, h) )
        self._filterResultWindow.show()


##########################################################################
def test2():
    l = list()
    d1 = dict()
    d1["gattung"] = ["Anleihe", "ETF"]
    l.append( d1 )

    d2 = dict()
    d2["land"] = ["Frankreich", "USA", "Italien"]
    l.append( d2 )

    d3 = dict()
    d3["sektor"] = ["Energie", "Finanzen"]
    l.append( d3 )

    print( l )

    for e in l:
        for key, value in e.items():
            print( key, ": ", value )


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

if __name__ == "__main__":
    test()