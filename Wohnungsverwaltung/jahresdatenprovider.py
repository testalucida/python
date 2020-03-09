from business import DataProviderBase, Server
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

#+++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    prov = JahresdatenProvider()
    prov.connect(utils.getUser())

    data = prov.getMtlEinAusJahr(2019, 2)
    print(data)