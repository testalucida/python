import enum
from datetime import date
from enum import Enum
from typing import List

import yfinance
from currency_converter import CurrencyConverter
from pandas import DataFrame, Series
from yfinance.scrapers.quote import FastInfo

import datehelper
from imon.enums import Period, Interval, SeriesName


def getOneYearAgo() -> str:
    currentDate: date = datehelper.getCurrentDate()
    oneyearago = datehelper.addYears( currentDate, -1 )
    return datehelper.getIsoStringFromDate( oneyearago )

######################################################################
class TickerHistory:
    currentDate = datehelper.getIsoStringFromDate( datehelper.getCurrentDate() )
    oneYearAgo = getOneYearAgo()
    default_period:Period = Period.oneYear
    default_interval:Interval = Interval.oneWeek
    currConverter = CurrencyConverter()

    @staticmethod
    def getFastInfo( ticker:str ) -> FastInfo:
        yf_ticker = yfinance.Ticker( ticker )
        return yf_ticker.fast_info

    @staticmethod
    def convertToEuro( value, fromCurr="USD" ):
        conv_val = TickerHistory.currConverter.convert( value, fromCurr, "EUR" )
        return conv_val

    # def getFastInfos( self, tickerlist:List[str] ) :
    #     yf_tickers = yfinance.Tickers( tickerlist )
    #     fastInfos = yf_tickers.??

    @staticmethod
    def getTickerHistoryByPeriod( ticker: str,
                                  period:Period = default_period, interval:Interval = default_interval ) -> DataFrame:
        """
        :param ticker: Ticker like "goog", "SEDM.L", ...
        :param period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :return:
        """
        yf_ticker = yfinance.Ticker( ticker )
        df = yf_ticker.history( period.value, interval.value )
        return df

    @staticmethod
    def getTickerHistoryByDates( ticker: str, interval:Interval = default_interval,
                                 start: str = oneYearAgo, end: str = currentDate ) -> DataFrame:
        """
        :param ticker: Ticker like "goog", "SEDM.L", ...
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :param start: Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
        :param end: Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        :return:
        """
        yf_ticker = yfinance.Ticker( ticker )
        df = yf_ticker.history( interval.value, start, end )
        return df

    @staticmethod
    def getTickerHistoriesByPeriod( tickers: List[str],
                                    period: Period = default_period, interval: Interval = default_interval ) -> DataFrame:
        """
        :param tickers: List of Tickers like "goog", "SEDM.L", ...
        :param period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :return:
        """
        yf_tickers = yfinance.Tickers( tickers )
        df = yf_tickers.history( period.value, interval.value )
        return df

    @staticmethod
    def getTickerHistoriesByDates( tickers: List[str], interval: Interval = default_interval,
                                   start: str = oneYearAgo, end: str = currentDate ) -> DataFrame:
        """
        :param tickers: List of Tickers like "goog", "SEDM.L", ...
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :param start: Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
        :param end: Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        :return:
        """
        yf_tickers = yfinance.Tickers( tickers )
        df = yf_tickers.history( interval.value, start, end )
        return df

    @staticmethod
    def getSeries( df:DataFrame, seriesName:SeriesName ) -> Series:
        return df[seriesName.name]


################  TEST TEST TEST   ###########################
def test3():
    tick_hist = TickerHistory()
    df = tick_hist.getTickerHistories( ["GGRG.L", "QDVX.DE"] )
    series = df["Close"]
    series.plot()
    print( "fertig" )

def test2():
    sname = SeriesName.Close
    print( sname.name )

def test():
    tick_hist = TickerHistory()
    df = tick_hist.getTickerHistory( "VJPN.SW" )
    series:Series = df["Close"]
    series.plot()