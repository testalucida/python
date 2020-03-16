from typing import Dict, List
from business import DataProviderBase, Server, DataProvider
from interfaces import Vergleichswert, \
    XWohnungMinimal, XWohnungMinimalList, \
    XMtlEinAusJahr, XMtlEinAusJahrList, \
    XRechnungKurz, XRechnungKurzList, \
    XSonstigeEinAusJahr, XSonstigeEinAusJahrList
import utils
import datehelper

class EinAusJahr():
    def __init__(self, whg_id:int, jahr:int):
        self.whg_id = whg_id
        self.jahr = jahr
        self.netto_miete = 0
        self.nk_abschlag = 0
        self.hg_abschlag = 0
#+++++++++++++++++++++++++++++++++++++++++++++
class SonstigeJahressummen():
    def __init__(self, whg_id:int, jahr:int):
        self.whg_id = whg_id
        self.jahr = jahr
        self.nk_abrechnung = 0
        self.hg_abrechnung = 0
        self.sonst_kosten = 0
        self.sonderumlagen = 0
        self.abloese = 0
#+++++++++++++++++++++++++++++++++++++++++++++
class Jahresdaten():
    def __init__(self, whg_id:int, jahr:int):
        self.whg_id = whg_id
        self.jahr = jahr
        self.netto_miete = 0
        self.nk_abschlag = 0
        self.hg_abschlag = 0
        self.rechng = 0
        self.nk_abrechng = 0
        self.hg_abrechng = 0
        self.sonst_kosten = 0
        self.ergebnis = 0
        self.sonderumlagen = 0
        self.netto_miete_qm = 0
        self.nk_qm = 0
        self.hg_netto_qm = 0
        self.ruecklage_qm = 0
        self.hg_ges_qm = 0
#+++++++++++++++++++++++++++++++++++++++++++++
class Rechnungssumme():
    def __init__(self, whg_id:int, jahr:int):
        self.whg_id = whg_id
        self.jahr = jahr
        self.betrag = 0
#+++++++++++++++++++++++++++++++++++++++++++++
class JahresdatenCollection():
    """
    A collection containing all Jahresdaten concerning ONE property (whg_id), n years
    """
    def __init__(self, whg_id:int):
        self.whg_id = whg_id
        self._wohnungIdent = ''
        self._qm = 0
        self._dataList = []

    def getWhgId(self) -> int:
        return self.whg_id

    def setWohnungIdent(self, ident:str) -> None:
        self._wohnungIdent = ident

    def getWohnungIdent(self) -> str:
        return self._wohnungIdent

    def setQm(self, qm:int) -> None:
        self._qm = qm

    def getQm(self) -> int:
        return self._qm

    def append(self, jahresdaten:Jahresdaten) -> None:
        self._dataList.append(jahresdaten)

    def getJahresdaten(self, jahr:int) -> Jahresdaten:
        for data in self._dataList:
            if data.jahr == jahr:
                return data
        raise Exception(str(jahr) + " not found in Collection")

    def getJahresdatenList(self) -> List[Jahresdaten]:
        return self._dataList
#+++++++++++++++++++++++++++++++++++++++++++++
class JahresdatenCollectionList():
    def __init__(self):
        self._list = []

    def append(self, coll:JahresdatenCollection):
        self._list.append(coll)

    def getWhgId(self) -> int:
        return self._list[0].getWhgId()
#+++++++++++++++++++++++++++++++++++++++++++++
class JahresdatenProvider(DataProviderBase):
    def __init__(self):
        DataProviderBase.__init__(self)

    def getJahresdaten(self, whg_id: int, jahr_von: int, jahr_bis: int = None) \
            -> JahresdatenCollection:
        pass

    def getJahresdatenAlleWohnungen(self, jahr_von:int, jahr_bis:int = None) \
            -> List[JahresdatenCollection]:
        """
        Gets Jahresdaten objects of all active properties for the years
        given by jahr_von and jahr_bis
        :param jahr_von:
        :param jahr_bis: if not given, current year is assumed.
        :return: A list of JahresdatenCollection*s, one for each property.
                 Each JahresdatenCollection contains as many Jahresdaten objects
                 as are defined by the substraction year_bis - year_von + 1
        """
        #create the collection list to be returned:
        coll_list: List[JahresdatenCollection] = []  # top container for all JahresdatenCollections
        #get the involved properties (whg_id et al.):
        whglist: XWohnungMinimalList = self._getWohnungsdaten()
        for whg in whglist.getList():
            # get Jahresdaten for each property
            jdcoll:JahresdatenCollection = \
                self._getJahresdatenCollection(whg, jahr_von, jahr_bis)
            coll_list.append(jdcoll)

        return coll_list

    def _getJahresdatenCollection(self, whg:XWohnungMinimal,
                                  jahr_von:int, jahr_bis:int = None) \
                                  -> JahresdatenCollection:
        #create new JahresdatenCollection for given property whg
        jdcoll = JahresdatenCollection(whg.whg_id)
        jdcoll.setWohnungIdent(self._getWohnungIdent(whg))
        jdcoll.setQm(whg.qm)
        for jahr in range(jahr_von, jahr_bis+1):
            jd = Jahresdaten(whg.whg_id, jahr)
            jdcoll.append(jd)

        #summation of monthly revenues and expenses
        eajlist:List[EinAusJahr] = \
            self._getEinAusJahre(whg.whg_id, jahr_von, jahr_bis)
        self._assignEinAusJahrValues(jdcoll, eajlist)

        #summation of bills and withdrawels of reserve fund
        rslist:List[Rechnungssumme] = \
            self._getRechnungssummenJahre(whg.whg_id, jahr_von, jahr_bis)
        self._assignRechnungssummen(jdcoll, rslist)

        #summation of clearings
        sonst_summen_list:List[SonstigeJahressummen] = \
            self._getSonstigeJahressummen(whg.whg_id, jahr_von, jahr_bis)
        self._assignSonstigeJahressummen(jdcoll, sonst_summen_list)

        #calculate balance
        self._calculateErgebnis(jdcoll)

        #costs and revenues per qm:
        #self._calculateQm(jdcoll)

        return jdcoll
    
    def _assignEinAusJahrValues(self, jdcoll:JahresdatenCollection,
                                eajlist:List[EinAusJahr]) -> None:
        """
        Assign the values of eajlist to JahresdatenCollection jdcoll
        :param eajlist: contains EinAusJahr objects concerning ONE property,
                        n years
        :return:  None

        class EinAusJahr():
            def __init__(self, jahr:int, whg_id:int):
                self.whg_id = whg_id
                self.jahr = jahr
                self.netto_miete = 0
                self.nk_abschlag = 0
                self.hg_abschlag = 0
        """
        for einausjahr in eajlist:
            jd:Jahresdaten = jdcoll.getJahresdaten(einausjahr.jahr)
            jd.netto_miete = einausjahr.netto_miete
            jd.nk_abschlag = einausjahr.nk_abschlag
            jd.hg_abschlag = einausjahr.hg_abschlag

    def _assignRechnungssummen(self, jdcoll: JahresdatenCollection,
                                rslist: List[Rechnungssumme]) -> None:
        """
        Assign the values of rslist to JahresdatenCollection jdcoll
        :param rslist: contains Rechnungssumme objects concerning ONE property,
                        n years
        :return:  None

        class Rechnungssumme():
            def __init__(self, whg_id:int, jahr:int):
                self.whg_id = whg_id
                self.jahr = jahr
                self.betrag = 0
        """
        for rs in rslist:
            jd: Jahresdaten = jdcoll.getJahresdaten(rs.jahr)
            jd.rechng = rs.betrag

    def _assignSonstigeJahressummen(self, jdcoll: JahresdatenCollection,
                                    so_sum_list:List[SonstigeJahressummen]) -> None:
        """
        Assign the values of so_sum_list to the corresponding Jahresdaten object in
        JahresdatenCollection jdcoll
        :param so_sum_list:
        :return: None

        class SonstigeJahressummen():
            def __init__(self, whg_id:int, jahr:int):
                self.whg_id = whg_id
                self.jahr = jahr
                self.nk_abrechnung = 0
                self.hg_abrechnung = 0
                self.sonst_kosten = 0
                self.sonderumlagen = 0
        self.abloese = 0
        """
        for so_sum in so_sum_list:
            jd:Jahresdaten = jdcoll.getJahresdaten(so_sum.jahr)
            jd.nk_abrechng = so_sum.nk_abrechnung
            jd.hg_abrechng = so_sum.hg_abrechnung
            jd.sonst_kosten = so_sum.sonst_kosten
            jd.sonderumlagen = so_sum.sonderumlagen
            #abloese is ignored

    def _getWohnungsdaten(self) -> XWohnungMinimalList:
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=wohnungen_minimal&user=' + self._user)

        wlist = XWohnungMinimalList(XWohnungMinimal,
                                    self._getReadRetValOrRaiseException(resp))
        return wlist

    def _getWohnungIdent(self, whg_min:XWohnungMinimalList) -> str:
        ident = whg_min.ort + "\n" + \
                whg_min.strasse + "\n" + \
                whg_min.whg_bez
        return ident

    def _getEinAusJahre(self, whg_id:int, jahr_von:int, jahr_bis:int) \
            -> List[EinAusJahr]:
        """
        Gets a list containing one EinAusJahr object for each year involved.
        :param whg_id:
        :param jahr_von:
        :param jahr_bis:
        :return: a list containing at least one EinAusJahr object
        """
        l = []
        mea_list: XMtlEinAusJahrList = self._getMtlEinAusJahre(whg_id, jahr_von)
        for jahr in range(jahr_von, jahr_bis + 1):
            einausjahr = EinAusJahr(whg_id, jahr)
            l.append(einausjahr)
            for mea in mea_list.getList():
                if self._isAffected(jahr, mea.gueltig_ab, mea.gueltig_bis):
                    #check how many months this mea record was valid in year jahr:
                    if mea.gueltig_bis == '':
                        mea.gueltig_bis = datehelper.getTodayAsIsoString()
                    cnt = datehelper. \
                        getNumberOfMonths(mea.gueltig_ab, mea.gueltig_bis, jahr)
                    einausjahr.netto_miete += (cnt * int(mea.netto_miete))
                    einausjahr.nk_abschlag += (cnt * int(mea.nk_abschlag))
                    einausjahr.hg_abschlag += (cnt * int(mea.hg_brutto))

        return l

    def _getMtlEinAusJahre(self, whg_id:int, jahr_von:int) -> XMtlEinAusJahrList:
        """
        Gets all monthly expenses and revenues for property whg_int,
        beginning from year jahr_von.
        :param whg_id:
        :param jahr_von:
        :return: a list of suchlike dictionaries:
        [
            {'whg_id': '2',
             'jahr': 2019
             'gueltig_ab': '16.11.2019',
             'gueltig_bis': '17.11.2019',
             'netto_miete': '132.00',
             'nk_abschlag': '22.00',
             'hg_netto_abschlag': '33.00',
             'ruecklage_zufuehr': '11.00',
             'hg_brutto': '44.00'
            },
            {...
            }
        ]
        Each dictionary represents a set of monthly periodic transactions during a
        period specified by gueltig_ab and gueltig_bis.
        """
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=mtl_ein_aus_jahre&id=' +
                str(whg_id) + '&jahr_von=' + str(jahr_von) + '&user=' + self._user)

        mea_data = self._getReadRetValOrRaiseException(resp)
        mea_list = XMtlEinAusJahrList(XMtlEinAusJahr, mea_data)

        return mea_list

    def _isAffected(self, jahr:int, von:str, bis:str) -> bool:
        """
        Checks if jahr intersects or is contained in the period defined by
        gueltig_von and gueltig_bis
        :param jahr: the year to be checked
        :param von: begin of period. Format "yyyy-mm-dd".
        :param bis: end of period. Format "yyyy-mm-dd"
        :return: True if jahr is part or intersects the given period, else False
        """
        jahr_von = int(von[0:4])
        if bis == '':
            bis = datehelper.getTodayAsIsoString()
        jahr_bis = int(bis[0:4])
        return True if jahr >= jahr_von and jahr <= jahr_bis else False

    def _getRechnungssummenJahre(self, whg_id:int, jahr_von:int, jahr_bis:int) \
            -> List[Rechnungssumme]:
        """
        Gets a Rechnungssumme object of each involved year.
        :param whg_id:
        :param jahr_von:
        :param jahr_bis:
        :return: list of Rechnungssumme objects, one for each year
        """
        l = []
        rg_list:XRechnungKurzList = self._getRechnungenJahre(whg_id, jahr_von, jahr_bis)
        rg_sum:Rechnungssumme = None
        jahr_memo = 0
        for rg in rg_list.getList():
            if rg.jahr != jahr_memo:
                rg_sum = Rechnungssumme(rg.whg_id, rg.jahr)
                l.append(rg_sum)
                jahr_memo = rg.jahr
            anteil = rg.betrag / rg.verteilung_jahre
            rg_sum.betrag += int(round(anteil))
        return l

    def _getRechnungenJahre(self, whg_id:int, jahr_von:int, jahr_bis:int = None) \
            -> XRechnungKurzList:
        """
        Liefert for Wohnung whg_d alle Rechnungen und Entnahmen aus Rücklagen im
        Laufe der Jahre jahr_von bis jahr_bis.
        :param whg_id:
        :param jahr_von:
        :param jahr_bis:
        :return: a list of dictionaries:
        [
          {'whg_id': '1',
           'betrag': '222.00',
           'verteilung_jahre': '1',
           'year_bezahlt_am': '2019'
          },
          {...
          }
        ]
        """
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=rechng_jahre&jahr_von=' +
                str(jahr_von) + '&jahr_bis=' + str(jahr_bis) + '&id=' + str(whg_id) + '&user=' + self._user)
        rg_data = self._getReadRetValOrRaiseException(resp)
        rg_list = XRechnungKurzList(XRechnungKurz, rg_data)

        return rg_list

    def _getSonstigeJahressummen(self, whg_id:int, jahr_von:int, jahr_bis:int) \
            -> List[SonstigeJahressummen]:
        """
        Gets the summation of all kinds of intermittent payments and revenues.
        For each year one object of SonstigeJahressummen is provided.
        :param whg_id:
        :param jahr_von:
        :param jahr_bis:
        :return: a list containing at least one SonstigeJahressummen object.
        """
        l = []
        einauslist:XSonstigeEinAusJahrList = \
            self._getSonstigeEinAusJahr(whg_id, jahr_von, jahr_bis)
        sonst_summen:SonstigeJahressummen = None
        jahr_memo = 0
        for einaus in einauslist.getList():
            if einaus.jahr != jahr_memo:
                sonst_summen = SonstigeJahressummen(einaus.whg_id, einaus.jahr)
                l.append(sonst_summen)
                jahr_memo = einaus.jahr

            betrag = int(round(einaus.betrag))
            if einaus.art_kurz == 'hg_nachz':
                sonst_summen.hg_abrechnung -= betrag
            elif einaus.art_kurz == 'hg_rueck':
                sonst_summen.hg_abrechnung += betrag
            elif einaus.art_kurz == 'nk_nachz':
                sonst_summen.nk_abrechnung += betrag
            elif einaus.art_kurz == 'nk_rueck':
                sonst_summen.nk_abrechnung -= betrag
            elif einaus.art_kurz == 'sonderum':
                sonst_summen.sonderumlagen += betrag
            elif einaus.art_kurz == 'abloese':
                sonst_summen.abloese += betrag
            elif einaus.art_kurz == 'sonst_kost':
                sonst_summen.sonst_kosten += betrag
            else:
                raise Exception(
                    "JahresdatenProvider._getSonstigeJahressummen: unbekannte Art: "
                    + einaus.art_kurz)

        return l

    def _getSonstigeEinAusJahr(self, whg_id:int, jahr_von:int, jahr_bis:int) \
            -> XSonstigeEinAusJahrList:
        """
        Liefert alle Sonstigen Ein- und Auszahlungen des Jahre jahr.
        Es gibt folgende Arten von Sonstigen Ein- und Auszahlungen
        (Tabelle sea_art, Spalte art_kurz; Spalte ein_aus gibt Auskunft
         darüber, ob es sich um eine Ein- oder Auszahlung handelt:
              art_kurz         ein_aus
              --------         -------
            - hg_nachz          a
            - hg_rueck          e
            - nk_nachz          e
            - nk_rueck          a
            - sonderum          a
            - sonst_kost        a
            - abloese           a (interessiert nicht in diesem Kontext)
        :param jahr:
        :param whg_id:
        :return: a list of dictionaries:
        [
            {
                'whg_id': '1',
                'vj': 2019
                'betrag': '500.00',
                'ein_aus': 'a',
                'art_kurz': 'sonderum'
            },
            {...
            }
        ]
        """
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=sonst_ein_aus_jahre&jahr_von=' +
                str(jahr_von) + '&jahr_bis=' + str(jahr_bis) + '&id=' + str(whg_id) + '&user=' + self._user)
        sea_data = self._getReadRetValOrRaiseException(resp)
        sea_list = XSonstigeEinAusJahrList(XSonstigeEinAusJahr, sea_data)
        return sea_list

    def _calculateErgebnis(self, jdcoll:JahresdatenCollection) -> None:
        """
        calculates balance of costs and revenues
        :param jdcoll: JahresdatenCollection referred to one property, n years
        :return:
        """
        for jd in jdcoll.getJahresdatenList():
            jd.ergebnis = jd.netto_miete + jd.nk_abschlag + jd.nk_abrechng - \
                          jd.rechng - \
                          (jd.hg_abschlag + jd.hg_abrechng) - jd.sonst_kosten

    def _calculatQm(self, jdcoll:JahresdatenCollection) -> None:
        """
        calculates costs and revenues per qm
        :param jdcoll: JahresdatenCollection referred to one property, n years
        :return:
        """
        pass
#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    prov = JahresdatenProvider()
    prov.connect(utils.getUser())

    l:List[JahresdatenCollection] = prov.getJahresdatenAlleWohnungen(2019, 2019)
    for coll in l:
        jd:Jahresdaten = coll.getJahresdaten(2019)
        print("Nettomiete: ", jd.netto_miete, "\n",
              "NK-Abschlag: ", jd.nk_abschlag, "\n",
              "HG-Abschlag: ", jd.hg_abschlag, "\n",
              "Rechnungssumme: ", jd.rechng, "\n",
              "Sonstige Kosten: ", jd.sonst_kosten, "\n",
              "NK-Abrechnung: ", jd.nk_abrechng, "\n",
              "HG-Abrechnung: ", jd.hg_abrechng, "\n",
              "Ergebnis: ", jd.ergebnis, "\n",
              "\n")
    # l = prov._getSonstigeJahressummen(2019, 0)
    # for sj in l:
    #     print(sj.whg_id, ": ",
    #           "NK-Abrechng: ", sj.nk_abrechnung,
    #           ", HG-Abrechng: ", sj.hg_abrechnung,
    #           ", Sonstige Kosten: ", sj.sonst_kosten,
    #           ", Sonderumlagen: ", sj.sonderumlagen,
    #           ", Ablösen: ", sj.abloese)

    # l = prov._getEinAusJahr(2019)
    # for ea in l:
    #     print(ea.whg_id, ": ", ea.netto_miete, ", ", ea.nk_abschlag, ", ", ea.hg_abschlag)

    # l = prov._getRechnungssummenJahr(2019, 0)
    # for rg in l:
    #     print(rg.whg_id, ": ", rg.betrag)

    #jahresdaten_list = prov.getJahresdaten(2019, 2019, 1)

    #rechng = prov.getRechnungenJahr(2019, 1)
    #sea_list = prov.getSonstigeEinAusJahr(2019, 1)
