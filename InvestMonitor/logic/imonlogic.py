import datetime
import glob
import math
import os
from math import isnan
from operator import attrgetter
from typing import List, Dict, Tuple

import pandas
from pandas import DataFrame, Timestamp, DatetimeIndex
from yfinance.scrapers.quote import FastInfo

import datehelper
from base.basetablemodel import SumTableModel
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import TickerHistory
from imon.enums import Period, Interval
from interface.interfaces import XDepotPosition, XDelta, XDateValueItem, XDetail, XDividend
from logic.exchangerates import ExchangeRates


class ImonLogic:
    tradingDaysASC:pandas.DatetimeIndex = None
    tradingDaysIsoASC:List[str] = None
    all_deppos:List[XDepotPosition] = None
    all_orders:List[XDelta] = None
    all_sales:List[XDelta] = None
    all_purchases:List[XDelta] = None
    ticker_wkn_curr_list = None

    def __init__( self ):
        self._db = InvestMonitorData()
        self._exchangeRates = ExchangeRates( self._db )
        self._tickerHist = TickerHistory()  # Wrapper um die yfinance-Schnittstelle

    def _ensureDataLoaded(self):
        if not ImonLogic.all_deppos:
            ImonLogic.all_deppos = self._db.getDepotPositions()
            ImonLogic.ticker_wkn_curr_list = [(pos.ticker, pos.wkn, pos.waehrung) for pos  in ImonLogic.all_deppos]
            tickerlist = [item[0] for item in ImonLogic.ticker_wkn_curr_list]
            ImonLogic.all_orders = self._db.getAllDeltas(sort_order="asc") # Alle deltas delta_datum ASC !!WICHTIG!!
            # Die aufsteigende Sortierung ist wichtig, weil die Werte der Käufe sonst nicht mit der
            # Reihenfolge von tradingDays übereinstimmen.
            ImonLogic.all_sales = [order for order in ImonLogic.all_orders if order.delta_stck < 0]
            ImonLogic.all_purchases = [order for order in ImonLogic.all_orders if order.delta_stck > 0]
            alltickershistories = self._getHistoriesFromAPI(tickerlist)
            ImonLogic.tradingDaysASC = alltickershistories.index
            ImonLogic.tradingDaysIsoASC = [str(dtix)[:10] for dtix in ImonLogic.tradingDaysASC]
            self._provideDepposListWithPeriodIndependentData( alltickershistories )

    @staticmethod
    def _getLastTradingDayIso() -> str:
        """
        Liefert den letzten TradingDay aus der Liste ImonLogic.tradingDaysIsoAsc
        """
        return ImonLogic.tradingDaysIsoASC[-1]

    def getKaeufe(self, wkn:str) -> List[XDelta]:
        self._ensureDataLoaded()
        return [kauf for kauf in ImonLogic.all_purchases if kauf.wkn == wkn]

    def getOrders( self, wkn:str ) -> List[XDelta]:
        self._ensureDataLoaded()
        return [order for order in ImonLogic.all_orders if order.wkn == wkn]

    def getOrdersTableModel( self, wkn:str ) -> SumTableModel:
        deltalist = self._db.getDeltas( wkn )
        tm = SumTableModel( deltalist, 0, ("delta_stck", "order_summe") )
        tm.setKeyHeaderMappings2( ("delta_datum", "delta_stck", "preis_stck", "order_summe",
                                   "verkauft_stck", "verkaufskosten", "bemerkung"),
                                  ("Datum",  "Stück", "Stück-\npreis (€)", "Order-\nsumme (€)",
                                   "Stück vk.", "Verk.kosten", "Bemerkung") )
        return tm

    def getAllOrdersTableModel( self ) -> SumTableModel:
        orders = self.getAllOrders()
        tm = SumTableModel(orders, 0, colsToSum=("order_summe",))
        tm.setKeyHeaderMappings2(
            ( "id", "delta_datum", "name", "wkn", "isin", "ticker", "depot_id", "delta_stck", "preis_stck", "order_summe"),
            ( "Id", "Datum", "Name", "WKN", "ISIN", "Ticker", "Depot", "Stück", "Preis/Stck", "Ordersumme" ) )
        return tm

    def getAllOrders(self, sort_order="asc") -> List[XDelta]:
        self._ensureDataLoaded()
        if sort_order == "asc":
            return ImonLogic.all_orders
        else:
            orders = sorted(ImonLogic.all_orders, key=lambda order: order.delta_datum)
            return orders

    def _getHistoriesFromAPI( self, tickers: list ) -> DataFrame:
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

        try:
            if dev_path.lower() in __file__.lower():  # wir sind in der Entwicklungsumgebung
                today = datehelper.getTodayAsIsoString()
                file_path = dev_path + "tickerhistories_" + today + ".txt"
                if not os.path.exists( file_path ):
                    deleteOlderTickerHistories()
                    tickHists: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickers, Period.fiveYears,
                                                                                        Interval.oneDay )
                    tickHists.to_pickle( file_path )
                else:
                    tickHists: DataFrame = pandas.read_pickle( file_path )
            else:
                tickHists: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickers, Period.fiveYears,
                                                                                    Interval.oneDay )
            # Spalten rauswerfen, die wir nicht brauchen (wir brauchen nur Close und Dividends):
            tickHists.drop( ["Capital Gains", "High", "Low", "Open", "Stock Splits", "Volume"],
                            axis=1, inplace=True )
            # Index umdrehen, damit der Ticker führend wird:
            if len(tickers) > 1:
                tickHists.columns = tickHists.columns.swaplevel( 0, 1 )
                tickHists.sort_index( axis=1, level=0, inplace=True )
        except Exception as ex:
            raise ex

        return tickHists

    def getKursAktuellInEuro( self, ticker: str ) -> (float, str):
        """
        Ermittelt aus der TickerHistory.FastInfo den letzten Kurs des Wertpapiers in Euro.
        Transformiert ihn in EUR, wenn er nicht in EUR geliefert wird.
        :param ticker:
        :param currency:
        :return: den letzten Kurs in Euro, gerundet auf 3 Stellen hinter dem Komma
                 UND die ursprüngliche Währung (EUR oder Fremdwährung, die konvertiert wurde)
        """
        fastInfo = self._tickerHist.getFastInfo( ticker )
        if fastInfo:
            last_price = fastInfo.last_price
            currency = fastInfo.currency
            if currency != "EUR":
                try:
                    today = datehelper.getTodayAsIsoString()
                    if currency == "GBp":
                        last_price = last_price/100
                        currency = "GBP"
                    last_price = self._exchangeRates.convert(currency, "EUR", today, last_price)
                except ValueError:
                    # Wochenende, letzten TradingDay holen und nochmal versuchen
                    lastTradingDay = ImonLogic._getLastTradingDayIso()
                    last_price = self._exchangeRates.convert(currency, "EUR", lastTradingDay, last_price)
            return round( last_price, 3 ), currency
        else:
            print( "Ticker '%s':\nNo FastInfo available" % ticker )
            return 0, ""

    def _provideDepposListWithPeriodIndependentData( self, alltickershistories:DataFrame ):
        """
        Versorgen derjenigen Felder einer jeden Depotposition, die **unabhängig von der gewählten period** sind.
        """
        class XOrderData:
            def __init__( self ):
                self.stueck = 0
                self.einstandswert_restbestand = 0
                self.maxKaufpreis = 0
                self.minKaufpreis = 0
                self.erster_kauf = ""
                self.letzter_kauf = ""
                self.preisprostueck = 0
        ########  start subfunctions  #############
        def getOrderData( wkn:str ) -> XOrderData:
            """
            Trägt Kaufdaten in <deppos> ein.
            Versorgt werden folgende deppos-Felder:
                .stueck, .erster_kauf, .letzter_kauf, .einstandswert_restbestand, .maxKaufpreis, .minKaufpreis,
                .preisprostck
            :param wkn:
            :return gefülltes Schnittstellenobjekt XOrderData
            """
            orderData = XOrderData()
            kaeufelist: List[XDelta] = self.getKaeufe(wkn)  # sortiert nach delta_datum aufsteigend
            if len(kaeufelist) > 0:
                orderData.erster_kauf = kaeufelist[0].delta_datum
                orderData.letzter_kauf = kaeufelist[-1].delta_datum

            for kauf_ in kaeufelist:
                restbestand_stck = kauf_.delta_stck - kauf_.verkauft_stck
                einstandswert_restbestand = restbestand_stck * kauf_.preis_stck
                orderData.einstandswert_restbestand += einstandswert_restbestand
                orderData.stueck += (kauf_.delta_stck - kauf_.verkauft_stck)
                if kauf_.preis_stck > orderData.maxKaufpreis:
                    orderData.maxKaufpreis = kauf_.preis_stck
                if kauf_.preis_stck < orderData.minKaufpreis or orderData.minKaufpreis == 0:
                    orderData.minKaufpreis = kauf_.preis_stck

            if orderData.stueck > 0:  # es gibt noch einen Depot-Bestand
                orderData.preisprostueck = round( orderData.einstandswert_restbestand / orderData.stueck, 2 )
                orderData.einstandswert_restbestand = int( round( orderData.einstandswert_restbestand, 2 ) )

            return orderData

        def convertGBpToGBP(pence_values:list) -> list:
            pound_values = [val/100 for val in pence_values]
            return pound_values

        def provideCloseEURandDividendsEUR( deppos_ ):
            if deppos_.waehrung == "EUR":
                deppos_.closePricesEUR = deppos_.closePrices
                deppos_.dividendsEUR = deppos_.dividends
            else:
                conv = self._exchangeRates.convert
                deppos_.closePricesEUR = [conv( deppos_.waehrung, "EUR", day, value ) for day, value
                                          in zip( ImonLogic.tradingDaysIsoASC, deppos_.closePrices )]
                deppos_.dividendsEUR = [conv( deppos_.waehrung, "EUR", day, value ) for day, value
                                        in zip( ImonLogic.tradingDaysIsoASC, deppos_.dividends )]

        ########### end of subfunctions ##################

        for deppos in ImonLogic.all_deppos:
            try:
                deppos.closePrices = alltickershistories[(deppos.ticker, "Close")].tolist() # alle Daten 5 Jahre, täglich
                deppos.dividends = alltickershistories[(deppos.ticker, "Dividends")].tolist()
            except:
                # es ist nur 1 Ticker in alltickershistories, dann sind die Spalten nicht multiindexed
                deppos.closePrices = alltickershistories["Close"].tolist()  # alle Daten 5 Jahre, täglich
                deppos.dividends = alltickershistories["Dividends"].tolist()
            # Sonderbehandlung britische pence:
            if deppos.waehrung == "GBp":
                deppos.closePrices = convertGBpToGBP( deppos.closePrices )
                deppos.dividends = convertGBpToGBP(deppos.dividends)
                deppos.waehrung = "GBP"
            # die Felder .closePricesEUR und .dividendsEUR versorgen:
            provideCloseEURandDividendsEUR( deppos )
            deppos.kurs_aktuell, curr = self.getKursAktuellInEuro(deppos.ticker)
            if curr != deppos.waehrung:
                raise ValueError("ImonLogic._provideDepposListWith...:\nFür Ticker '%s' stimmt Währungsinfo aus "
                                 "FastInfo ('%s') und deppos.waehrung ('%s') nicht überein. "
                                 % (deppos.ticker, curr, deppos.waehrung))
            # Versorgung Feld delta_kurs_percent
            ImonLogic._provideDeltaKursPercent( deppos )
            #deppos.kaeufe = list([0] * len(ImonLogic.tradingDaysIsoASC)) # leere Liste anlegen, in der Länge von tradingDays


            orderData_:XOrderData = getOrderData(deppos.wkn)
            deppos.einstandswert_restbestand = orderData_.einstandswert_restbestand
            deppos.stueck = orderData_.stueck
            deppos.minKaufpreis = orderData_.minKaufpreis
            deppos.maxKaufpreis = orderData_.maxKaufpreis
            deppos.erster_kauf = orderData_.erster_kauf
            deppos.letzter_kauf = orderData_.letzter_kauf
            deppos.preisprostueck = orderData_.preisprostueck
            deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
            # print(deppos.ticker, ": stueck= ", deppos.stueck, " kurs_aktuell = ", deppos.kurs_aktuell,
            #       " gesamtwert_aktuell = ", deppos.gesamtwert_aktuell)
            if deppos.einstandswert_restbestand > 0:
                deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.einstandswert_restbestand - 1) * 100, 2 )

    def provideTickerHistories( self, depposList:List[XDepotPosition], period: Period, interval: Interval ):
        """
        Versorgt die Depotpositionen mit den Daten, die für die gewünschte period relevant sind.
        Diese ändern sich bei jeder Änderung von period.
        Wird aufgerufen von MainController.onPeriodIntervalChanged(). Das Signal period_interval_changed wird nur
        vom MainWindow aufgerufen, nicht von den einzelnen InfoPanels.
        """
        self._provideDepposListWithPeriodDependingData( depposList, period, interval )

    @staticmethod
    def _getStartIdx( period:Period, tradingDays:List[str] ) -> int:
        # Ermittelt den Index der Liste tradingDays, ab dem - gem. der gewünschten period - die Tage
        # dieser Liste zu berücksichtigen sind.
        from_datetime, curr_datetime = ImonLogic._getStartAndCurrentDatetime( period )
        from_day = str( from_datetime )[:10]
        for idx, day in enumerate( tradingDays ):
            if day >= from_day:
                return idx
        raise ValueError( "ImonLogic._getStartIdx():\nStart-Tag '%s' größer als "
                          "größter Tag in tradingDays: '%s'" % (from_day, tradingDays[-1]) )

    def _provideDepposListWithPeriodDependingData( self, depposList:List[XDepotPosition], period:Period, interval:Interval ):
        """
        versorgt diejeinigen Felder aller Depot-Positionen, die period-spezifisch sind
        """
        def getAllFridays(start:datetime.datetime, end:datetime.datetime) -> pandas.DatetimeIndex:
            return pandas.date_range( start=start, end=end, freq='W-FRI' ) #.strftime( '%Y-%m-%d' ).tolist()

        def getAllMonthEnds(start:datetime.datetime, end:datetime.datetime) -> pandas.DatetimeIndex:
            return pandas.date_range( start=start, end=end, freq='ME' )

        def createTradingDaysIndex() -> DatetimeIndex:
            tradingDaysPeriod: List[Timestamp] = list()  # (Rückgabe-)Liste, aus der später der DatetimeIndex
            # deppos.tradingDaysPeriod gemacht wird
            # ALLE trading days in der gewünschten Periode:
            daysInPeriod = ImonLogic.tradingDaysASC[startIdxPeriod:]
            lastdayInPeriod: Timestamp = daysInPeriod[-1]  # max. gestern, nie heute
            if interval == Interval.oneWeek:
                specialDaysInPeriod: DatetimeIndex = getAllFridays( daysInPeriod[0], lastdayInPeriod )  # ALLE Freitage in period
            elif interval == Interval.oneMonth:
                specialDaysInPeriod:DatetimeIndex = getAllMonthEnds(daysInPeriod[0], lastdayInPeriod)
            elif interval == Interval.oneDay:
                specialDaysInPeriod = daysInPeriod
            else:
                raise ValueError("ImonLogic.createTradingDaysIndex(): unknown Interval '%s'" %interval.value)

            ix = startIdxPeriod
            len_ = len( ImonLogic.tradingDaysASC )
            for specialDay in specialDaysInPeriod:
                for i in range( ix, len_ ):
                    tradeday: Timestamp = ImonLogic.tradingDaysASC[i]
                    if tradeday == specialDay:  # friday war ein trading day...
                        # ...also in die Rückgabe-Liste aufnehmen
                        tradingDaysPeriod.append( specialDay )
                        break
                    elif tradeday > specialDay:
                        # dieser friday war KEIN trading day, also nehmen wir den letzten Handelstag davor
                        i = i - 1
                        tradeday = ImonLogic.tradingDaysASC[i]
                        tradingDaysPeriod.append( tradeday )
                        break
                    ix = i + 1

            if lastdayInPeriod > specialDaysInPeriod[-1]:
                # der letzte Handelstag war kein Freitag, trotzdem wollen wir ihn in der Liste haben.
                # der letzte Tag der Periode ist immer der letzte Tag von tradingDaysASC
                tradingDaysPeriod.append( lastdayInPeriod )

            return DatetimeIndex(tradingDaysPeriod)

        #################   end of subfunctions  ######################

        startIdxPeriod = -1
        dtix:DatetimeIndex = None

        for deppos in depposList:
            if deppos.period == period and deppos.interval == interval:
                continue

            # Versorgung der Felder .startIdxPeriod, .period, .interval, .startIdxPeriod
            if startIdxPeriod == -1:
                startIdxPeriod = ImonLogic._getStartIdx(period, ImonLogic.tradingDaysIsoASC)
                dtix = createTradingDaysIndex()

            deppos.tradingDaysPeriod = dtix
            deppos.period = period
            deppos.interval = interval
            deppos.startIdxPeriod = startIdxPeriod # brauchen wir das überhaupt nach u.a. Änderung?

            self._provideDepposWithPeriodDependingData(deppos)

    def _provideDepposWithPeriodDependingData(self, deppos:XDepotPosition):
        """
        versorgt die übergebene Depot-Position mit den period-spezifischen Informationen
        Von _provideDepposListWithPeriodDependingData() sind bereits versorgt:
            deppos.tradingDaysPeriod
            deppos.period
            deppos.interval
            deppos.startIdxPeriod
        """
        def getDeltasKauf( wkn: str, startdatumIso:str ) -> List[Tuple]:
            """
            :return: Liefert zum Wertpapier <wkn> eine Liste von Käufen, die *am oder nach* startdatumIso
             stattgefunden haben, repräsentiert durch einen Teil der Kaufdaten in Form eines Tuples je Kauf.
             Die Rückgabeliste hat den Aufbau [(delta_datum:str, preis_stck:float), ...]
            """
            # wichtig: all_purchases muss aufsteigend sortiert sein
            # kaeufe_ = [(order.delta_datum, order.preis_stck) for order in ImonLogic.all_purchases if order.wkn == wkn]
            kaufDatumUndPreisList = list()
            for delta in ImonLogic.all_purchases:
                if delta.wkn == wkn and delta.delta_datum >= startdatumIso:
                    isodate = delta.delta_datum
                    dt = datetime.datetime( int( isodate[:4] ), int( isodate[5:7] ), int( isodate[-2:] ) )
                    kaufDatumUndPreisList.append( (dt, delta.preis_stck) )
            return kaufDatumUndPreisList  # [(datetime, preis), ...]

        def getDeltasVerkauf( wkn: str, startdatumIso:str ) -> list:
            """
            :return: Liefert zum Wertpapier <wkn> eine Liste von Verkäufen, repräsentiert durch einen Teil
             der Verkaufsdaten in Form eines Tuples je Verkauf.
             Die Liste enthält die Verkäufe dieses Wertpapiers, die *am oder nach* startdatumIso stattgefunden haben,
             ist also period-dependent.
             Die Rückgabeliste hat den Aufbau [(delta_datum:str, preis_stck:float), ...]
            """
            # wichtig: all_sales muss aufsteigend sortiert sein
            # verkaeufe_ = [(order.delta_datum, order.preis_stck) for order in ImonLogic.all_sales if order.wkn == wkn]
            verkaufsDatumUndPreisList = list()
            for delta in ImonLogic.all_sales:
                if delta.wkn == wkn and delta.delta_datum >= startdatumIso:
                    isodate = delta.delta_datum
                    dt = datetime.datetime( int( isodate[:4] ), int( isodate[5:7] ), int( isodate[-2:] ) )
                    verkaufsDatumUndPreisList.append( (dt, delta.preis_stck) )
            return verkaufsDatumUndPreisList  # [(datetime, preis), ...]

        #################  end of subfunctions  ##################

        deppos.closePricesPeriod = list()
        deppos.closePricesEURPeriod = list()
        deppos.dividendsEURPeriod = list()
        len_ = len(ImonLogic.tradingDaysASC)
        ix = deppos.startIdxPeriod
        for day in deppos.tradingDaysPeriod:
            for i in range( ix, len_ ):
                tradeday:Timestamp = ImonLogic.tradingDaysASC[i]
                if tradeday == day: # day war ein trading day...
                    # ...also die Close-Werte ermitteln
                    deppos.closePricesPeriod.append( deppos.closePrices[i] )
                    deppos.closePricesEURPeriod.append( deppos.closePricesEUR[i] )
                    break
                elif tradeday > day:
                    # dieser day war KEIN trading day, also nehmen wir den letzten Handelstag davor
                    i = i-1
                    #tradeday = ImonLogic.tradingDaysASC[i]
                    deppos.closePricesPeriod.append( deppos.closePrices[i] )
                    deppos.closePricesEURPeriod.append( deppos.closePricesEUR[i] )
                    break
                ix = i + 1

        # Versorgung dividend_period: die Summe der Dividenden, die in period je Stück bezahlt wurde:
        startIdxPeriod = deppos.startIdxPeriod
        divs:list = deppos.dividendsEUR[startIdxPeriod:]
        deppos.dividend_period = ImonLogic._getSumDividends(divs)
        if deppos.dividend_period > 0:
            deppos.dividend_yield = self._computeDividendYield( deppos.closePricesEUR[startIdxPeriod],
                                                                deppos.dividend_period )
        # Versorgung dividend_paid_period: die Summe der Dividenden, die für deppos in period bezahlt wurde:
        days = ImonLogic.tradingDaysIsoASC[startIdxPeriod:]
        deppos.dividend_paid_period = self._getPaidDividends(deppos.wkn, days, divs)

        # Die Listen für Käufe und Verkäufe versorgen:
        deppos.kaufKurse = list()
        deppos.kauf_dtix = list()
        startDatum = ImonLogic.tradingDaysIsoASC[startIdxPeriod]
        kaufdatumundpreislist: List[Tuple] = getDeltasKauf( deppos.wkn, startDatum )
        for datumundpreis in kaufdatumundpreislist:  # kauf: (datum:datetime, value:float)
            deppos.kauf_dtix.append(datumundpreis[0])
            deppos.kaufKurse.append( datumundpreis[1] )
        deppos.verkaufKurse = list()
        deppos.verkauf_dtix = list()
        verkaufsdatumundpreislist = getDeltasVerkauf( deppos.wkn, startDatum )
        for datumundpreis in verkaufsdatumundpreislist:
            deppos.verkauf_dtix.append(datumundpreis[0])
            deppos.verkaufKurse.append(datumundpreis[1])

    @staticmethod
    def _computeDividendYield( kurs: float, dividend: float ) -> float:
        if not dividend or math.isnan(dividend) or dividend <= 0: return 0
        divYield = dividend / kurs
        return round( divYield * 100, 3 )

    @staticmethod
    def _provideDeltaKursPercent(deppos:XDepotPosition):
        previous_close = deppos.closePricesEUR[-1]
        if deppos.kurs_aktuell and previous_close and previous_close > 0:
            deltaPrice = deppos.kurs_aktuell - previous_close
            # Verhältnis des akt. Kurses zum Schlusskurs des Vortages:
            deppos.delta_kurs_percent = round( deltaPrice / previous_close * 100, 2 )
        else:
            deppos.delta_kurs_percent = 0

    @staticmethod
    def _getSumDividends( dividends:List[float] ) -> float:
        div: float = sum( [v for v in dividends if not math.isnan( v )] )
        return round( div, 3 )

    def _getPaidDividends(self, wkn:str, days:List[str], dividendsEUR:List[float], callback=None ) -> int:
        """
        Ermittelt die Dividendenzahlungen gemäß Eintragungen in <dividends>.
        Für jede Dividendenzahlung wird nur der zum Zahlungszeitpunkt vorhandene Depotbestand berücksichtigt.
        (Wobei das auch ungenau ist, denn Dividenden werden aufgeteilt zwischen aktuellem und Vor-Besitzer.)
        :param wkn: Wertpapier, dessen Dividenden ermittelt werden sollen
        :param days: Liste der Tage, die betrachtet werden sollen. Div.zahlungen in dieser Liste werden für die
                    Rückgabe berücksichtigt (summiert).
        :param dividendsEUR: Die Dividenden-Liste der Depotposition wkn.
                            Es wird vorausgesetzt, dass sie in Euro übergeben wird.
                BEACHTE: days und dividendsEUR müssen die gleiche Länge haben!
        :param callback: Funktion, die aufgerufen wird für jede Dividendensumme, die durch _computeDividendOnBestand
                        ausgerechnet wurde.
                        Die Callback-Funktion muss 3 Argumente empfangen: den Div.-Zahltag (ISO), die Div. pro Stück
                        und die Gesamt-Dividende, die auf den am Zahltag vorhandenen Bestand ausgezahlt wurde.
        :return Summe der Dividendenzahlungen während des Zeitraums, der durch days vorgegeben wird.
        """
        if len(days) != len(dividendsEUR):
            raise ValueError("ImonLogic._getPaidDividends():\nDie Länge der Argumente days und dividendsEUR "
                             "ist unterschiedlich. WKN: '%s'" %wkn)

        deltas: List[XDelta] = self.getOrders( wkn )
        sum_dividends = 0
        #for idx, value in enumerate( dividendsEUR ):
        for day, value in zip(days, dividendsEUR):
            if isnan(value) or value <= 0:
                continue
            #print( "paid: ", str(pay_ts)[:10], ": ", value )
            # den Depotbestand der Position <deppos> zum Datum <paydate> ermitteln:
            div_pro_stck = float( value )
            div = ImonLogic._computeDividendOnBestand( deltas, div_pro_stck, day )
            if callback:
                callback( day, div_pro_stck, div )
            sum_dividends += div
        return sum_dividends

    @staticmethod
    def _computeDividendOnBestand( deltas: List[XDelta], dividend: float, paydate: str ) -> int:
        """
        Errechnet die Dividende, die auf den am Ausschüttungstag <paydate> vorhandenen Bestand bezahlt wurde.
        :param deltas: Alle Käufe u. Verkäufe eines bestimmten Fonds (oder Aktie)
                       Es wird vorausgesetzt, dass deltas nach <delta_datum> aufsteigend sortiert ist.
        :param dividend: an paydate bezahlte Dividende pro Stück
        :param paydate: Ausschüttungstag (ISO-Format)
        :return:
        """
        if not dividend or math.isnan(dividend) or dividend <= 0:
            return 0
        summe_stck = 0
        for delta in deltas:
            if delta.delta_datum < paydate:
                summe_stck += delta.delta_stck  # gekaufte Stücke werden addiert, verkaufte subtrahiert.
                                                # <delta.verkauft_stck> braucht nicht berücksichtigt werden,
                                                # da sie nur eine Aufteilung der Verkäufe (die hier subtrahiert werden)
                                                # auf die Käufe darstellen (im Sinne verfügbarer Stücke)
            else:
                break
        return int( round( summe_stck * dividend, 2 ) )

    @staticmethod
    def getDividendPaymentsInPeriodSumTableModel( deppos:XDepotPosition ) -> SumTableModel:
        divs = deppos.dividendsEUR[deppos.startIdxPeriod:]
        days = ImonLogic.tradingDaysIsoASC[deppos.startIdxPeriod:]
        dateValueItemList:List[XDateValueItem] = list()
        for idx, val in enumerate(divs):
            if val > 0:
                dateIso = days[idx]
                dateValueItemList.append(XDateValueItem(dateIso, val))
        tm = SumTableModel(dateValueItemList, jahr=0, colsToSum=("value",))
        tm.setKeyHeaderMappings2(("dateIso", "value"), ("Datum", "Dividende"))
        return tm

    def getSumDividendsCurrentYear( self ) -> int:
        """
        Liefert die Summe aller Dividendenzahlungen für die im Monitor vertretenen Fonds für das laufende Jahr.
        "Im Monitor vertreten" heißt: depotposition.flag_displ == 1.
        Annahme: alle Bestände lassen sich über Einträge in der Tabelle delta errechnen - auch die Anfangsbestände.
        Hier dürfen keine DB-Zugriffe gemacht werden, weil diese Methode auch aus einem separaten Thread aufgerufen wird.
        :return: die Dividendensumme
        """
        sum_dividends = 0
        startIdx = -1 # der Start-Index ist für alle Depotpositionen gleich und wird nur einmal ermittelt
        for deppos in ImonLogic.all_deppos:
            if startIdx < 0:
                startIdx = ImonLogic._getStartIdx(Period.currentYear, ImonLogic.tradingDaysIsoASC)
            divs = deppos.dividendsEUR[startIdx:]
            if all(x == 0 for x in divs):
                continue
            sum_dividends += self._getPaidDividends(deppos.wkn, ImonLogic.tradingDaysIsoASC[startIdx:], divs)

        return sum_dividends

    def getPaidDividendsTableModel( self, period:Period ) -> SumTableModel:
        """
        Diese Methode wird *nicht* aus einem separaten Thread aufgerufen.
        Sie ermittelt für alle Depot-Positionen alle Dividenden, die in period geflossen sind,
        baut daraus ein SumTableModel und liefert es zurück.
        :param period: Gibt die Periode an, für die die Dividendenzahlungen ermittelt werden sollen
        :return:
        """
        #todo

        def createXDividendAndAddToList( pay_day, div_pro_stck, div ):
            #print( pay_day, div_pro_stck, div )
            if div > 0:
                xdiv = XDividend()
                xdiv.wkn = deppos.wkn
                xdiv.name = deppos.name
                xdiv.ticker = deppos.ticker
                xdiv.pay_day = pay_day
                xdiv.div_pro_stck = div_pro_stck
                xdiv.div_summe = div
                xdiv_list.append( xdiv )

        xdiv_list:List[XDividend] = list()

        for deppos in ImonLogic.all_deppos:
            self._getPaidDividends( deppos.wkn, ImonLogic.tradingDaysIsoASC[deppos.startIdxPeriod:],
                                    deppos.dividendsEUR[deppos.startIdxPeriod:],
                                    callback=createXDividendAndAddToList )

        tm = SumTableModel( xdiv_list, None, ("div_summe",) )
        tm.setKeyHeaderMappings2( ( "name", "wkn", "ticker", "pay_day", "div_pro_stck", "div_summe" ),
                                  ( "Name", "WKN", "Ticker", "Zahltag", "Dividende\nje Stck", "Dividende" ) )
        return tm
        # return None # test

    @staticmethod
    def _getStartAndCurrentDatetime( period: Period ) -> (datetime.datetime, datetime.datetime):
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
                dd = -20 # trading days
            elif period == Period.threeMonths:
                dd = -60
            elif period == Period.sixMonths:
                dd = -120
            elif period == Period.oneDay:
                dd = -1
            elif period == Period.fiveDays:
                dd = -5
            if dd == 0:
                if period == Period.currentYear:
                    from_datetime = datetime.datetime( year, 1, 1 )
                else:
                    raise ValueError(
                        "ImonLogic._getStartAndCurrentDatetime(): unknown period" + str( period ) )
            else:
                from_datetime = datehelper.addDays( curr_date, dd )
        else:
            from_datetime = datehelper.addYears( curr_date, dy )

        return from_datetime, curr_datetime

    def getDepotPositions( self, period:Period, interval:Interval, TEST=False ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der gewünschten Periode und
        dem gewünschten Zeitintervall
        :return:
        """
        self._ensureDataLoaded()
        # Wertpapierdaten in Positionen eintragen (Kursverlauf, Dividenden etc.)
        self.provideTickerHistories( ImonLogic.all_deppos, period, interval )
        return ImonLogic.all_deppos

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

    def updateKursAndDivYield( self, deppos:XDepotPosition ):
        self._provideFastInfoData( deppos )
        if deppos.kurs_aktuell > 0 and deppos.dividend_period > 0:
            first_kurs_period = deppos.closePricesEURPeriod[0]
            deppos.dividend_yield = self._computeDividendYield( first_kurs_period, deppos.dividend_period )

    def _provideFastInfoData( self, deppos:XDepotPosition ):
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
                    last_price = self._exchangeRates.convert(currency, "EUR", datehelper.getCurrentDateIso(), last_price, 2)
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
        else:
            print( "Ticker '%s':\nNo FastInfo available" % deppos.ticker )
            raise  Exception("ImonLogic._provideFastInfoData(): Kein Zugriff auf FastInfo für Ticker '%s'" %deppos.ticker)

    @staticmethod
    def _getDeltaKursPercent( last_price: float, previous_close: float ) -> float:
        if not previous_close or previous_close == 0:
            return 0
        deltaPrice = last_price - previous_close
        # Verhältnis des akt. Kurses zum Schlusskurs des Vortages:
        delta_kurs_percent = round( deltaPrice / previous_close * 100, 2 )
        return delta_kurs_percent

    def getSimulatedDividendYield( self, deppos:XDepotPosition ) -> float: #, kurs_aktuell: float, dividends: Series ) -> float:
        """
        Berechnet die theoretische Dividendenrendite auf Basis des aktuellen Kurses und der Summe der Dividendenzahlungen
        pro  Stück während der letzten 12 Monate.
        :return: die Rendite in Prozent, gerundet auf 2 Stellen genau
        """
        if deppos.kurs_aktuell == 0:
            raise ValueError("ImonLogic.getSimulatedDividendYield():\nDividende für Ticker '%s' kann nicht ausgerechnet "
                             "werden, da deppos.kurs_aktuell == 0")
        startIdx = self._getStartIdx(Period.oneYear, ImonLogic.tradingDaysIsoASC)
        divs = deppos.dividendsEUR[startIdx:]
        sumDiv = 0
        for div in divs:
            if div > 0: sumDiv += div
        return round(sumDiv / deppos.kurs_aktuell * 100, 2)

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

    @staticmethod
    def getDetails( deppos: XDepotPosition ) -> XDetail:
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

##########################################################################################


###################    T E S T   ##########################################################
def test():
    logic = ImonLogic()
    poslist = logic.getDepotPositions(Period.oneYear, Interval.oneWeek)
    print(poslist)

def testDatetime():
    isodate = "2025-11-02"
    yyyy = isodate[:4]
    mm = isodate[5:7]
    dd = isodate[-2:]
    dt = datetime.datetime(int(yyyy), int(mm), int(dd))
    print( dt )
    dtix:pandas.DatetimeIndex = pandas.DatetimeIndex((dt,))
    for idx, dt_ in enumerate(dtix):
        if dt == dt_:
            print(idx)

def allfridays(year_start, year_end):
    # Aufruf von date_range ohne .strftime bringt einen DatetimeIndex zurück
    return pandas.date_range(start=str(year_start), end=str(year_end+1),
                         freq='W-FRI').strftime('%Y-%m-%d').tolist()

def allfridays2():
    # Aufruf von date_range ohne .strftime bringt einen DatetimeIndex zurück
    allfridays = pandas.date_range(start="2024-11-01", end="2025-11-30",
                         freq='W-FRI').strftime('%Y-%m-%d').tolist()
    allfridays2:pandas.DatetimeIndex = pandas.date_range(start=datetime.datetime(year=2024, month=11, day=1),
                                    end=datetime.datetime(year=2025, month=11, day=30),
                                    freq='W-FRI')
    day = datetime.datetime(year=2025, month=12, day=1)
    lastday = allfridays2[-1]
    if lastday < day:
        allfridays2 = allfridays2.append(pandas.Index((day,)))

    print("")


if __name__ == "__main__":
    #fridays = allfridays2()
    # print(fridays)
    #testDatetime()
    test()