from typing import List
from business import DataProviderBase, Server
from interfaces import Vergleichswert, XJahresdaten, \
    XMtlEinAusJahr, XMtlEinAusJahrList, XEinAusJahr, \
    XRechnungKurz, XRechnungKurzList, \
    XSonstigeEinAusJahr, XSonstigeEinAusJahrList, XSonstigeJahressummen
import utils
import datehelper

class JahresdatenProvider(DataProviderBase):
    def __init__(self):
        DataProviderBase.__init__(self)

    def getJahresdaten(self,
                       jahr_von:int,
                       jahr_bis:int,
                       whg_id:int = 0) -> List[XJahresdaten]:
        li:List[XJahresdaten] = [];
        for jahr in range(jahr_von, jahr_bis+1):
            data:XJahresdaten = XJahresdaten()
            data.jahr = jahr
            data.whg_id = whg_id
            #summation of monthly revenues and expenses
            einausjahr:XEinAusJahr = self._getEinAusJahr(jahr, whg_id)
            data.netto_miete = einausjahr.netto_miete
            data.nk_abschlag = einausjahr.nk_abschlag
            data.hg_abschlag = einausjahr.hg_abschlag
            #summation of bills
            data.rechng = self._getRechnungssummeJahr(jahr, whg_id)
            #summation of clearings
            sonst_summen:XSonstigeJahressummen = \
                self._getSonstigeJahressummen(jahr, whg_id)
            data.nk_abrechng = sonst_summen.nk_abrechnung
            data.hg_abrechng = sonst_summen.hg_abrechnung

            li.append(data)

        return li

    def _getEinAusJahr(self, jahr:int, whg_id:int = 0) -> XEinAusJahr:
        mea_list: XMtlEinAusJahrList = self._getMtlEinAusJahr(jahr, whg_id)
        einausjahr = XEinAusJahr()
        for mea in mea_list.getList():
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

        return einausjahr

    def _getMtlEinAusJahr(self, jahr:int, whg_id:int = 0) -> XMtlEinAusJahrList:
        """
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
        """
        resp = self._session. \
            get(Server.SERVER + 'business.php?q=mtl_ein_aus_jahr&jahr=' +
                str(jahr) + '&id=' + str(whg_id) + '&user=' + self._user)

        mea_data = self._getReadRetValOrRaiseException(resp)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        mea_list = XMtlEinAusJahrList(XMtlEinAusJahr, mea_data)

        return mea_list

    def _getRechnungssummeJahr(self, jahr:int, whg_id:int) -> int:
        rg_list:XRechnungKurzList = self._getRechnungenJahr(jahr, whg_id)
        rg_sum = 0
        for rg in rg_list.getList():
            anteil = rg.betrag / rg.verteilung_jahre
            rg_sum += int(anteil)
        return rg_sum

    def _getRechnungenJahr(self, jahr:int, whg_id:int = None) -> XRechnungKurzList:
        """
        Liefert alle Rechnungen des Jahres jahr.
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
            -> XSonstigeJahressummen:
        einauslist = self._getSonstigeEinAusJahr(jahr, whg_id)

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

#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    prov = JahresdatenProvider()
    prov.connect(utils.getUser())

    jahresdaten_list = prov.getJahresdaten(2019, 2019, 1)

    #rechng = prov.getRechnungenJahr(2019, 1)
    #sea_list = prov.getSonstigeEinAusJahr(2019, 1)
