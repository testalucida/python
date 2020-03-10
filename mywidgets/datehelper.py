from datetime import datetime, date
import dateutil.parser
from dateutil.relativedelta import relativedelta

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
    start = dateutil.parser.parse(d1)
    dt = start
    end = dateutil.parser.parse(d2)

    while dt.year < year:
        dt = addMonths(dt, 1)

    cnt = 0
    while dt.year == year and dt <= end:
        dt = addMonths(dt, 1)
        cnt += 1

    return cnt

def addYears(mydate: date, cntYears: int) -> date:
    return mydate + relativedelta(years = cntYears)

def addMonths(mydate: date, cntMonths: int) -> date:
    return mydate + relativedelta(months = cntMonths)

def addDays(mydate: date, cntDays: int) -> date:
    return mydate + relativedelta(days = cntDays)



def test():
    s = getTodayAsIsoString()
    d1 = '2018-01-01'
    d2 = '2018-12-01'
    cnt = getNumberOfMonths(d1, d2, 2018)
    print(cnt)

if __name__ == '__main__':
    test()