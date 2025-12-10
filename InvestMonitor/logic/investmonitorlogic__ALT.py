
import datetime
import glob
import json
import math
import os
from enum import StrEnum, IntEnum
from operator import attrgetter
from typing import List, Dict, Iterable, Tuple

import numpy as np
import pandas
import requests
from pandas import DataFrame, Series, Timestamp
from yfinance.scrapers.quote import FastInfo

import datehelper
from base.basetablemodel import BaseTableModel, SumTableModel
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from ftp import FtpIni, Ftp
from interface.interfaces import XDepotPosition, XDelta, XDetail, XDividend
from imon.definitions import DATABASE_DIR, DEFAULT_PERIOD, DEFAULT_INTERVAL
from logic.exchangerates import ExchangeRates
from simpledatatable import SimpleDataTable


# class WorkerSignals( QObject ):
#     finished = Signal()
#     error = Signal( tuple )
#     result = Signal( object )
#
# ##############################################################
# class Worker( QRunnable ):
#     def __init__( self, fn, wkn_ticker_list:List[Dict], allOrders:List[XDelta] ):
#         super( Worker, self ).__init__()
#         # Store constructor arguments (re-used for processing)
#         self.fn = fn
#         self._wkn_ticker_list = wkn_ticker_list
#         self._allOrders = allOrders
#         self.signals = WorkerSignals()
#
#     @Slot()
#     def run( self ):
#         try:
#             result = self.fn( self._wkn_ticker_list, self._allOrders )
#         except:
#             traceback.print_exc()
#             exctype, value = sys.exc_info()[:2]
#             self.signals.error.emit( (exctype, value, traceback.format_exc()) )
#         else:
#             self.signals.result.emit( result )  # Return the result of the processing
#         finally:
#             self.signals.finished.emit()  # Done

####################################################################
class InvestMonitorLogic:
    class TickerWknListSortBy(IntEnum):
        TICKER = 0
        WKN = 1
        UNK = -1
    # allHistories enthält den von yfinance zurückgelieferten DataFrame.
    # Es ist eine class variable, weil für alle Instanzen nur einmal die Histories geladen werden sollen:
    allHistories: DataFrame = None
    # Liste mit Tuples [(Ticker, WKN), (Ticker, WKN),...]
    ticker_wkn_list:List[Tuple] = None
    # Liste mit *allen* Depot-Positionen, die angezeigt werden sollen (depotposition.flag_displ == 1)
    poslist:List[XDepotPosition] = None
    # Liste mit Positionen und der Währung [(Ticker, Währung), (Ticker, Währung),...]
    tickersAndCurrencies: List[Tuple] = None
    # gibt Auskunft, wie die Ticker- und WKN-Liste gerade sortiert ist
    ticker_wkn_list_sorted_by = TickerWknListSortBy.UNK
    # alle Käufe:
    allPurchases:List[XDelta] = list()
    # alle Verkäufe:
    allSales:List[XDelta] = list()

    @staticmethod
    def getTickerList( sortByTicker=True ):
        if sortByTicker and InvestMonitorLogic.ticker_wkn_list_sorted_by != InvestMonitorLogic.TickerWknListSortBy.TICKER:
            InvestMonitorLogic.sortTickerWknList( InvestMonitorLogic.TickerWknListSortBy.TICKER )
        return [tpl[0] for tpl in InvestMonitorLogic.ticker_wkn_list]

    @staticmethod
    def getWknList( sortByWkn=True ):
        if sortByWkn and InvestMonitorLogic.ticker_wkn_list_sorted_by != InvestMonitorLogic.TickerWknListSortBy.WKN:
            InvestMonitorLogic.sortTickerWknList( InvestMonitorLogic.TickerWknListSortBy.WKN )
        return [tpl[1] for tpl in InvestMonitorLogic.ticker_wkn_list]

    @staticmethod
    def sortTickerWknList( sortBy:TickerWknListSortBy ):
        InvestMonitorLogic.ticker_wkn_list.sort( key=lambda x: x[sortBy.value] )
        InvestMonitorLogic.ticker_wkn_list_sorted_by = sortBy

    @staticmethod
    def getTicker( wkn: str ) -> str:
        for tpl in InvestMonitorLogic.ticker_wkn_list:
            if wkn == tpl[1]:
                return tpl[0]
        raise Exception( "WKN '%s' nicht in der Ticker-/WKN-Liste gefunden." % wkn )

    @staticmethod
    def getWkn( tickr: str ) -> str:
        for tpl in InvestMonitorLogic.ticker_wkn_list:
            if tickr == tpl[0]:
                return tpl[1]
        raise Exception( "Ticker '%s' nicht in der Ticker-/WKN-Liste gefunden." % tickr )

    def __init__( self ):
        pandas.options.mode.copy_on_write = True
        self._db = InvestMonitorData()
        self._exchangeRates = ExchangeRates( self._db )
        self._tickerHist = TickerHistory()  # Wrapper um die yfinance-Schnittstelle
        self._defaultPeriod = DEFAULT_PERIOD #Period.oneYear
        self._defaultInterval = DEFAULT_INTERVAL
        self._minPeriod = Period.oneDay
        self._minInterval = Interval.oneMin

    # def initExchangeRatesDatabase( self, yyyy_mm_dd_from:str, cntDaysBackwards:int ):
    #     self._exchangeRates.initDatabase( yyyy_mm_dd_from, cntDaysBackwards )

    def convert( self, yyyy_mm_dd:str, fromCurr:str, targetCurr:str, value:float ) -> float:
        """
        Rechnet den Betrag value, der in der Währung from_curr (z.B. "USD") angegeben ist,
        in die Währung to_curr (z.B. "EUR") um, auf Basis der exchange rates vom Datum yyyy_mm_dd.
        Umrechnungen sind möglich zwischen EUR, CHF, GBP, USD.
        """
        if pandas.isna( value ):
            return value
        val = self._exchangeRates.convert( fromCurr, targetCurr, yyyy_mm_dd, value )
        return val

    def convertMany_( self, fromCurr:str, targetCurr:str, dates:List, fromValues:List ) -> List:
        """
        Wandelt die Beträge in <fromValues> von <fromCurr> in <targetCurr> um.
        Gibt eine neue Liste mit den umgewandelten Beträgen zurück. Diese ist genauso lang und in der gleichen
        Reihenfolge wie <fromValues>
        """
        targetValues = [self.convert( str(ts)[:10], fromCurr, targetCurr, val ) for ts, val in zip(dates, fromValues )]
        return targetValues

    def convertMany( self, fromCurr:str, targetCurr:str, fromValues:Series ) -> Series:
        """
        Wandelt die Beträge in <fromValues> von <fromCurr> in <targetCurr> um.
        Gibt eine neue Series mit den umgewandelten Beträgen zurück. Diese ist genauso lang und in der gleichen
        Reihenfolge wie <fromValues>. Auch der Index ist gleich.
        """
        targetValues = [self.convert( str(ts)[:10], fromCurr, targetCurr, val ) for ts, val in zip(fromValues.index, fromValues )]
        return pandas.Series(targetValues, index=fromValues.index)

    @staticmethod
    def exportDatabase():
        ftpIni = FtpIni( "./ftp.ini" )
        ftp = Ftp( ftpIni )
        ftp.connect()
        ftp.upload( "invest.db", "invest.db" )
        ftp.quit()

    def getDepotPositions( self, period:Period, interval:Interval, TEST=False ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der gewünschten Periode und
        dem gewünschten Zeitintervall
        :return:
        """
        self._ensureStaticDataLoaded()
        # Wertpapierdaten in Positionen eintragen (Kursverlauf, Dividenden etc.)
        poslist = self.provideTickerHistories( InvestMonitorLogic.poslist, period, interval )
        return poslist

    @staticmethod
    def provideFastInfo( poslist:Iterable[XDepotPosition] ):
        """
        Wird von getDepotPositions() in einem separaten Thread aufgerufen und versorgt
        in aas Attribut fastInfo in allen übergebenen XDepotPositon-Objekten
        :param poslist: Iterable of XDepotPosition
        :return:
        """
        for deppos in poslist:
            deppos.fastInfo =TickerHistory.getFastInfo( deppos.ticker )

    def _convertToEUR( self, curr:str, closeValuesOrig:Series, dividendsOrig:Series ) -> List:
        def handleGBp( val ):
            if val and val > 0:
                return val / 100 # GBP
            else:
                return None

        # convertToEuro( closeValues und dividends )
        if curr == "GBp":  # pence
            curr = "GBP"  # pound
            closeValuesOrig = [handleGBp(val) for val in closeValuesOrig if val and val > 0 ]
            dividendsOrig = [handleGBp(val) for val in dividendsOrig]

        if closeValuesOrig.isna().all():
            rows, cols = closeValuesOrig.shape
            closeValuesEUR:Series = pandas.Series([np.nan]*rows, index=closeValuesOrig.index)
        else:
            closeValuesEUR:Series = self.convertMany( fromCurr=curr, targetCurr="EUR",
                                                     fromValues=closeValuesOrig )
        if dividendsOrig.isna().all():
            rows, cols = closeValuesOrig.shape
            dividendsEUR:Series = pandas.Series([np.nan]*rows, index=dividendsOrig.index)
        else:
            dividendsEUR:Series = self.convertMany( fromCurr=curr, targetCurr="EUR", fromValues=dividendsOrig )
        return [closeValuesEUR, dividendsEUR]

    # def _getHistoriesFromAPIandConvert( self, tickersAndCurrencies:list ) -> DataFrame:
    #     """
    #     Holt die Histories der in tickerlist enthaltenen Ticker im max. Umfang (5 J., je Tag) aus der yfinance-Schnittstelle,
    #     entfernt die hier nicht benötigten Spalten und dreht den Index um, sodass nicht die Spaltennamen führend sind
    #     sondern die Ticker.
    #     Es werden vier Spalten CloseEUR und DividendsEUR, SalesEUR und PurchasesEUR hinzugefügt.
    #     Wenn die Währung nicht EUR ist, werden alle Werte  aus der Close- und der Dividens-Spalte umgerechnet
    #     und in die neuen Spalten eingetragen.
    #     Der so modifizierte DataFrame wird zurückgeliefert.
    #     """
    #     def deleteOlderTickerHistories():
    #         wildcard_pattern = "tickerhistories_*"
    #         full_path_pattern = os.path.join( dev_path, wildcard_pattern )
    #         files_to_delete = glob.glob( full_path_pattern )
    #         for file in files_to_delete:
    #             try:
    #                 os.remove( file )
    #                 print( f"Deleted: {file}" )
    #             except OSError as e:
    #                 print( f"Error deleting {file}: {e}" )
    #
    #     dev_path = "/home/martin/Projects/python/InvestMonitor/logic/"
    #     tickerlist = [t[0] for t in tickersAndCurrencies]
    #     try:
    #         if dev_path.lower() in __file__.lower(): # wir sind in der Entwicklungsumgebung
    #             today = datehelper.getTodayAsIsoString()
    #             file_path = dev_path + "tickerhistories_" + today + ".txt"
    #             if not os.path.exists( file_path ):
    #                 deleteOlderTickerHistories()
    #                 tickHists:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist, Period.fiveYears,
    #                                                                                    Interval.oneDay )
    #                 tickHists.to_pickle( file_path )
    #             else:
    #                 tickHists:DataFrame = pandas.read_pickle( file_path )
    #         else:
    #             tickHists: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist, Period.fiveYears,
    #                                                                                 Interval.oneDay )
    #         # Spalten rauswerfen, die wir nicht brauchen (wir brauchen nur Close und Dividends):
    #         tickHists.drop( ["Capital Gains", "High", "Low", "Open", "Stock Splits", "Volume"],
    #                                    axis=1, inplace=True )
    #         # Rows entfernen, wo Spaltenwerte "NaN" sind:
    #         ## nein - da bleiben kaum Zeilen übrig (erst ab März 2025)tickHists = tickHists.dropna()
    #         # alle Spalten durchgehen und für jede Spalte:
    #         #      if series.isnull().all(): ...
    #         # Index umdrehen, damit der Ticker führend wird:
    #         tickHists.columns = tickHists.columns.swaplevel( 0, 1 )
    #         tickHists.sort_index( axis=1, level=0, inplace=True )
    #     except Exception as ex:
    #         raise ex
    #
    #     # Für jeden Ticker...
    #     # ...das DepotPosition-Objekt ermitteln
    #     # ...wenn die Währung nicht Euro ist, die Spalten Close und Dividends ergänzen um zwei Spalten CloseEUR und
    #     #    DividendsEUR
    #     # ...das tickHists-Objekt um die Spalten SalesEUR und PurchasesEUR ergänzen und dort die im Zeitraum (5 J.)
    #     #    getätigten (Ver-)Käufe eintragen
    #     for ticker, curr in tickersAndCurrencies:
    #         # egal, was man macht, die Warnung...
    #         # A value is trying to be set on a copy of a slice from a DataFrame.
    #         # Try using .loc[row_indexer,col_indexer] = value instead
    #         #...kommt immer
    #         if curr != "EUR":
    #             closeValuesEUR, dividendsEUR = self._convertToEUR( curr,
    #                                                                tickHists[(ticker, "Close")],
    #                                                                tickHists[(ticker, "Dividends")] )
    #             tickHists.loc[:, (ticker, "CloseEUR")] = pandas.Series( closeValuesEUR, index=tickHists.index )
    #             tickHists.loc[:, (ticker, "DividendsEUR")] = pandas.Series( dividendsEUR, index=tickHists.index )
    #         else:
    #             tickHists.loc[:, (ticker, "CloseEUR")] = tickHists[(ticker, "Close")]
    #             tickHists.loc[:, (ticker, "DividendsEUR")] = tickHists[(ticker, "Dividends")]
    #
    #         rows, cols = tickHists.shape
    #         # Spalten für die Käufe hinzufügen
    #         tickHists.loc[:, (ticker, "SalesEUR")] = pandas.Series( [0] * rows, dtype=float, index=tickHists.index )
    #         tickHists.loc[:, (ticker, "PurchasesEUR")] = pandas.Series( [0] * rows, dtype=float, index=tickHists.index )
    #     return tickHists

    def _getHistoriesFromAPI( self, tickersAndCurrencies: list ) -> DataFrame:
        """
        Holt die Histories der in tickerlist enthaltenen Ticker im max. Umfang (5 J., je Tag) aus der yfinance-Schnittstelle,
        entfernt die hier nicht benötigten Spalten und dreht den Index um, sodass nicht die Spaltennamen führend sind
        sondern die Ticker.
        Der so modifizierte DataFrame wird zurückgeliefert.
        """

        def deleteOlderTickerHistories():
            wildcard_pattern = "tickerhistories_*"
            full_path_pattern = os.path.join( dev_path, wildcard_pattern )
            files_to_delete = glob.glob( full_path_pattern )
            for file in files_to_delete:
                try:
                    os.remove( file )
                    print( f"Deleted: {file}" )
                except OSError as e:
                    print( f"Error deleting {file}: {e}" )

        dev_path = "/home/martin/Projects/python/InvestMonitor/logic/"
        tickerlist = [t[0] for t in tickersAndCurrencies]
        try:
            if dev_path.lower() in __file__.lower():  # wir sind in der Entwicklungsumgebung
                today = datehelper.getTodayAsIsoString()
                file_path = dev_path + "tickerhistories_" + today + ".txt"
                if not os.path.exists( file_path ):
                    deleteOlderTickerHistories()
                    tickHists: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist, Period.fiveYears,
                                                                                        Interval.oneDay )
                    tickHists.to_pickle( file_path )
                else:
                    tickHists: DataFrame = pandas.read_pickle( file_path )
            else:
                tickHists: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist, Period.fiveYears,
                                                                                    Interval.oneDay )
            # Spalten rauswerfen, die wir nicht brauchen (wir brauchen nur Close und Dividends):
            tickHists.drop( ["Capital Gains", "High", "Low", "Open", "Stock Splits", "Volume"],
                            axis=1, inplace=True )
            # Index umdrehen, damit der Ticker führend wird:
            tickHists.columns = tickHists.columns.swaplevel( 0, 1 )
            tickHists.sort_index( axis=1, level=0, inplace=True )
        except Exception as ex:
            raise ex

        return tickHists

    def _loadOrders( self ):
        allOrders:List[XDelta] = self._db.getAllDeltas()
        for order in allOrders:
            if order.verkauft_stck > 0:
                InvestMonitorLogic.allSales.append( order )
            else:
                InvestMonitorLogic.allPurchases.append( order )

    def _getSales( self, ticker:str ) -> Series:
        l = list()
        for sale in InvestMonitorLogic.allSales:
            pass

    def _ensureStaticDataLoaded( self ):
        """
        Prüft, ob die Daten, die für alle Instanzen von InvestMonitorLogic gelten, geladen sind.
        Wenn nein, werden sie geladen.
        Es handelt sich um:
            - die History-Daten, die durch einen Aufruf der yfinance-API ermittelt werden
            - die Ticker- und WKN-Liste, die aus der Datenbank geholt wird
            - die Ticker-Währung-Liste
            - die Kaufs- und Verkaufsdaten  aus der Datenbank
        """
        if InvestMonitorLogic.allHistories is None:
            InvestMonitorLogic.poslist = poslist = self._db.getDepotPositions()
            # Die one and only Ticker- und WKN-Liste laden:
            InvestMonitorLogic.ticker_wkn_list = [(pos.ticker, pos.wkn) for pos in poslist]
            # die Ticker-Histories von der yfinance API abrufen, vorher die Ticker und Währungen ermitteln:
            InvestMonitorLogic.tickersAndCurrencies = [(pos.ticker, pos.waehrung) for pos in poslist]
            # Aufruf der Schnittstelle. In dieser Methode wird auch die Konvertierung von Fremdwährung in EUR
            # vorgenommen, wenn nötig.
            InvestMonitorLogic.allHistories = self._getHistoriesFromAPI( InvestMonitorLogic.tickersAndCurrencies )
            # alle Deltas in die Listen allSales bzw. allPurchases laden:
            self._loadOrders()

    def provideTickerHistories( self, poslist: List[XDepotPosition], period: Period, interval: Interval ) -> List[XDepotPosition]:
        """
        In dieser Methode wird der Gesamt-History-Bestand (über 5 J.) lediglich angepasst an Änderungen von period und
        interval.
        Sollte der Gesamt-History-Bestand noch nicht ermittelt worden sein (beim ersten Aufruf), erfolgt zuerst ein
        Aufruf der yfinance-Schnittstelle und die Käufe und Verkäufe werden geladen.
        allHistories enthält hier nur die Spalten Close und Dividends
        """
        self._ensureStaticDataLoaded()

        # den relevanten Ausschnitt (period, interval) aus der Gesamtmenge tickHists ermitteln (betrifft ALLE Ticker,
        # Spalten Close und Dividends):
        tickHistsPart:DataFrame = self._getTickHistsPart( period, interval )
        dt_min, dt_max = InvestMonitorLogic._getMinAndMaxDatetime(tickHistsPart.index)
        for deppos in poslist:
            # die Käufe und Verkäufe in deppos laden, die in period angefallen sind:
            
            # in tickHistsPart die Tage ergänzen, die wegen <interval> nicht mehr enthalten sind,
            # an denen aber für dieses Wertpapier Dividenden gezahlt wurden:
            # todo ...
            # in tickHistsPart die Tage ergänzen, die wegen <interval> nicht mehr enthalten sind,
            # an denen aber (Ver-)Käufe dieses Wertpapiers stattgefunden haben:
            # todo ...
            deppos.closePrices = tickHistsPart[(deppos.ticker, "Close")]
            deppos.closePrices.dropna()
            deppos.closePricesEUR = deppos.closePrices.copy() # müssen wir noch konvertieren, wenn die Währung ungleich EUR
            # Behandlung der Dividenden:
            deppos.dividendsEUR = tickHistsPart[(deppos.ticker, "Dividends")] # wir nehmen erstmal an, divs in EUR
            if deppos.waehrung == "EUR":
                pass
            deppos.period = period
            deppos.interval = interval
            last_price = deppos.closePrices.iloc[-1]  # todo: vllt. ist es besser, hier einen Zugriff auf FastInfo zu  machen
            previous_close = deppos.closePrices.iloc[-2]
            if pandas.isna(last_price): # passiert manchmal, dass manche Close-Preise nicht versorgt sind, z.B. bei wkn == DBX1SM
                last_price = previous_close
                previous_close = deppos.closePrices.iloc[-3]
            deppos.delta_kurs_percent = self._getDeltaKursPercent( last_price, previous_close )
            if deppos.waehrung == "EUR":
                deppos.kurs_aktuell = last_price
            else:
                deppos.kurs_aktuell = self.convert( yyyy_mm_dd=str(deppos.closePrices.index[-1])[:10],
                                                    fromCurr=deppos.waehrung, targetCurr="EUR", value=last_price )
            # eine neue Series für die Dividenden erzeugen, die nur die Datümer enthält, an denen Dividenden bezahlt wurden.
            # Diese komprimierte Dividenden-Spalte wird deppos.dividendsEUR zugewiesen.
            # Hintergrund: Dividenden machen wertmäßig nur einen Bruchteil des Kurses aus und müssen deshalb in einer
            # eigenen Grafik dargestellt werden.
            first_kurs_period = deppos.closePrices.iloc[0] # todo: das muss doch sicher .closePricesEUR heißen?!
            # die Dividenden-Attribute von deppos versorgen; diese können sich je nach period ändern.
            self._provideDividends( deppos, first_kurs_period, deppos.history["DividendsEUR"] )
            # Den Feldern .allSales und .allPurchases die entsprechenden *verdichteten* Spalten des History-DataFrames zuweisen.
            # Diese neuen Series enthalten nur die Datümer, an denen Käufe oder Verkäufe stattfanden.
            s = deppos.history["PurchasesEUR"]
            deppos.kaufKurse = s[s != 0]
            s = deppos.history["SalesEUR"]
            deppos.verkaufKurse = s[s != 0]
        return poslist

    @staticmethod
    def _getMinAndMaxDatetime( indexlist ) -> (datetime.datetime, datetime.datetime):
        ts0 = indexlist[0]
        ts1 = indexlist[len(indexlist)-1]
        if ts0 < ts1:
            return ts0, ts1
        else:
           return ts1, ts0

    # @staticmethod
    # def _getIndexRange(period:Period, interval:Interval) -> Series:
    #     from_datetime, curr_datetime = InvestMonitorLogic._getStartAndCurrentDatetime(period)
    #     all_days = InvestMonitorLogic.allHistories.index
    #     days_segment = all_days[from_datetime:curr_datetime]
    #     days_part = InvestMonitorLogic._getEveryNthDay(days_segment, interval)
    #     return days_part

    @staticmethod
    def _getStartAndCurrentDatetime(period:Period) -> (datetime.datetime, datetime.datetime):
        """
        Ermittelt aufgrund von period den Start-Timestamp und current date als Timestamp
        period kann sein: oneDay, fiveDays, oneMonth, threeMonths, sixMonths, currentYear,
                          oneYear, twoYears, threeYears, fiveYears
        @returns: from_datetime, curr_datetime
        """
        curr_date = datehelper.getCurrentDate()
        year, month, day = curr_date.year, curr_date.month, curr_date.day
        curr_datetime = datetime.datetime( year, month, day )
        dy, dd = 0, 0
        if period == Period.oneYear:
            dy = -1
        elif period == Period.twoYears:
            dy = -2
        elif period == Period.threYears:
            dy = -3
        elif period == Period.fiveYears:
            dy = -5
        if dy == 0:
            if period == Period.oneMonth:
                dd = -30
            elif period == Period.threeMonths:
                dd = -90
            elif period == Period.sixMonths:
                dd = -180
            elif period == Period.oneDay:
                dd = -1
            elif period == Period.fiveDays:
                dd = -5
            if dd == 0:
                if period == Period.currentYear:
                    from_datetime = datetime.datetime( year, 1, 1 )
                else:
                    raise ValueError( "InvestMonitorLogic._getStartAndCurrentDatetime(): unknown period" + str( period ) )
            else:
                from_datetime = datehelper.addDays( curr_date, dd )
        else:
            from_datetime = datehelper.addYears( curr_date, dy )

        return from_datetime, curr_datetime

    @staticmethod
    def _getEveryNthDay(days_segment, interval) -> Series:
        # interval auswerten:
        # wenn interval == oneDay, brauchen wir nichts filtern; jede Row wird verwendet.
        # wenn interval != '1d' brauchen wir nur jede n-te Row. Dieses n muss ermittelt werden:
        if interval == Interval.oneDay:
            days_part = days_segment
        elif interval in (Interval.fiveDays, Interval.oneWeek):
            days_part = days_segment[-1::-5]  # starte "hinten", gehe jeweils 5 nach oben
        elif interval == Interval.oneMonth:
            days_part = days_segment[-1::-20]  # ungefähr. Im Monat durchschn. 20 Handelstage.
        elif interval == Interval.threeMonths:
            days_part = days_segment[-1::-60]  # starte "hinten", gehe jeweils 60 noch oben
        else:
            raise ValueError( "InvestMonitorLogic._getTickHistsPart(): unbekanntes Intervall" )

        return days_part

    @staticmethod
    def _getTickHistsPart( period:Period, interval:Interval ) -> DataFrame:
        """
        tickHists enthält ALLE Ticker mit ihren Werten für jeden Tag innerhalb eines 5-JAhres-Zeitraums.
        Je nach period und interval wird hier der zutreffende Teil der tickHists-Rows selektiert und zurückgeliefert.
        period kann sein: oneDay, fiveDays, oneMonth, threeMonths, sixMonths, currentYear,
                          oneYear, twoYears, threeYears, fiveYears
        interval kann sein: oneDay, fiveDays, oneWeek, oneMonth, threeMonths
        """
        # Schritt 1: Die Rows holen, die in <period> fallen
        from_datetime, curr_datetime = InvestMonitorLogic._getStartAndCurrentDatetime(period)
        tickHistsPartAllDays = InvestMonitorLogic.allHistories.loc[from_datetime:curr_datetime] # tickHistsPartAllDays
                                                                                # enthält jetzt alle Tage der period
        # interval auswerten:
        # wenn interval == oneDay, brauchen wir nichts filtern; jede Row wird verwendet.
        # wenn interval != '1d' brauchen wir nur jede n-te Row. Dieses n muss ermittelt werden:
        if interval == Interval.oneDay:
            tickHistsPart = tickHistsPartAllDays
        elif interval in (Interval.fiveDays, Interval.oneWeek ):
            tickHistsPart = tickHistsPartAllDays[-1::-5] # starte "hinten", gehe jeweils 5 nach oben
        elif interval == Interval.oneMonth:
            tickHistsPart = tickHistsPartAllDays[-1::-20] # ungefähr. Im Monat durchschn. 20 Handelstage.
        elif interval == Interval.threeMonths:
            tickHistsPart = tickHistsPartAllDays[-1::-60] # starte "hinten", gehe jeweils 60 noch oben
        else:
            raise ValueError( "InvestMonitorLogic._getTickHistsPart(): unbekanntes Intervall" )

        # Möglicherweise haben wir Tage mit Dividendenzahlungen und/oder Käufen/Verkäufen eliminiert.
        # Die müssen wir wieder einfügen. Dazu gehen wir tickHistsPartAllDays Zeile für Zeile durch, und prüfen,
        # ob in den Dividenden-, Käufe- oder Verkäufe-Spalten Werte > 0 eingetragen sind.
        # Wenn ja, überprüfen wir, ob diese Zeile in tickHistsPart enthalten ist.
        # Wenn nicht, fügen wir sie dort ein.
        # muxlist = tickHistsPartAllDays.columns
        # muxlistDivs = [mux for mux in muxlist if mux[1] in ("DividendsEUR", "SalesEUR", "PurchasesEUR")]
        # for ts in tickHistsPartAllDays.index:
        #     for mux in muxlistDivs:
        #         val = tickHistsPartAllDays.loc[ts, mux]
        #         if val > 0:
        #             #print( "row-index: ", ts, "; col-index: ", mux, "; val: ", val )
        #             # ist dieser Timestamp in tickHistsPart enthalten? Wenn nein, einfügen:
        #             if not ts in tickHistsPart.index:
        #                 row:Series = tickHistsPartAllDays.loc[ts]
        #                 tickHistsPart.loc[ts] = row
        #             break
        # tickHistsPart = tickHistsPart.sort_index()
        return tickHistsPart

    @staticmethod
    def _checkForNaN( df:DataFrame ) -> DataFrame:
        #row:DataFrame = df.tail(1) # damit haben wir die letzte Zeile des DataFrame, also die letzten Values aller Series (columns)
        row2:Series = df.iloc[-1]
        #row3:DataFrame = df.iloc[-1:]
        for name, cellValue in row2.items():
            # name: Spaltenkopf, z.B. EZTQ.F
            # cellValue: value des Items
            #print( "name: ", name, "cellValues: ", cellValue )
            if math.isnan( cellValue ):
                df = df[:-1]
                break
        return df

    def _provideDividends( self, deppos, first_kurs_period:float, dividends:Series ) -> None:
        """
        Ersatz für _provideWertpapierData.
        Versorgt werden im deppos-Objekt folgende Attribute:
        .dividendsEUR, .dividend_yield, .dividend_period, .dividend_paid_period
        """
        # Neues Series nur für die Datümer, an denen Dividenden gezahlt wurden:
        dividendsFiltered = dividends[dividends > 0]
        deppos.dividendsEUR = dividendsFiltered
        deppos.dividend_yield = 0.0

        if deppos.kurs_aktuell == 0:
            print( deppos.wkn, "/", deppos.ticker,
                   ": _provideWertpapierData(): call to getKursAktuellInEuro() failed.\nNo last_price availabel." )

        deppos.dividend_period = self._getSumDividends( deppos.dividendsEUR )  # Summe der Div. PRO STÜCK während d. Periode
        if deppos.dividend_period > 0:
            deppos.dividend_yield = self._computeDividendYield( first_kurs_period, deppos.dividend_period )
        self._provideGesamtwertAndDelta( deppos )
        deppos.dividend_paid_period = \
            self._getPaidDividends( deppos.dividendsEUR, deppos.allDeltas )  # Summe der Dividendenzahlungen,
                                                        # die während d. Perdiode auf meinen Bestand gezahlt wurden

    def _getPaidDividends( self, dividends:Series, deltas:List[XDelta], callback=None ) -> int:
        """
        Ermittelt die Dividendenzahlungen, die für <deppos> gemäß Eintragungen in <dividends> angefallen sind.
        Für jede Dividendenzahlung wird nur der zum Zahlungszeitpunkt vorhandene Depotbestand berücksichtigt.
        :param dividends: Die Dividenden-Serie. Es wird vorausgesetzt, dass sie in Euro übergeben wird.
        :param deltas: Alle Orders, die sich auf <wkn> beziehen
        :param callback: Funktion, die aufgerufen wird für jede Dividendensumme, die durch _computeDividendOnBestand
                        ausgerechnet wurde.
                        Die Callback-Funktion muss 3 Argumente empfangen: den Div.-Zahltag (ISO), die Div. pro Stück
                        und die Gesamt-Dividende, die auf den am Zahltag vorhandenen Bestand ausgezahlt wurde.
        :return:
        """
        if dividends.isna().all():
            return 0

        deltas.sort( key=attrgetter( "delta_datum" ) )
        sum_dividends = 0
        for pay_ts, value in dividends.items():
            if pandas.isna( value ) or value <= 0:
                continue
            #print( "paid: ", str(pay_ts)[:10], ": ", value )
            # den Depotbestand der Position <deppos> zum Datum <paydate> ermitteln:
            div_pro_stck = float( value )
            pay_day = str( pay_ts )[:10]
            div = self._computeDividendOnBestand( deltas, div_pro_stck, pay_day )
            if callback:
                callback( pay_day, div_pro_stck, div )
            sum_dividends += div
        return sum_dividends

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
        if not dividend or dividend <= 0:
            return 0
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
        if not deppos.kurs_aktuell: # kann passieren, wenn yfinance nicht auf der Höhe ist, z.B. bei WKN == DBX1SM
            deppos.kurs_aktuell = 0

        deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
        #if deppos.gesamtkaufpreis > 0:
        if deppos.einstandswert_restbestand > 0:
            deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.einstandswert_restbestand - 1) * 100, 2 )

    @staticmethod
    def _getSumDividends( dividends: Series ) -> float:
        if dividends.isna().all():
            return 0
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
        self.provideTickerHistories([x,], period, interval)
        #df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( x.ticker, period, interval )
        #self._provideWertpapierData( x, df[SeriesName.Close.value], df[SeriesName.Dividends.value] )
        x.period = period
        x.interval = interval

    def updateKursAndDivYield( self, deppos:XDepotPosition ):
        self._provideFastInfoData( deppos )
        if deppos.kurs_aktuell > 0 and deppos.dividend_period > 0:
            # Wahrscheinlich ist deppos.history aufsteigend sortiert, aber wir verlassen uns lieber nicht darauf:
            ts0 = deppos.history.index[0]
            ts1 = deppos.history.index[1]
            if ts0 < ts1:
                first_kurs_period = deppos.history["Close"].head(1).values[0]
            else:
                first_kurs_period = deppos.history["Close"].tail(1).values[0]
            deppos.dividend_yield = self._computeDividendYield( first_kurs_period, deppos.dividend_period )

    @staticmethod
    def _computeDividendYield( kurs:float, dividend:float ) -> float:
        if not dividend or dividend <= 0: return 0
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

    @staticmethod
    def _getDeltaKursPercent( last_price:float, previous_close:float ) -> float:
        if not previous_close or previous_close == 0:
            return 0
        deltaPrice = last_price - previous_close
        # Verhältnis des akt. Kurses zum Schlusskurs des Vortages:
        delta_kurs_percent = round( deltaPrice / previous_close * 100, 2 )
        return delta_kurs_percent

    def _provideFastInfoData( self, deppos:XDepotPosition ) -> str:
        """
        Ermittelt die yfinance.Ticker.fast_info des Wertpapiers und schreibt sie in <deppos>
        Transformiert den letzten Kurs (fast_info.last_price) in EUR, wenn er nicht in EUR geliefert wird.
        :param deppos: das XDepotPosition-Objekt, das mit den FastInfo-Daten versorgt werden soll.
        :return: die ursprüngliche Währung (EUR oder Fremdwährung, die konvertiert wurde)
        """
        fastInfo: FastInfo = self._tickerHist.getFastInfo( deppos.ticker )
        if fastInfo:
            deppos.fastInfo = fastInfo
            last_price = fastInfo.last_price
            currency = str( fastInfo.currency )
            if currency != "EUR":
                try:
                    last_price = self.convert( datehelper.getCurrentDateIso(), currency, "EUR", last_price )
                except ValueError:
                    # wahrscheinlich ist heute Wochenende, deshalb keine Conversions verfügbar.
                    # Deshalb Umwandlung über TickerHistory.convertToEuro:
                    last_price = TickerHistory.convertToEuro(last_price, currency)
            deppos.kurs_aktuell = round( last_price, 3 )
            try:
                # wegen des lazy loading der fast_info geht das hin und wieder schief
                previous_close = fastInfo.previous_close
                deppos.delta_kurs_percent = self._getDeltaKursPercent( fastInfo.last_price, previous_close )
                # if previous_close:
                #     deltaPrice = fastInfo.last_price - previous_close
                #     # Verhältnis des akt. Kurses zum Schlusskurs des Vortages:
                #     deppos.delta_kurs_1_percent = round( deltaPrice / previous_close * 100, 2 )
                # else:
                #     deppos.delta_kurs_1_percent = 0
                #     print( deppos.ticker, ": fastInfo.previous_close is None." )
            except Exception as ex:
                print( deppos.ticker, ": Zugriff auf Feld previous_close nicht möglich." )
            return currency
        else:
            print( "Ticker '%s':\nNo FastInfo available" % deppos.ticker )
            return ""

    def getKursAktuellInEuro( self, ticker: str ) -> (float, str):
        """
        Ermittelt den letzten Kurs des Wertpapiers.
        Transformiert ihn in EUR, wenn er nicht in EUR geliefert wird.
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

    def _convertSeries( self, series:Series, currency:str ):
        """
        Übersetzt alle Werte in series.values in Euro und schreibt sie in eine Liste.
        Macht daraus und aus series.index eine neue Series und gibt diese zurück.
        Das muss sein, damit die Beschriftung der y-Achse im Graphen stimmt.
        :param series:
        :param currency: Währung wie in FastInfo eingetragen. (GBp also noch nicht in GBP umgewandelt.)
        :return:
        """
        #values = series.values
        datetimes = series.index.to_numpy()
        values = series.to_numpy()
        vlist = list()
        for dt, value in zip( datetimes, values ):
            if not math.isnan( value ):
                day = str( dt.date() )
                val = self.convert( day, currency, "EUR", value )
                print( day, "USD: ", value, "  EUR: ", val )
            else:
                val = 0
            vlist.append( val )

        index = series.index
        serNew = Series(vlist, index)
        return serNew

    def _provideOrders( self, poslist:List[XDepotPosition], tickHists:DataFrame ):
        """
        Versorgt die Spalten PurchasesEUR und SalesEUR mit den Kaufs- und Verkaufswerten.
        """
        tickerlist = [pos.ticker for pos in poslist]
        # Für jeden Ticker...
        # ...das DepotPosition-Objekt ermitteln
        # ...in die Spalten SalesEUR und PurchasesEUR die im Zeitraum (5 J.) getätigten (Ver-)Käufe eintragen
        for ticker in tickerlist:
            deppos = next( pos for pos in poslist if pos.ticker == ticker )
            assert deppos

            deltas: List[XDelta] = self._provideOrderData( deppos )  # deltas enthält ALLE Käufe und Verkäufe
            # Nur Deltas berücksichtigen, die in <period> liegen
            min_date = str( tickHists.index[0] )[:10]  # max today - 5 years
            for delta in deltas:
                if delta.delta_datum >= min_date:  # es könnte sein, dass der (Ver-)Kauf mehr als 5 Jahre her ist, dann
                                                    # ist das Datum nicht in tickHists.index vorhanden
                    dt = datetime.datetime( int(delta.delta_datum[:4]),
                                            int(delta.delta_datum[5:7]), int(delta.delta_datum[8:]), 0, 0, 0)
                    if delta.verkauft_stck == 0:
                        # ein Kauf
                        tickHists.at[dt, (ticker, "PurchasesEUR")] = delta.preis_stck
                    else:
                        # Verkauf
                        tickHists.at[dt, (ticker, "SalesEUR")] = delta.preis_stck
            deppos.history = tickHists[ticker]
            deppos.allDeltas = deltas

    def _provideOrderData( self, deppos: XDepotPosition ) -> List[XDelta]:
        """
        Holt zur übergebenen Depotposition die delta-Daten aus der DB und trägt sie in <deppos> ein.
        Die Verkäufe werden zwar selektiert, sind also in der Rückgabeliste enthalten, aber für keinerlei
        Berechnungen berücksichtigt.
        Versorgt werden folgende deppos-Felder:
            .stueck, .erster_kauf, .letzter_kauf, .einstandswert_restbestand, .maxKaufpreis, .minKaufpreis,
            .preisprostck
        :param deppos: die Depotposition, die mit den Delta-Zahlen ergänzt wird
        :return: Liste aller Käufe und Verkäufe, die sich auf deppos.wkn beziehen.
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
                restbestand_stck = delta.delta_stck - delta.verkauft_stck
                einstandswert_restbestand = restbestand_stck * delta.preis_stck
                deppos.stueck += ( delta.delta_stck - delta.verkauft_stck )
                ## 5.3.25 deppos.einstandswert_restbestand += ( delta.delta_stck * delta.preis_stck )
                einstandswert_restbestand_falsch = delta.delta_stck * delta.preis_stck
                deppos.einstandswert_restbestand += einstandswert_restbestand
                deppos.maxKaufpreis = delta.preis_stck if delta.preis_stck > deppos.maxKaufpreis else deppos.maxKaufpreis
                deppos.minKaufpreis = delta.preis_stck \
                    if delta.preis_stck < deppos.minKaufpreis or deppos.minKaufpreis == 0 \
                    else deppos.minKaufpreis
            else:
                # Verkauf
                # 5.3.25 deppos.einstandswert_restbestand += ( delta.delta_stck * delta.preis_stck ) # delta_stck < 0, deshalb "+"
                pass # 5.3.25
        if deppos.stueck > 0: # es gibt noch einen Depot-Bestand
            deppos.preisprostueck = round( deppos.einstandswert_restbestand / deppos.stueck, 2 )
            deppos.einstandswert_restbestand = int( round( deppos.einstandswert_restbestand, 2 ) )

        return deltalist

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
        deltas:List[XDelta] = self.getAllOrdersList()
        tm = SumTableModel( deltas, 0, ("order_summe",) )
        tm.setKeyHeaderMappings2(
            ( "id", "delta_datum", "name", "wkn", "isin", "ticker", "depot_id", "delta_stck", "preis_stck", "order_summe"),
            ( "Id", "Datum", "Name", "WKN", "ISIN", "Ticker", "Depot", "Stück", "Preis/Stck", "Ordersumme" ) )
        return tm

    def getAllOrdersList( self ) -> List[XDelta]:
        return self._db.getAllDeltas()

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
        nach einem Anteilsverkauf muss zur späteren Berechnung der Abgeltungssteuer die Anzahl der verkauften Stücke
        auf die vorherigen Käufe verteilt werden.
        Beispiel:
        Verkauft wurden 100 Stück.
        Es gibt 2 Käufe, der ältere mit 80 Stück, der jüngere mit 40 Stück.
        Gem FIFO-Prinzip müssen nun im älteren Kauf 80 verkaufte Stück eingetragen werden und im neueren Kauf
        20 Stück.
        Nach diesen Datenbank-Updates müssen in der Schnittstelle <deppos> die Felder stueck und einstandswert_restbestand
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

    def computeAbgeltungssteuer( self, wkn:str, kurs:float, stck:int ) -> int:
        """
        Berechnet die Abgeltungssteuer, die bei einem Verkauf von <stck> Papieren <wkn> bei aktuellem Kurs <kurs>
        fällig würden
        :param wkn:
        :param kurs:
        :param stck:
        :return: die fällige Abgeltungssteuer
        """
        deltas: List[XDelta] = self._db.getKaeufe( wkn )  # sortiert nach Kaufdatum aufsteigend, also ältester Kauf oben
        rest = stck
        steuer = 0 # fällige Abgeltungssteuer
        for delta in deltas:
            vfgbar = delta.delta_stck - delta.verkauft_stck # so viele Stücke sind von dieser Order noch verfügbar
            if rest >= vfgbar:  # alle verfügbaren Stücke des Kaufes <delta> werden für den gewünschten Verkauf benötigt
                vk = vfgbar
                rest -= vk
            else:
                vk = rest
            if vk > 0:
                kaufpreis = vk * delta.preis_stck # das war der damalige Order-Preis
                vk_preis = vk * kurs  # das wäre der aktuelle Verkaufspreis
                delta = vk_preis - kaufpreis # Gewinn bzw. Verlust dieser Order bei jetzigem Verkauf; negativ bei Verlust
                steuer += (delta * 0.25) # 25% Abgeltungssteuer auf das Delta
        return int( round(steuer, 2) )

    def getPaidDividendsTableModel( self, period:Period ) -> SumTableModel:
        """
        Diese Methode wird *nicht* aus einem separaten Thread aufgerufen.
        Sie ermittelt die WKN-/Tickerlist, alle Orders und mittels TickerHistories alle Dividenden und
        baut daraus ein SumTableModel und liefert es zurück.
        :param period: Gibt die Periode an, für die die Dividendenzahlungen ermittelt werden sollen
        :return:
        """

        def createXDividendAndAddToList( pay_day, div_pro_stck, div ):
            #print( pay_day, div_pro_stck, div )
            xdiv = XDividend()
            xdiv.wkn = wkn
            xdiv.name = name
            xdiv.ticker = ticker
            xdiv.pay_day = pay_day
            xdiv.div_pro_stck = div_pro_stck
            xdiv.div_summe = div
            xdiv_list.append( xdiv )

        xdiv_list:List[XDividend] = list()

        tickHistsPart: DataFrame = self._getTickHistsPart( period, Interval.oneDay )
        divColumns: DataFrame = tickHistsPart.xs( 'DividendsEUR', level='Price', axis=1, drop_level=False )
        allOrders: List[XDelta] = self.getAllOrdersList()
        wkn_list = InvestMonitorLogic.getWknList(sortByWkn=True)
        for wkn in wkn_list:
            wkn_orders = [order for order in allOrders if order.wkn == wkn ]
            if len( wkn_orders ) > 0:
                name = wkn_orders[0].name # brauchen wir in createXDividendAndAddToList() (Pfui Deifi)
                ticker = InvestMonitorLogic.getTicker( wkn )
                divs:Series = divColumns[(ticker, "DividendsEUR")]
                self._getPaidDividends( divs, wkn_orders, callback=createXDividendAndAddToList )

        tm = SumTableModel( xdiv_list, None, ("div_summe",) )
        tm.setKeyHeaderMappings2( ( "name", "wkn", "ticker", "pay_day", "div_pro_stck", "div_summe" ),
                                  ( "Name", "WKN", "Ticker", "Zahltag", "Dividende\nje Stck", "Dividende" ) )
        return tm

    def getSumDividendsCurrentYear( self, allOrders: List[XDelta] ) -> int:
        """
        Liefert die Summe aller Dividendenzahlungen für die im Monitor vertretenen Fonds für das laufende Jahr.
        "Im Monitor vertreten" heißt: depotposition.flag_displ == 1.
        Annahme: alle Bestände lassen sich über Einträge in der Tabelle delta errechnen - auch die Anfangsbestände.
        Hier dürfen keine DB-Zugriffe gemacht werden, weil diese Methode auch aus einem separaten Thread aufgerufen wird.
        ###:param wkn_ticker_list: Liste aller WKN/Ticker, für die die Div.zahlungen ermittelt werden sollen.
        :param allOrders: Alle Orders aus Tabelle <delta>
        :return: die Dividendensumme
        """

        def getOrders( wkn_: str ) -> List[XDelta]:
            orderlist = [order for order in allOrders if order.wkn == wkn_]
            return orderlist

        sum_dividends = 0
        # Den Teil aus self.allHistories holen, der das laufende Jahr umfasst.
        # Dann aus diesem Teil die Spalten DividendsEUR extrahieren:
        tickHistsPart: DataFrame = self._getTickHistsPart( Period.currentYear, Interval.oneDay )
        divColumns: DataFrame = tickHistsPart.xs( 'DividendsEUR', level='Price', axis=1, drop_level=False )

        for mux in divColumns.columns: # mux: ('GLDV.L', "DividendsEUR')
            # für jeden Ticker ist ein Delta vorhanden!
            divCol: Series = divColumns[mux]
            wkn = InvestMonitorLogic.getWkn( mux[0] )  # ticker
            orders = getOrders( wkn )
            sum_dividends += self._getPaidDividends( divCol, orders )

        return sum_dividends


##################################################################################
##################################################################################
def testProvideFastInfoInSeparateThread():
    logic = InvestMonitorLogic()
    depposList:List[XDepotPosition] = logic.getDepotPositions( period=Period.oneYear, interval=Interval.oneWeek )
    print( depposList )

def testGetPaidDividendsTableModel():
    l = InvestMonitorLogic()
    period = Period.currentYear
    sum = l.getPaidDividendsTableModel( period=period )
    print( sum )

def testGetSumDividendsCurrentYear():
    l = InvestMonitorLogic()
    summe = l.getSumDividendsCurrentYear()
    print( summe )

def testComputeAbgeltungssteuer():
    logic = InvestMonitorLogic()
    steuer = logic.computeAbgeltungssteuer( "ABCDEF", 31.00, 12 )
    print( "Steuer: ", steuer )

def test():
    logic = InvestMonitorLogic()
    logic.getDepotPositions( period=Period.oneYear, interval=Interval.oneWeek )
    ##logic.provideTickerHistories( list(), period=Period.oneYear, interval=Interval.oneWeek )
    #lastPrice = logic.getKursAktuellInEuro( "PRIJ.L" )
    #poslist = logic.getDepotPositions()
    #print( poslist )

    # logic.saveMyHistories()

    # poslist = logic.getDepotPositions( period=Period.oneYear, interval=Interval.oneWeek )
    # print( poslist )

    # df = logic.loadMyHistories()
    # close:DataFrame = df["Close"]
    # cols:Index = close.columns # <-- ticker-collection
    # print( cols[0] ) # <-- ticker
    # eusri:DataFrame = close["EUSRI.PA"]
    # print( eusri )

    #series = logic.getSeriesHistoryByPeriod( "WTEM.DE", SeriesName.Close, Period.fiveDays, Interval.oneDay )
    #print( series )

def testDataFrameScheiss():
    import numpy as np
    import pandas as pd
    df = pd.DataFrame(np.random.random((4,4)))
    df.columns = pd.MultiIndex.from_product([[1,2],['A','B']])
    print( df )
    xxx = df.iloc[:, df.columns.get_level_values(1) == 'A']
    print( xxx )
    xxxser = xxx.iloc[2]
    yyy = df.iloc[:, df.columns.get_level_values(0) == 1]
    print( yyy )

def testDataFrameToSimpleDataTable() -> List[SimpleDataTable]:
    def convertToEuro( values:List ) -> List:
        eurovalues = [round(val*0.9, 5) for val in values] # hier die richtige Umwandlung
        return eurovalues

    tickers = ["GLDV.L", "LQDE.L"]
    df = pandas.read_pickle( "tickerhistories.txt" )

    tables:List[SimpleDataTable] = list()
    dfClose = df["Close"] # enthält die Close-Spalten (und nur die) aller Ticker sowie eine Index-Spalte
    dfDividends = df["Dividends"] # enthält die Dividends-Spalten (und nur die) aller Ticker

    for ticker in tickers:  ## in range( len( tickers ) ):
        colClose = dfClose[ticker] # wieder ein DataFrame, mit DateTimeIndex und der Close-Spalte von Ticker LQDE.L
        dates = [ts.date() for ts in colClose.index]
        closeValues = colClose.tolist()
        colDivs = dfDividends[ticker]
        dividends = colDivs.tolist()
        closeValuesEUR:List = convertToEuro( closeValues )
        dividendsEUR = convertToEuro( dividends )
        tbl = SimpleDataTable( tableName=ticker, columns=[dates, closeValues, closeValuesEUR, dividends, dividendsEUR],
                               headers=["Datum", "Close", "Close_EUR", "Dividends", "Dividends_EUR"] )
        tbl.print()
        tables.append( tbl )
    return tables


def testExchangeRates():
    logic = InvestMonitorLogic()
    #########logic.initExchangeRatesDatabase( "2020-11-15", 40 )
    val = logic.convert( "2025-10-22", "CHF", "EUR", 100.00 )
    print( val )

def testSort():
    l = [('LQDE.L', 'B11950'), ('GLDV.L', 'A1T8GD')]
    l.sort( key=lambda x: x[1] )
    print( l )

def testNeu():
    logic = InvestMonitorLogic()
    poslist = logic.getDepotPositions(Period.oneYear, Interval.oneWeek)
    print(poslist)

if __name__ == "__main__":
    testNeu()
    #testSort()
    #testDataFrameToSimpleDataTable()
    #test()
    #testGetPaidDividendsTableModel()
    #testExchangeRates()
