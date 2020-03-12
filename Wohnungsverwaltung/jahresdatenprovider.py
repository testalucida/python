from typing import Dict, List
from business import DataProviderBase, Server, DataProvider
from interfaces import Vergleichswert, \
    XMtlEinAusJahr, XMtlEinAusJahrList, \
    XRechnungKurz, XRechnungKurzList, \
    XSonstigeEinAusJahr, XSonstigeEinAusJahrList
import utils
import datehelper

class EinAusJahr():
    def __init__(self, jahr:int, whg_id:int):
        self.jahr = jahr
        self.whg_id = whg_id
        self.netto_miete = 0
        self.nk_abschlag = 0
        self.hg_abschlag = 0

class SonstigeJahressummen():
    def __init__(self, jahr:int, whg_id:int):
        self.jahr = jahr
        self.whg_id = whg_id
        self.nk_abrechnung = 0
        self.hg_abrechnung = 0
        self.sonst_kosten = 0
        self.sonderumlagen = 0
        self.abloese = 0

class Jahresdaten():
    def __init__(self):
        self.jahr = 0
        self.whg_id = 0
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

class Rechnungssumme():
    def __init__(self, jahr:int, whg_id:int):
        self.jahr = jahr
        self.whg_id = whg_id
        self.betrag = 0

class JahresdatenCollection():
    """
    A collection containing all Jahresdaten of exactly one property (whg_id)
    """
    def __init__(self, whg_id:int):
        self.whg_id = whg_id
        self.wohnungIdent = ''
        self.dataList = []

    def append(self, jahresdaten:Jahresdaten) -> None:
        self.dataList.append(jahresdaten)

    def get(self, jahr:int) -> Jahresdaten:
        for data in self.dataList:
            if data.jahr == jahr:
                return data
        raise Exception(str(jahr) + " not found in Collection")

class JahresdatenProvider(DataProviderBase):
    def __init__(self):
        DataProviderBase.__init__(self)

    def getJahresdaten(self,
                       jahr_von:int,
                       jahr_bis:int,
                       whg_id:int = 0) -> List[JahresdatenCollection]:
        """
        :param jahr_von:
        :param jahr_bis:
        :param whg_id: if whg_id > 0: Jahresdaten are provided for this whg_id.
                       if whg_id == 0: Jahresdaten are provided for all active
                       property objects.
        :return: a list of as many JahresdatenCollection objects as are concerned
                 by argument whg_id.
                 Each JahresdatenCollection contains as many
                 Jahresdaten objects as are defined by the subtraction
                 jahr_bis - jahr_von + 1.
        """
        coll:JahresdatenCollection = None
        for jahr in range(jahr_von, jahr_bis+1):
            data:Jahresdaten = Jahresdaten()
            data.jahr = jahr
            data.whg_id = whg_id
            #summation of monthly revenues and expenses
            einausjahr:EinAusJahr = self._getEinAusJahr(jahr, whg_id)
            data.netto_miete = einausjahr.netto_miete
            data.nk_abschlag = einausjahr.nk_abschlag
            data.hg_abschlag = einausjahr.hg_abschlag
            #summation of bills and withdrawels of reserve fund
            data.rechng = self._getRechnungssummenJahr(jahr, whg_id)
            #summation of clearings
            sonst_summen:SonstigeJahressummen = \
                self._getSonstigeJahressummen(jahr, whg_id)
            data.nk_abrechng = sonst_summen.nk_abrechnung
            data.hg_abrechng = sonst_summen.hg_abrechnung
            data.sonderumlagen = sonst_summen.sonderumlagen
            li.append(data)

        return coll

    def _getWohnungsdaten(self, whg_id:int) -> None:
        dp = DataProvider.createFromExistingConnection()
        dic = dp.getWohnungIdentifikation(whg_id)
        self._qm = dic['qm']
        self._wohnungident = dic['ort'] + '\n' + \
                             dic['strasse'] + '\n' + \
                             dic['whg_bez']

    def _getEinAusJahr(self, jahr:int, whg_id:int = 0) -> List[EinAusJahr]:
        """
        Gets a list containing one EinAusJahr object for each wohnung involved.
        If whg_id is specified (whg_id > 0) only one EinAusJahr object
        will be provided.
        :param jahr:
        :param whg_id:
        :return: a list containing at least one EinAusJahr object
        """
        l = []
        mea_list: XMtlEinAusJahrList = self._getMtlEinAusJahr(jahr, whg_id)
        einausjahr:EinAusJahr = None
        whg_id_memo = 0
        for mea in mea_list.getList():
            if mea.whg_id != whg_id_memo:
                einausjahr = EinAusJahr(jahr, mea.whg_id)
                l.append(einausjahr)
                whg_id_memo = mea.whg_id
            #each mea represents a record in table mtl_ein_aus which is or was
            #valid through a period of year jahr.
            #We have to check the number of months the record was valid
            #and summarize the amounts of each kind (netto_miete, nk_abschlag,...)
            if mea.gueltig_bis == '':
                mea.gueltig_bis = datehelper.getTodayAsIsoString()
            cnt = datehelper.\
                getNumberOfMonths(mea.gueltig_ab, mea.gueltig_bis, jahr)
            einausjahr.netto_miete += (cnt * int(mea.netto_miete))
            einausjahr.nk_abschlag += (cnt * int(mea.nk_abschlag))
            einausjahr.hg_abschlag += (cnt * int(mea.hg_brutto))

        return l

    def _getMtlEinAusJahr(self, jahr:int, whg_id:int = 0) -> XMtlEinAusJahrList:
        """
        Gets all monthly expenses and revenues of year jahr and wohnung whg_id.
        If no whg_id is specified (whg_id is 0) all monthly expenses and revenues
        of year jahr and *all* active wohnungen in table wohnung are provided.
        :param jahr:
        :param whg_id:
        :return: a list of suchlike dictionaries:
        [
            {'whg_id': '2',
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
            get(Server.SERVER + 'business.php?q=mtl_ein_aus_jahr&jahr=' +
                str(jahr) + '&id=' + str(whg_id) + '&user=' + self._user)

        mea_data = self._getReadRetValOrRaiseException(resp)
        #mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        mea_list = XMtlEinAusJahrList(XMtlEinAusJahr, mea_data)

        return mea_list

    def _getRechnungssummenJahr(self, jahr:int, whg_id:int) -> List[Rechnungssumme]:
        """
        Gets a Rechnungssumme object of each involved Wohnung.
        If whg_id is specified, the returned list will only contain one Rechnungssumme.
        :param jahr:
        :param whg_id: if whg_id is 0, a Rechnungssumme of each Wohnung in the database
                       will be returned.
        :return: list of Rechnungssumme objects
        """
        l = []
        rg_list:XRechnungKurzList = self._getRechnungenJahr(jahr, whg_id)
        rg_sum:Rechnungssumme = None
        whg_id_memo = 0
        for rg in rg_list.getList():
            if rg.whg_id != whg_id_memo:
                rg_sum = Rechnungssumme(jahr, rg.whg_id)
                l.append(rg_sum)
                whg_id_memo = rg.whg_id
            anteil = rg.betrag / rg.verteilung_jahre
            rg_sum.betrag += int(round(anteil))
        return l

    def _getRechnungenJahr(self, jahr:int, whg_id:int = None) -> XRechnungKurzList:
        """
        Liefert alle Rechnungen und Entnahmen aus Rücklagen im
        Laufe des Jahres jahr.
        :param jahr:
        :param whg_id:
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
            get(Server.SERVER + 'business.php?q=rechng_jahr&jahr=' +
                str(jahr) + '&id=' + str(whg_id) + '&user=' + self._user)
        rg_data = self._getReadRetValOrRaiseException(resp)
        rg_list = XRechnungKurzList(XRechnungKurz, rg_data)

        return rg_list

    def _getSonstigeJahressummen(self, jahr:int, whg_id:int = None) \
            -> List[SonstigeJahressummen]:
        """
        Gets the summation of all kinds of intermittent payments and revenues.
        For each property one object of SonstigeJahressummen is provided.
        If whg_id is given (whg_id > 0) the returned list will contain
        only one object.
        :param jahr:
        :param whg_id:
        :return: a list containing at least one SonstigeJahressummen object.
        """
        l = []
        einauslist:XSonstigeEinAusJahrList = \
            self._getSonstigeEinAusJahr(jahr, whg_id)
        sonst_summen:SonstigeJahressummen = None
        whg_id_memo = 0
        for einaus in einauslist.getList():
            if einaus.whg_id != whg_id_memo:
                sonst_summen = SonstigeJahressummen(jahr, einaus.whg_id)
                l.append(sonst_summen)
                whg_id_memo = einaus.whg_id

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

    def _getSonstigeEinAusJahr(self, jahr:int, whg_id:int) -> XSonstigeEinAusJahrList:
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
                'betrag': '500.00',
                'ein_aus': 'a',
                'art_kurz': 'sonderum'
            },
            {...
            }
        ]
        """
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=sonst_ein_aus_jahr&jahr=' +
                str(jahr) + '&id=' + str(whg_id) + '&user=' + self._user)
        sea_data = self._getReadRetValOrRaiseException(resp)
        sea_list = XSonstigeEinAusJahrList(XSonstigeEinAusJahr, sea_data)
        return sea_list

    def _calculateEinAusQm(self, data:Jahresdaten, qm:int) -> Jahresdaten:

        return data
#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    prov = JahresdatenProvider()
    prov.connect(utils.getUser())

    l = prov._getSonstigeJahressummen(2019, 0)
    for sj in l:
        print(sj.whg_id, ": ",
              "NK-Abrechng: ", sj.nk_abrechnung,
              ", HG-Abrechng: ", sj.hg_abrechnung,
              ", Sonstige Kosten: ", sj.sonst_kosten,
              ", Sonderumlagen: ", sj.sonderumlagen,
              ", Ablösen: ", sj.abloese)

    # l = prov._getEinAusJahr(2019)
    # for ea in l:
    #     print(ea.whg_id, ": ", ea.netto_miete, ", ", ea.nk_abschlag, ", ", ea.hg_abschlag)

    # l = prov._getRechnungssummenJahr(2019, 0)
    # for rg in l:
    #     print(rg.whg_id, ": ", rg.betrag)

    #jahresdaten_list = prov.getJahresdaten(2019, 2019, 1)

    #rechng = prov.getRechnungenJahr(2019, 1)
    #sea_list = prov.getSonstigeEinAusJahr(2019, 1)
