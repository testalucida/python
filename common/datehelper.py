from datetime import datetime, date
import dateutil.parser
from PySide2.QtCore import QDate
from dateutil.relativedelta import relativedelta
from typing import Tuple, Dict


monthList = ("Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember")

monatsletzter = {
    "Januar": 31,
    "Februar": 28,
    "März": 31,
    "April": 30,
    "Mai": 31,
    "Juni": 30,
    "Juli": 31,
    "August": 31,
    "September": 30,
    "Oktober": 31,
    "November": 30,
    "Dezember": 31
}

def getCurrentYearAndMonth() -> Dict:
    d = { }
    d["month"] = datetime.now().month
    d["year"] = datetime.now().year
    return d

def getMonthIndex( month:str ) -> int:
    """
    returns index of month given as (german) string, e.g.: return 1 if month == "Januar"
    :param month: "Januar", "Februar",... according to monthlist
    :return: index of given month
    """
    for i in range( len( monthList ) ):
        if monthList[i] == month:
            return i+1
    raise Exception( "Wrong month name: '%s'" % (month) )

def getDateParts( datestring:str ) -> Tuple[int, int, int]:
    """
    Returns the given ISO or EUR datestring converted in
    integer parts (y, m, d)
    :param datestring:  yyyy-mm-dd (ISO) or dd.mm.yyyy (EUR)
    :return:
    """
    if isValidIsoDatestring( datestring ):
        y = int( datestring[0:4] )
        m = int( datestring[5:7] )
        d = int( datestring[-2:] )
        return y, m, d
    if isValidEurDatestring( datestring ):
        d = int( datestring[0:2] )
        m = int( datestring[3:5] )
        y = int( datestring[-4:] )
        return y, m, d
    raise Exception( "datehelper.getDateParts(): '%s' is not a valid date string" % (datestring) )

def convertIsoToEur(isostring: str) -> str:
    """
    converts an isodatestring into an eur datestring
    (2019-08-05 into 05.08.2019)
    :param isostring:
    :return: a converted datestring
    """
    if not isostring:
        return ''

    iso = isostring.split('-')
    eur = ''.join((iso[2], '.', iso[1], '.', iso[0]))
    return eur

def isValidEurDatestring(eurstring: str) -> bool:
    try:
        datetime.strptime(eurstring, '%d.%m.%Y')
        return True
    except ValueError as err:
        return False

def isValidIsoDatestring(isostring: str) -> bool:
    try:
        datetime.strptime(isostring, '%Y-%m-%d')
        return True
    except ValueError as err:
        return False

def convertEurToIso(eurstring: str) -> str:
    """
    converts an eurdatestring int an iso datestring
    ('29.08.2019' into '2019-08-29')
    :param eurstring:
    :return: a converted datestring
    """
    if not isValidEurDatestring(eurstring): return ''

    eur = eurstring.split('.')
    iso = ''.join((eur[2], '-', eur[1], '-', eur[0]))
    return iso

def compareEurDates(eurstring1: str, eurstring2: str) -> int:
    """
    compare 2 dates given in eur strings ('mm.dd.yyyy').
    :param eurstring1:
    :param eurstring2:
    :return:    -1 if eurstring1 < eurstring2 (earlier)
                 0 if eurstring1 == eurstring2
                 1 if eurstring1 > eurstring2
    """
    eur1 = eurstring1.split('.')
    eur2 = eurstring2.split('.')
    date1 = datetime(int(eur1[2]), int(eur1[1]), int(eur1[0]))
    date2 = datetime(int(eur2[2]), int(eur2[1]), int(eur2[0]))
    if date1 > date2: return 1
    if date1 == date2: return 0
    return -1

def getDateFromIsoString( isostring:str ) -> date:
    y, m, d = getDateParts( isostring )
    d = date( y, m, d )
    return d

def getQDateFromIsoString( isostr:str ) -> QDate:
    parts = isostr.split( "-" )
    return QDate( int(parts[0]), int(parts[1]), int(parts[2]) )

def getIsoStringFromQDate( date:QDate ) -> str:
    return getIsoStringFromDateParts( date.year(), date.month(), date.day() )

def getIsoStringFromDate( dt:date ) -> str:
    return getIsoStringFromDateParts( dt.year, dt.month, dt.day )

def getIsoStringFromDateParts( yyyy:int, mm:int, dd:int ) -> str:
    return str( yyyy ) + "-%.2d-%.2d" % ( mm, dd )

def isWithin(datestring2check: str, startdatestring: str, enddatestring: str) -> bool:
    """
    checks if datestring2check is part of the given interval.
    datestring2check being equal startdatestring or enddatestring means it is
    part of the interval
    :param datestring2check: date in eur string format
    :param startdatestring: date in eur string format
    :param enddatestring: date in eur string format
    :return:
    """
    if compareEurDates(datestring2check, startdatestring) < 0:

        return False
    if compareEurDates(datestring2check, enddatestring) > 0:
        return False
    return True

def compareToToday(eurstring: str) -> int:
    """
    compares a given date in eur string format with today's date.
    :param eurstring:  the date to check
    :return: -1 if eurstring is in the past, 0 if eurstring == today,
    +1 if eurstring is in the future.
    """
    eurtoday = date.today().strftime('%d.%m.%Y')
    return compareEurDates(eurstring, eurtoday)

def getCurrentYear() -> int:
    return date.today().year

def getLastYears(cnt: int) -> list:
    current = date.today().year
    yearlist = []
    for n in range(cnt):
        yearlist.append(current - n)
    return yearlist

def getTodayAsIsoString() -> str:
    return date.today().isoformat()

def getNumberOfMonths(d1: str, d2: str, year: int) -> int:
    """
    gets the number of months within the period beginning on d1 and
    ending on d2 which are in the given year
    NOTE: the day of month will not be considered.
          If year is 2019 and d1 is '2019-01-31' january '19 will be counted.
          If year is 2019 and d2 is '2019-12-01' december '19 will be counted.
    :param d1: date the period is beginning. Must be given as iso string 'YYYY-MM-DD'
    :param d2: date the period is ending. Must be given as iso string 'YYYY-MM-DD'
    :param year: a four digit integer like 2019
    :return: number of months
    """
    start:datetime = dateutil.parser.parse(d1)
    dt:datetime = start
    end:datetime = dateutil.parser.parse(d2)
    if end.year > year:
        d2 = str(year) + "-12-31"
        end = dateutil.parser.parse(d2)

    while dt.year < year:
        dt = addMonths(dt, 1)

    cnt = 0
    while dt.year == year and dt <= end:
        dt = addMonths(dt, 1)
        cnt += 1

    return cnt

def getLastMonth() -> Tuple[int, str]:
    monat = datetime.now().month
    monat = 12 if monat == 1 else monat-1
    smonat = monthList[monat-1]
    return monat, smonat

def getRelativeQDate( monthdelta:int, day:int ) -> QDate:
    """
    Returns a date relative to current date.
    :param monthdelta: number of months to add or subtract from current month
    :param day: the day to set
    :return: the created QDate object
    """
    today = datetime.now()
    m = today.month
    y = today.year
    m += monthdelta
    if m == 0:
        m = 12
        y -= 1
    return QDate( y, m, day )


def addYears(mydate: date, cntYears: int) -> date:
    return mydate + relativedelta(years = cntYears)

def addMonths(mydate: date, cntMonths: int) -> date:
    return mydate + relativedelta(months = cntMonths)

def addDays(mydate: date, cntDays: int) -> date:
    return mydate + relativedelta(days = cntDays)

def addDaysToIsoString( isostring:str, cntDays:int ) -> str:
    d = getDateFromIsoString( isostring )
    d = addDays( d, cntDays )
    return getIsoStringFromDate( d )

def test():
    d = QDate( 2020, 12, 3 )
    print( d )
    iso = getIsoStringFromQDate( d )
    print( iso )

    y, m, d = getDateParts( "2020-05-25" )
    y, m, d = getDateParts( "13.11.2019" )
    i = getMonthIndex( "Dezember" )
    print( i )

    s = getTodayAsIsoString()
    d1 = '2019-12-01'
    d2 = '2020-03-10'
    cnt = getNumberOfMonths(d1, d2, 2019)
    print(cnt)

if __name__ == '__main__':
    test()