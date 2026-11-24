import copy
from typing import List, Dict

from base.basetablemodel import SumTableModel
from data.db.investmonitordata import InvestMonitorData
from imon.enums import AllocTyp
from interface.interfaces import XDepotPosition, XWpGattung, XAllocation, XAllocReport
from logic.imonlogic import ImonLogic


class ReportTableModel(SumTableModel):
    def __init__( self, allocTyp:AllocTyp, allocReportList:List[XAllocReport] ):
        SumTableModel.__init__(self, allocReportList, jahr=None, colsToSum=["wert",])
        self.setKeyHeaderMappings2( ("gattung", "alloc_name", "wkn", "deppos_name", "prozent", "wert", "delta_kurs"),
                                    ("Gattung", allocTyp.value, "WKN", "Name", "Wert(%) im WP", "Wert(€) im Bestand", "Δ Kurs 2 Wo.(%)" ) )
        self._allocTyp = allocTyp

##########################################################################
class FilterMatch:
    def __init__( self, deppos:XDepotPosition ):
        self.deppos: XDepotPosition = deppos
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
        match = FilterMatch(dp)
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

    def getReportTableModels( self, checkedFiltersDict:Dict, matches:List[FilterMatch] ) -> List[ReportTableModel]:
        """
        Erzeugt aus <checkedFiltersDict> und <matches> eine Liste von XAllocReport-Objekten, mit denen eine Liste von
        ReportTableModel-Objekten erzeugt wird.
        Eine Zeile des ReportTableModels hat folgenden Aufbau:
        Gattung | Land od. Sektor | WKN | WP-Name | Anteil d. Allok. | Wert d. Position | Delta Kurs 14 Tg
        Näheres siehe unterhalb dere Parameter-Erklärungen.
        @param allocTyp: Ein Wert von AllocTyp: "Land" oder "Sektor". Er bestimmt, ob nach Länder-  oder Sektoren-
                        Allokation ausgewertet wird und wird für die Überschrift der zweiten Spalte verwendet ("Land"
                        oder "Sektor").
                         verwendet.
        @param checkedFiltersDict: ein Dictionary mit den Keys "gattung", "land", "sektor".
                        Die Values sind Listen mit den entsprechenden Werten, z.B. ['ETF'] (key=gattung),
                        ['Australien', 'Brasilien', 'China'] (key=land) oder
                        ['Basiskonsumgüter', 'Cash', 'Energie', 'Finanzen', 'Gesundheit'] (key=sektor)
                        Die values entsprechen den Filterkriterien, die der User ausgewählt hat.
                        BEACHTE: *Immer* berücksichtigt werden die values des Keys "gattung".
                        Für die anderen beiden Keys gilt: Berücksichtigt werden nur die values desjeniges Keys,
                        der gem. <allocTyp> ausgewertet wird.
                        Wenn allocTyp == AllocTyp.land werden nur die values des Keys "land" berücksichtigt.
                        Die values des Keys "sektor" bleiben unberücksichtigt.
        @param matches: Eine Liste von FilterMatch-Objekten, die zu den ausgewählten Filterkriterien in
                        <checkedFiltersDict> passen.
                        Ein FilterMatch enthält eine Depot-Position und eine Liste von XAllokation-Objekten.
                        Nicht zu jedem Filterkriterium gibt es matches.
        Je Value wird ein ReportTableModel erstellt, also wenn allocTyp == AllocTyp.land und die values sind
        ["Australien", "Brasilien"], dann werden 2 ReportTableModel-Objekte initiiert.
        """
        tmlist:List[ReportTableModel] = list()
        laender = sorted(list(checkedFiltersDict["land"]))
        gattungen = list(checkedFiltersDict["gattung"])
        for land in laender:
            alloclist:List[XAllocReport] = list()
            for match in matches:
                for allok in match.allokationen:
                    if match.deppos.gattung in gattungen and allok.typ == "land" and allok.name == land:
                        allocrep = XAllocReport()
                        allocrep.gattung = match.deppos.gattung
                        allocrep.alloc = allok.typ.capitalize()
                        allocrep.alloc_name = land
                        allocrep.wkn = match.deppos.wkn
                        allocrep.deppos_name = match.deppos.name
                        allocrep.wert = int(match.deppos.gesamtwert_aktuell * (allok.prozent/100))
                        allocrep.prozent = int(round(allok.prozent, 0))

                        allocrep.delta_kurs = ImonLogic.getDeltaKursPercent(match.deppos, 14)
                        alloclist.append(allocrep)
            if len(alloclist) > 0:
                tm = ReportTableModel(AllocTyp.land, alloclist)
                tmlist.append(tm)
        return tmlist
