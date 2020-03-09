from business import DataProviderBase, Server
from interfaces import Vergleichswert, XJahresdaten
import utils

class JahresdatenProvider(DataProviderBase):
    def __init__(self):
        DataProviderBase.__init__(self)

    def getMtlEinAusJahr(self, jahr:int, whg_id:int = None):
        """
        :param jahr:
        :param whg_id:
        :return: a list like that:
        [
            {'whg_id': '2',
             'gueltig_ab': '16.11.2019',
             'gueltig_bis': '17.11.2019',
             'netto_miete': '132.00',
             'nk_abschlag': '22.00',
             'brutto_miete': '154.00',
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
        return mea_data

    def getRechnungenJahr(self, jahr:int, whg_id:int = None):
        """
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
        rg_list = self._getReadRetValOrRaiseException(resp)

        return rg_list

    def getSonstigeEinAusJahr(self, jahr:int, whg_id:int):
        """
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
        sea_list = self._getReadRetValOrRaiseException(resp)

        return sea_list

#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    prov = JahresdatenProvider()
    prov.connect(utils.getUser())

    #data = prov.getMtlEinAusJahr(2019, 2)
    #rechng = prov.getRechnungenJahr(2019, 1)
    sea_list = prov.getSonstigeEinAusJahr(2019, 1)
    print(data)