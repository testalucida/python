import json
from typing import List, Tuple, Dict

import requests

import datehelper
from data.db.investmonitordata import InvestMonitorData


class ExchangeRates:
    def __init__( self, db:InvestMonitorData ):
        self._url = "https://v6.exchangerate-api.com/v6/0a0eb5cb6e62d6fba70d772a/"
        self._baseCurrency = "EUR"
        self._url_history = self._url + "history/" + self._baseCurrency + "/"
        self._db = db
        self._currencies = ["USD", "GBP", "CHF", "AUD", "CAD"]
        self._rates:List[Tuple] = None # enthält alle Sätze der Tabelle exchangerates
        self._yearIdx = dict()

    def initDatabase( self, yyyy_mm_dd_start:str, cntDaysBackwards:int ):
        """
        Ermittelt, beginnend ab yyyy_mm_dd_start, für cntDays die exchange rates und schreibt sie in die Datenbank.
        Beachte: Die Initialiserung erfolgt descending, also es wird bei yyy_mm_dd_start beginnend, cntDaysBackwards rückwärts
        gezählt.
        """
        day_end = datehelper.addDaysToIsoString( yyyy_mm_dd_start, -cntDaysBackwards )
        self._insertRates( day_end, yyyy_mm_dd_start )

    def updateLatestRates( self ):
        """
        Ermittelt in der Tabelle exchangerates das jüngste Datum.
        Ist dieses kleiner als current date, werden die exchange rates der fehlenden Tage aus der exchangerate-api ermittelt
        und in die Tabelle exchangerates eingefügt.
        Beim Aufruf der exchangerate-api ist base_code immer "EUR"
        """
        today = datehelper.getTodayAsIsoString()
        latest = self._getLatestDate()
        if today > latest:
            fromdate = datehelper.addDaysToIsoString( latest, 1 )
            self._insertRates( fromdate, today )

    def _getLatestDate( self ) -> str:
        """
        Ermittelt aus der Tabelle exchangerates das jüngste Datum, zu dem Daten existieren, und liefert es zurück
        """
        latest = self._db.getLatestDate()
        if not latest:
            raise Exception( "Datenbank ist nicht initialisiert." )
            # today = datehelper.getCurrentDate()
            # latest = datehelper.addYears( today, -5 )
            #return datehelper.getIsoStringFromDate( latest )
        return latest

    def _insertRates( self, from_yyyy_mm_dd:str, to_yyyy_mm_dd:str ):
        """
        Ermittelt aus der exchangerate-api die exchange rates des angegebenen Intervalls und speichert sie in der
        Tabelle exchangerates ab.
        Beachte: from_yyyy_mm_dd muss <= sein to_yyyy_mm_dd
        """
        assert from_yyyy_mm_dd <= to_yyyy_mm_dd
        day = to_yyyy_mm_dd
        while day >= from_yyyy_mm_dd:
            if not datehelper.isWeekend( day ) and not self._db.existRates( day ):
                rates = self._callApiHistory( day ) # rates
                for curr in self._currencies: # USD, GBP, CHF
                    #print( rates[curr] )
                    self._insert( day, curr, rates[curr] )
            self._db.commit()
            day = datehelper.addDaysToIsoString( day, -1 )

    def _insert( self, day:str, targetCurrency:str, value:float ):
        """
        Fügt 2 Sätze in die Datenbank ein: einen mit den Daten wie übergeben,
        einen zweiten mit targetCurrency als baseCurrency und entsprechend umgerechneten value.
        """
        self._db.insertExchangeRate( day, self._baseCurrency, targetCurrency, value )
        value = 1/value
        self._db.insertExchangeRate( day, targetCurrency, self._baseCurrency, value )

    @staticmethod
    def _getDayParts( day, withSlashes=True ) -> str or Tuple:
        """
        Bildet aus day das Tuple (yyyy, mm, dd) und liefert es zurück.
        Wenn withSlashes == True, werden "/" zwischen die Parts eingefügt. Es wird dann ein String zurückgeliefert
        """
        if withSlashes:
            return  day[:4] + "/" + day[5:7] + "/" + day[8:10]
        return day[:4], day[5:7], day[8:10]

    def getRatesFromApi( self, day:str ) -> List:
        """
        Ermittelt für den Tag day die interessierenden exchange rates
        """
        raise NotImplementedError( "Methode ExchangeRates.getRatesFromApi() not yet implemented.")

    def _callApiHistory( self, day:str ) -> Dict or None:
        url = self._url_history + self._getDayParts( day )
        resp = requests.get( url )
        if resp.status_code == 200:  # ok
            dic = json.loads( resp.content )
            all_rates:Dict = dic["conversion_rates"]
            # print( all_rates["EUR"] )
            rates = dict()
            # ein Dictionary bilden, das nur die gewünschten Währungen enthält,
            # das sieht dann so aus {"USD": 1.10, "GBP": 1.22, "CHF": 1.0}
            for curr in self._currencies:
                rates[curr] = all_rates[curr]
        else:
            rates = None
        return rates

    def convert( self, base:str, target:str, yyyy_mm_dd:str, amount:float, decimals:int=4 ) -> float:
        """
        Wandelt amount um von der Währung base (z.B. "USD") in die Währung target (z.B. "EUR") am Tag yyyy_mm_dd
        und liefert diesen Wert zurück - per default mit 4 Nachkommastellen.
        """
        if not self._rates:
            self.updateLatestRates()
            self._loadRates()

        if not (base == self._baseCurrency or base in self._currencies):
            raise ValueError( "Für die angegebene base-Währung '%s' gibt es keine exchange rates." % base )
        if not (target == self._baseCurrency or target in self._currencies):
            raise ValueError( "Für die angegebene target-Währung '%s' gibt es keine exchange rates." % target )

        sYear = yyyy_mm_dd[:4]
        start = self._yearIdx[sYear][0]
        end = self._yearIdx[sYear][1]
        # print( start, end)
        exc_rate = 0.0
        rates = self._rates[start:end+1]
        for rate in rates: # rate: (day, curr1, curr2, value)
            if rate[0] == yyyy_mm_dd \
            and rate[1] == base \
            and rate[2] == target:
                exc_rate = rate[3]
                break
        if exc_rate == 0.0:
            # könnte ein Wochenende sein
            raise ValueError( "Für den angegebenen Tag '%s' gibt es keine exchange rates - Wochenende?" % yyyy_mm_dd )

        value = amount * exc_rate
        return round( value, decimals )

    def _checkExists( self, yyyy_mm_dd:str ) -> bool:
        """
        prüft, ob für das angegebene Datum die exchange rates in der Tabelle exchangerates vorhanden sind
        """
        raise NotImplementedError( "Methode ExchangeRates._checkExists() not yet implemented." )

    def _checkExistsToday( self ) -> bool:
        """
        prüft, ob für das heutige Datum (current date) die exchange rates in der Tabelle exchangerates vorhanden sind
        """
        raise NotImplementedError( "Methode ExchangeRates._checkExistsToday() not yet implemented." )

    def _loadRates( self ):
        """
        Lädt alle Sätze der Tabelle exchangerates in die Liste self._rates
        """
        self._rates = self._db.getAllExchangeRates() # sortiert nach date desc
        sYear = "0"
        idx = 0
        for rate in self._rates:
            sY = rate[0][:4]
            if sY != sYear:
                self._yearIdx[sY] = list()
                self._yearIdx[sY].append( idx )
                if not sYear == "0":
                    self._yearIdx[sYear].append( idx-1 )
                sYear = sY
            idx += 1
        # Index des letzten Elements eintragen:
        self._yearIdx[sYear].append( idx-1 )


if __name__ == "__main__":
    db = InvestMonitorData()
    ex = ExchangeRates(db)
    #ex.initDatabase("2025-12-08", 1825)
