import enum
from datetime import date
from enum import Enum
from typing import List

import yfinance
from pandas import DataFrame, Series
import datehelper

def getOneYearAgo() -> str:
    currentDate: date = datehelper.getCurrentDate()
    oneyearago = datehelper.addYears( currentDate, -1 )
    return datehelper.getIsoStringFromDate( oneyearago )

class SeriesName( Enum ):
    Close = enum.auto()
    Dividends = enum.auto()
    High = enum.auto()
    Low = enum.auto()
    Open = enum.auto()

class Period( Enum ):
    # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    oneDay = "1d"
    fiveDays = "5d"
    oneMonth = "1mo"
    threeMonths = "3mo"
    sixMonths = "6mo"
    oneYear = "1y"
    twoYears = "2y"
    fiveYears = "5y"
    tenYears = "10y"
    max = "max"

class Interval( Enum ):
    # 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
    oneMin = "1m"
    twoMins = "2m"
    fiveMins = "5m"
    fifteenMins = "15m"
    thirtyMins = "30m"
    sixtyMins = "60m"
    ninetyMins = "90m"
    oneHour = "1h"
    oneDay = "1d"
    fiveDays = "5d"
    oneWeek = "1wk"
    oneMonth = "1mo"
    threeMonths = "3mo"

######################################################################
class TickerHistory:
    currentDate = datehelper.getIsoStringFromDate( datehelper.getCurrentDate() )
    oneYearAgo = getOneYearAgo()

    @staticmethod
    def getTickerHistory( ticker: str, period:Period = Period.oneYear, interval:Interval = Interval.oneDay,
                          start: str = oneYearAgo, end: str = currentDate ) -> DataFrame:
        """
        :param ticker: Ticker like "goog", "SEDM.L", ...
        :param period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :param start: Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
        :param end: Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        :return:
        """
        yf_ticker = yfinance.Ticker( ticker )
        df = yf_ticker.history( period.value, interval.value, start, end )
        return df

    @staticmethod
    def getTickerHistories( tickers: List[str], period: Period = Period.oneYear, interval: Interval = Interval.oneDay,
                          start: str = oneYearAgo, end: str = currentDate ) -> DataFrame:
        """
        :param tickers: List of Tickers like "goog", "SEDM.L", ...
        :param period: Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
        :param interval: Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
        :param start: Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
        :param end: Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        :return:
        """
        yf_tickers = yfinance.Tickers( tickers )
        df = yf_tickers.history( period.value, interval.value, start, end )
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