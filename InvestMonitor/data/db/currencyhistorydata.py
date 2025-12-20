from typing import List

from base.databasecommon2 import DatabaseCommon
from imon.definitions import DATABASE
from interface.interfaces import XExchangeRate


class CurrencyHistoryData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self, DATABASE )

    def getExchangeRates( self, fromIsoDate:str, toIsoDate:str, baseCurr:str ) -> List[XExchangeRate]:
        """
        Liefert zur gewünschten Base-Currency alle in der DB vorhandenen Wechselkurse im Zeitraum
        fromIsoDate bis toIsoDate. Beide Tage sind included.
        Liefert eine Liste von XExchangeRates zurück.
        """
        sql = ("select date, base, target, rate "
               "from exchangerates "
               "where date >= '%s' and date <= '%s' "
               "and base = '%s' "
               "order by date asc " % (fromIsoDate, toIsoDate, baseCurr))
        xlist = self.readAllGetObjectList( sql, XExchangeRate )
        return xlist

if __name__ == "__main__":
    data = CurrencyHistoryData()
    l = data.getExchangeRates("2025-11-01", "2025-11-05", "EUR")
    print(l)

