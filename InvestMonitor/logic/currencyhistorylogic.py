from typing import List, Dict

import datehelper
from data.db.currencyhistorydata import CurrencyHistoryData
from interface.interfaces import XExchangeRate


class CurrencyHistoryLogic:
    def __init__(self):
        self._db = CurrencyHistoryData()

    # def getDaysAndCurrencies( self, fromIsoDate:str=None, toIsoDate:str=None, base:str="EUR" ) -> (List, Dict):
    def getDaysAndCurrencies( self, cntYears:int) -> (List, Dict):
        today = datehelper.getCurrentDate()
        start = datehelper.addYears(today, -cntYears)
        fromIsoDate = datehelper.getIsoStringFromDate(start)
        toIsoDate = datehelper.getTodayAsIsoString()

        l:List[XExchangeRate] = self._db.getExchangeRates(fromIsoDate, toIsoDate, "EUR")
        daylist = list()
        currencies_ = dict()
        for xr in l:
            dt = datehelper.getDateFromIsoString(xr.date)
            daylist.append(dt)
            if not xr.target in currencies_:
                currencies_[xr.target] = list()
            currencies_[xr.target].append(xr.rate)
        daylist = list( set( daylist ) )
        daylist = sorted(daylist)
        return daylist, currencies_

####################################################################

if __name__ == "__main__":
    l = CurrencyHistoryLogic()
    days, currencies = l.getDaysAndCurrencies("2025-11-01", "2025-11-30", "EUR")
    for idx, day in enumerate(days):
        for key in currencies.keys():
            print(day, ": ", key, ": ", currencies[key][idx])