import math
from operator import itemgetter, attrgetter
from typing import List

from pandas import DataFrame, Series
import pandas as pd
from yfinance.scrapers.quote import FastInfo

import datehelper
from base.basetablemodel import BaseTableModel, SumTableModel
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from imon.enums import InfoPanelOrder
from interface.interfaces import XDepotPosition, XDelta, XDetail
from imon.definitions import DATABASE_DIR, DEFAULT_PERIOD, DEFAULT_INTERVAL


class InvestMonitorLogic:
    #summe_gesamtwerte = 0.0
    def __init__( self ):
        self._db = InvestMonitorData()
        self._tickerHist = TickerHistory()
        self._defaultPeriod = DEFAULT_PERIOD #Period.oneYear
        self._defaultInterval = DEFAULT_INTERVAL #Interval.oneWeek
        self._minPeriod = Period.oneDay
        self._minInterval = Interval.oneMin

    # def saveMyHistories( self ):
    #     histDf:DataFrame = self.getMyTickerHistories( self._defaultPeriod, self._defaultInterval )
    #     histDf.to_pickle( DATABASE_DIR + "/histories.df" ) # + datehelper.getCurrentDateIso() )
    #     actDf:DataFrame = self.getMyTickerHistories( Period.oneDay, Interval.oneMin )
    #     actDf.to_pickle( DATABASE_DIR + "/todayhistories.df" )
    #
    # @staticmethod
    # def loadMyHistories( todayHistory:bool = False) -> DataFrame:
    #     if todayHistory:
    #         df = pd.read_pickle( DATABASE_DIR + "/todayhistories.df" )
    #     else:
    #         df = pd.read_pickle( DATABASE_DIR + "/histories.df" )
    #     return df
    #
    # @staticmethod
    # def getHistory( ticker:str, series:SeriesName, dfAllHistories:DataFrame=None ) -> Series:
    #     """
    #     Ermittelt aus dem DataFrame, der alle Historien aller Ticker enthält, die gewünschte Serie.
    #     !!! Ist dfAllHistories nicht angegeben, wird der DataFrame ***DER AUF PLATTE GESPEICHERT IST*** geladen. !!!
    #     :param ticker:
    #     :param series:
    #     :param dfAllHistories:
    #     :return:
    #     """
    #     if not dfAllHistories:
    #         dfAllHistories = InvestMonitorLogic.loadMyHistories()
    #     allSeries:DataFrame = dfAllHistories[series.value]
    #     tickerhist:Series = allSeries[ticker]
    #     return tickerhist

    # def getMyTickerHistories( self, period=Period.oneYear, interval=Interval.oneWeek ):
    #     # Alle Ticker aus dem Depot holen:
    #     tickerlist = self._db.getAllMyTickers()
    #     # Mit der TickerList die Historien holen:
    #     tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
    #                                                                               period=period,
    #                                                                               interval=interval )
    #     return tickerHistories

    # @staticmethod
    # def getSummeGesamtwerte():
    #     return InvestMonitorLogic.summe_gesamtwerte

    def getDepotPosition( self, ticker:str, period=Period.oneYear, interval=Interval.oneWeek ) -> XDepotPosition:
        """
        Liefert alle Daten für die Depotposition <ticker>.

        :param ticker:
        :param period:
        :param interval:
        :return:
        """
        deppos:XDepotPosition = self._db.getDepotPosition( ticker )
        #self.provideTickerHistories( [deppos,], period=period, interval=interval )
        self._provideOrderData( deppos )
        tickerHistory:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        closeHist:Series = tickerHistory[SeriesName.Close.value]
        dividends:Series = tickerHistory[SeriesName.Dividends.value]
        self._provideWertpapierData( deppos, closeHist, dividends )
        return deppos

    # def getDepotPositions____( self, period:Period, interval:Interval ) -> List[XDepotPosition]:
    #     """
    #     Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
    #     im Default-Zeitintervall
    #     :return:
    #     """
    #     # Depotpositonen holen:
    #     poslist:List[XDepotPosition] = self._db.getDepotPositions()
    #     tickerlist = [pos.ticker for pos in poslist]
    #     tickerHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
    #                                                                              period=period,
    #                                                                              interval=interval )
    #     tickerHistories = self._checkForNaN( tickerHistories )
    #     closeDf:DataFrame = tickerHistories[SeriesName.Close.value]
    #     dividendsDf:DataFrame = tickerHistories[SeriesName.Dividends.value]
    #     for deppos in poslist:
    #         self._provideOrderData( deppos )
    #         try:
    #             closeHist:Series = closeDf[deppos.ticker]
    #             dividends:Series = dividendsDf[deppos.ticker]
    #             self._provideWertpapierData( deppos, closeHist, dividends )
    #         except Exception as ex:
    #             print( deppos.ticker, " not found in DataFrame closeDf" )
    #     return poslist

    def getDepotPositions( self, period:Period, interval:Interval ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        # for deppos in poslist:
        #     self._provideOrderData( deppos )
        # Wertpapierdaten in Positionen eintragen (Kursverlauf, Dividenden etc.)
        poslist = self.provideTickerHistories( poslist, period, interval )
        return poslist

    def provideTickerHistories( self, poslist:List[XDepotPosition], period:Period, interval:Interval ) -> List[XDepotPosition]:
        tickerlist = [pos.ticker for pos in poslist]
        tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                  period=period,
                                                                                  interval=interval )
        tickerHistories = self._checkForNaN( tickerHistories )
        closeDf: DataFrame = tickerHistories[SeriesName.Close.value]
        dividendsDf: DataFrame = tickerHistories[SeriesName.Dividends.value]
        for deppos in poslist:
            self._provideOrderData( deppos )
            try:
                closeHist: Series = closeDf[deppos.ticker]
                dividends: Series = dividendsDf[deppos.ticker]
                self._provideWertpapierData( deppos, closeHist, dividends )
            except Exception as ex:
                print( deppos.ticker, " not found in DataFrame closeDf" )
        return poslist

    @staticmethod
    def _checkForNaN( df:DataFrame ) -> DataFrame:
        row = df.tail(1) # damit haben wir die letzte Zeile des DataFrame, also die letzten Values aller Series (columns)
        for name, cellValues in row.items():
            # name: Spaltenkopf, z.B. EZTQ.F
            # cellValues: die Values von row
            if math.isnan( cellValues[0] ):
                df = df[:-1]
                break
        return df

    def _provideWertpapierData( self, deppos:XDepotPosition, closeHist:Series, dividends:Series ) -> None:
        deppos.history = closeHist
        deppos.history_period = self._defaultPeriod
        deppos.history_interval = self._defaultInterval
        deppos.dividends = dividends
        deppos.dividend_yield = 0.0

        deppos.kurs_aktuell, orig_currency = self.getKursAktuellInEuro( deppos.ticker )
        if deppos.kurs_aktuell == 0:
            print( deppos.wkn, "/", deppos.ticker,
                   ": _provideWertpapierData(): call to getKursAktuellInEuro() failed.\nNo last_price availabel.")

        deppos.dividend_period = self._getSumDividends( dividends )
        if orig_currency != "EUR":
            deppos.history = self._convertSeries( deppos.history, orig_currency )
            if deppos.dividend_period > 0:
                deppos.dividends = self._convertSeries( deppos.dividends, orig_currency )
                deppos.dividend_period = \
                    round( TickerHistory.convertToEuro( deppos.dividend_period, orig_currency ), 3 )
        if deppos.dividend_period > 0:
            # deppos.dividend_yield = self._computeDividendYield( deppos.kurs_aktuell, deppos.dividend_period )
            first_kurs_period = closeHist.array[0]
            deppos.dividend_yield = self._computeDividendYield( first_kurs_period, deppos.dividend_period )
        self._provideGesamtwertAndDelta( deppos )
        self._providePaidDividends( deppos, dividends )

    def _providePaidDividends( self, deppos:XDepotPosition, dividends:Series ):
        """
        Ermittelt die Dividendenzahlungen, die für <deppos> gemäß Eintragungen in <dividends> angefallen sind.
        Für jede Dividendenzahlung wird nur der zu diesem Zeitpunkt vorhandene Depotbestand berücksichtigt.
        :param deppos:
        :param dividends:
        :return:
        """
        deppos.dividend_paid_period = 0
        #todo
        deltas = self._db.getDeltas( deppos.wkn  )
        deltas.sort( key=attrgetter( "delta_datum" ) )
        sum_dividends = 0
        for pay_ts, value in dividends.items():
            if value > 0:
                #print( "paid: ", str(pay_ts)[:10], ": ", value )
                # den Depotbestand der Position <deppos> zum Datum <paydate> ermitteln:
                sum_dividends += self._computeDividendOnBestand( deltas, float( value ), str( pay_ts )[:10] )
        deppos.dividend_paid_period = sum_dividends

    @staticmethod
    def _computeDividendOnBestand( deltas:List[XDelta], dividend:float, paydate:str ) -> int:
        """
        Errechnet die Dividende, die auf den am Ausschüttungstag <paydate> vorhandenen Bestand bezahlt wurde.
        :param deltas: Alle Käufe u. Verkäufe eines bestimmten Fonds (oder Aktie)
                       Es wird vorausgesetzt, dass deltas nach <delta_datum> aufsteigend sortiert ist.
        :param dividend: an paydate bezahlte Dividende pro Stück
        :param paydate: Ausschüttungstag (ISO-Format)
        :return:
        """
        summe_stck = 0
        for delta in deltas:
            if delta.delta_datum < paydate:
                summe_stck += delta.delta_stck # gekaufte Stücke werden addiert, verkaufte subtrahiert.
                                               # <delta.verkauft_stck> braucht nicht berücksichtigt werden,
                                               # da sie nur eine Aufteilung der Verkäufe (die hier subtrahiert werden)
                                               # auf die Käufe darstellen (im Sinne verfügbarer Stücke)
            else:
                break
        return int(round( summe_stck * dividend, 2 ) )


    @staticmethod
    def _provideGesamtwertAndDelta( deppos:XDepotPosition ):
        deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
        #if deppos.gesamtkaufpreis > 0:
        if deppos.einstandswert_restbestand > 0:
            deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.einstandswert_restbestand - 1) * 100, 2 )

    @staticmethod
    def _getSumDividends( dividends: Series ) -> float:
        div: float = sum( [v for v in dividends.values if not math.isnan( v )] )
        return round( div, 3 )

    def updateWertpapierData( self, x:XDepotPosition, period:Period, interval:Interval ) -> None:
        """
        Ermittelt für das übergebene Wertpapier (repräsentiert durch <x>) die Historie gem. <period> und <interval>
        und schreibt diese Werte in <x> (x.history, x.history_period, x.history_interval.
        :param x: die zu aktualisierende Depot-Position
        :param period:
        :param interval:
        :return:
        """
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( x.ticker, period, interval )
        self._provideWertpapierData( x, df[SeriesName.Close.value], df[SeriesName.Dividends.value] )
        x.history_period = period
        x.history_interval = interval

    def updateKursAndDivYield( self, deppos:XDepotPosition ):
        deppos.kurs_aktuell, dummy = self.getKursAktuellInEuro( deppos.ticker )
        if deppos.kurs_aktuell > 0 and deppos.dividend_period > 0:
            first_kurs_period = deppos.history.array[0]
            # deppos.dividend_yield = self._computeDividendYield( deppos.kurs_aktuell, deppos.dividend_period )
            deppos.dividend_yield = self._computeDividendYield( first_kurs_period, deppos.dividend_period )

    @staticmethod
    def _computeDividendYield( kurs:float, dividend:float ) -> float:
        divYield = dividend / kurs
        return round( divYield*100, 3 )

    @staticmethod
    def getSimulatedDividendYield( kurs_aktuell:float, dividends:Series ) -> float:
        """
        Berechnet die theoretische Dividendenrendite auf Basis des aktuellen Kurses und des Durchschnitts der
        Dividendenzahlungen in der eingestellten Periode
        :return: die Rendite in Prozent, gerundet auf 2 Stellen genau
        """
        sumDiv = 0.0
        startDayIso = ""
        endDayIso = ""
        for index, value in dividends.items():
            dateIso = str(index)[:10]
            if not startDayIso:
                startDayIso = dateIso
            endDayIso = dateIso
            if value and value > 0:
                sumDiv += value
        days = datehelper.getNumberOfDays3( startDayIso, endDayIso )
        years = days/365
        if years > 0:
            avg_annual_yield = sumDiv / years
            return round( avg_annual_yield/kurs_aktuell*100, 2 )
        return 0.0

    def getKursAktuellInEuro( self, ticker:str ) -> (float, str):
        """
        Ermittelt den letzten Kurs des Wertpapiers.
        Transformiert ihn in EUR, wenn erforderlich.
        umgewandelt in eine Serie mit EUR-Werten.
        :param ticker:
        :return: den letzten Kurs in Euro, gerundet auf 3 Stellen hinter dem Komma
                 UND die ursprüngliche Währung (EUR oder Fremdwährung, die konvertiert wurde)
        """
        fastInfo: FastInfo = self._tickerHist.getFastInfo( ticker )
        if fastInfo:
            last_price = fastInfo.last_price
            currency = str( fastInfo.currency )
            if currency != "EUR":
                last_price = TickerHistory.convertToEuro( last_price, currency )
            return round( last_price, 3 ), currency
        else:
            print( "Ticker '%s':\nNo FastInfo available" % ticker )
            return 0, ""

    @staticmethod
    def _convertSeries( series:Series, currency:str ):
        """
        Übersetzt alle Werte in series.values in Euro und schreibt sie in eine Liste.
        Macht daraus und aus series.index eine neue Series und gibt diese zurück.
        Das muss sein, damit die Beschriftung der y-Achse im Graphen stimmt.
        :param series:
        :param currency: Währung wie in FastInfo eingetragen. (GBp also noch nicht in GBP umgewandelt.)
        :return:
        """
        values = series.values
        vlist = list()
        for value in values:
            if not math.isnan( value ):
                value = TickerHistory.convertToEuro( value, currency )
            else:
                value = 0
            vlist.append( value )
        index = series.index
        serNew = Series(vlist, index)
        return serNew

    # def _provideOrderData( self, deppos:XDepotPosition ):
    #     """
    #     Holt zur übergebenen Depotposition die delta-Daten aus der DB und trägt sie ein
    #     :param deppos:
    #     :return:
    #     """
    #     deltalist:List[XDelta] = self._db.getDeltas( deppos.wkn )
    #     deppos.stueck = 0
    #     deppos.gesamtkaufpreis = deppos.maxKaufpreis = deppos.minKaufpreis = 0
    #     for delta in deltalist:
    #         deppos.stueck += delta.delta_stck
    #         if delta.delta_stck > 0:
    #             # Kauf; Verkäufe dürfen für die Ermittlung von max, min und Durchscnitt nicht
    #             # berücksichtigt werden
    #             orderpreis = delta.delta_stck * delta.preis_stck
    #             deppos.gesamtkaufpreis += orderpreis
    #             deppos.maxKaufpreis = delta.preis_stck if delta.preis_stck > deppos.maxKaufpreis else deppos.maxKaufpreis
    #             deppos.minKaufpreis = delta.preis_stck \
    #                                   if delta.preis_stck < deppos.minKaufpreis or deppos.minKaufpreis == 0 \
    #                                   else deppos.minKaufpreis
    #     deppos.gesamtkaufpreis = int( round( deppos.gesamtkaufpreis, 2 ) )
    #     if deppos.stueck > 0:
    #         deppos.preisprostueck = round( deppos.gesamtkaufpreis / deppos.stueck, 2 )

    # def _provideOrderData( self, deppos: XDepotPosition ):
    #     """
    #     Holt zur übergebenen Depotposition die delta-Daten aus der DB und trägt sie ein
    #     :param deppos:
    #     :return:
    #     """
    #     deltalist: List[XDelta] = self._db.getDeltas( deppos.wkn )
    #     deppos.stueck = gekaufte_stueck = 0
    #     deppos.gesamtkaufpreis = deppos.maxKaufpreis = deppos.minKaufpreis = 0
    #     for delta in deltalist:
    #         deppos.stueck += delta.delta_stck
    #         if delta.delta_stck > 0:
    #             # Kauf; Verkäufe dürfen für die Ermittlung von max, min und Durchscnitt nicht
    #             # berücksichtigt werden
    #             gekaufte_stueck += delta.delta_stck
    #             orderpreis = delta.delta_stck * delta.preis_stck
    #             deppos.gesamtkaufpreis += orderpreis
    #             deppos.maxKaufpreis = delta.preis_stck if delta.preis_stck > deppos.maxKaufpreis else deppos.maxKaufpreis
    #             deppos.minKaufpreis = delta.preis_stck \
    #                 if delta.preis_stck < deppos.minKaufpreis or deppos.minKaufpreis == 0 \
    #                 else deppos.minKaufpreis
    #     deppos.gesamtkaufpreis = int( round( deppos.gesamtkaufpreis, 2 ) )
    #     if deppos.stueck > 0: # es gibt noch einen Depot-Bestand
    #         deppos.preisprostueck = round( deppos.gesamtkaufpreis / gekaufte_stueck, 2 )
    #         deppos.einstandswert_restbestand = int( round( deppos.preisprostueck * deppos.stueck, 2 ) )

    def _provideOrderData( self, deppos: XDepotPosition ):
        """
        Holt zur übergebenen Depotposition die delta-Daten aus der DB und trägt sie ein
        :param deppos:
        :return:
        """
        deltalist: List[XDelta] = self._db.getDeltas( deppos.wkn ) # sortiert nach delta_datum absteigend
        deppos.stueck = 0
        deppos.einstandswert_restbestand = deppos.maxKaufpreis = deppos.minKaufpreis = 0
        for delta in deltalist:
            if delta.delta_stck > 0:
                # Kauf; Verkäufe dürfen für die Ermittlung von max, min und Durchscnitt nicht
                # berücksichtigt werden
                if not deppos.letzter_kauf:
                    deppos.letzter_kauf = delta.delta_datum
                deppos.erster_kauf = delta.delta_datum
                deppos.stueck += ( delta.delta_stck - delta.verkauft_stck )
                deppos.einstandswert_restbestand += ( delta.delta_stck * delta.preis_stck )
                deppos.maxKaufpreis = delta.preis_stck if delta.preis_stck > deppos.maxKaufpreis else deppos.maxKaufpreis
                deppos.minKaufpreis = delta.preis_stck \
                    if delta.preis_stck < deppos.minKaufpreis or deppos.minKaufpreis == 0 \
                    else deppos.minKaufpreis
        deppos.einstandswert_restbestand = int( round( deppos.einstandswert_restbestand, 2 ) )
        if deppos.stueck > 0: # es gibt noch einen Depot-Bestand
            deppos.preisprostueck = round( deppos.einstandswert_restbestand / deppos.stueck, 2 )
            deppos.einstandswert_restbestand = int( round( deppos.einstandswert_restbestand, 2 ) )

    def getHistoryByPeriod( self, ticker:str, period:Period, interval:Interval ):
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        return df

    def getSeriesHistoryByPeriod( self, ticker, seriesName:SeriesName, period:Period, interval:Interval ) -> Series:
        df:DataFrame = self.getHistoryByPeriod( ticker, period, interval )
        return df[seriesName.value]

    def getOrders( self, wkn:str ) -> SumTableModel:
        deltalist = self._db.getDeltas( wkn )
        tm = SumTableModel( deltalist, 0, ("delta_stck", "order_summe") )
        tm.setKeyHeaderMappings2( ("delta_datum", "delta_stck", "preis_stck", "order_summe",
                                   "verkauft_stck", "verkaufskosten", "bemerkung"),
                                  ("Datum",  "Stück", "Stück-\npreis (€)", "Order-\nsumme (€)",
                                   "Stück vk.", "Verk.kosten", "Bemerkung") )
        return tm

    @staticmethod
    def getDetails( deppos:XDepotPosition ) -> XDetail:
        """
        Liefert die Daten für die Detailanzeige.
        Diese befinden sich bereits in <deppos>, sie müssen nur in ein XDetail-Objekt überführt werden.
        :param deppos:
        :return:
        """
        x = XDetail()
        x.basic_index = deppos.basic_index
        x.beschreibung = deppos.beschreibung
        x.topfirmen = deppos.topfirmen
        x.toplaender = deppos.toplaender
        x.topsektoren = deppos.topsektoren
        x.bank = deppos.bank
        x.depot_nr = deppos.depot_nr
        x.depot_vrrkto = deppos.depot_vrrkto
        return x

    def getAllOrders( self ) -> SumTableModel:
        deltas:List[XDelta] = self._db.getAllDeltas()
        tm = SumTableModel( deltas, 0, ("order_summe",) )
        tm.setKeyHeaderMappings2(
            ( "id", "delta_datum", "name", "wkn", "isin", "ticker", "depot_id", "delta_stck", "preis_stck", "order_summe"),
            ( "Id", "Datum", "Name", "WKN", "ISIN", "Ticker", "Depot", "Stück", "Preis/Stck", "Ordersumme" ) )
        return tm

    def insertOrderAndUpdateDepotData( self, delta:XDelta, deppos:XDepotPosition ):
        """
        Fügt eine Order (Kauf oder Verkauf) in Tabelle delta ein.
        Danach werden die deppos-Attribute stueck, gesamtkaufpreis, preisprostueck und ggf. maxKaufpreis oder minKaufpreis
        geändert. Außerdem werden gesamtwert_aktuell und delta_proz neu berechnet.
        :param delta: die Daten der neuen Order
        :param deppos: die Depotposition, die sich durch die Order verändert
        :return:
        """
        delta.order_summe = abs( round( delta.preis_stck * delta.delta_stck, 2 ) )
        self._db.insertDelta( delta )
        if delta.delta_stck < 0:
            # es ist ein Verkauf, jetzt muss die verkaufte Stückzahl in einen oder mehrere Kauf-Sätze
            # gebucht werden
            self._bookShareSale( delta, deppos )
        self._db.commit()
        self._provideOrderData( deppos )
        self._provideGesamtwertAndDelta( deppos )

    def _bookShareSale( self, verkauf:XDelta, deppos:XDepotPosition ):
        """
        nach einem Anteilsverkauf muss die Anzahl der verkauften Stücke auf die vorherigen Käufe verteilt werden.
        Beispiel:
        Verkauft wurden 100 Stück.
        Es gibt 2 Käufe, der ältere mit 80 Stück, der jüngere mit 40 Stück.
        Gem FIFO-Prinzip müssen nun im älteren Kauf 80 verkaufte Stück eingetragen werden und im neueren Kauf
        20 Stück.
        Nach diesen Datenbank-Updates müssen in der Depotpositon <deppos> die Felder stueck und einstandswert_restbestand
        neu berechnet werden.
        :param verkauf:
        :param deppos:
        :return:
        """
        # Zuerst die Kauf-Orders dieses Wertpapiers holen:
        deltas:List[XDelta] = self._db.getKaeufe( verkauf.wkn ) # sortiert nach Kaufdatum aufsteigend, also ältester Kauf oben
        verkaufte_stuecke = verkauf.delta_stck * -1
        rest = verkaufte_stuecke
        deppos.stueck = 0
        deppos.einstandswert_restbestand = 0
        for delta in deltas:
            vfgbar = delta.delta_stck - delta.verkauft_stck
            if vfgbar >= rest:
                # es gibt in diesem Satz (Kauf) soviele verfügbare Stücke, dass der Verkauf aus ihnen bedient
                # werden kann
                delta.verkauft_stck += rest
                rest = 0
            else:
                # nicht genügend Stücke für den Verkauf vorhanden. Die vorhandenen in verkauft_stck eintragen.
                delta.verkauft_stck += vfgbar
                rest -= vfgbar
            self._db.updateDeltaVerkaufteStuecke( delta.id, delta.verkauft_stck )
            deppos.stueck += rest
            deppos.einstandswert_restbestand += (rest * delta.preis_stck)
            if rest == 0:
                break
        if deppos.stueck > 0:
            # Durchschnittl. Preis pro Stück:
            deppos.preisprostueck = round( deppos.einstandswert_restbestand / deppos.stueck, 2 )



def test():
    logic = InvestMonitorLogic()
    lastPrice = logic.getKursAktuellInEuro( "PRIJ.L" )
    #poslist = logic.getDepotPositions()
    #print( poslist )

    # logic.saveMyHistories()

    poslist, dummy = logic.getDepotPositions()
    print( poslist )

    # df = logic.loadMyHistories()
    # close:DataFrame = df["Close"]
    # cols:Index = close.columns # <-- ticker-collection
    # print( cols[0] ) # <-- ticker
    # eusri:DataFrame = close["EUSRI.PA"]
    # print( eusri )

    #series = logic.getSeriesHistoryByPeriod( "WTEM.DE", SeriesName.Close, Period.fiveDays, Interval.oneDay )
    #print( series )