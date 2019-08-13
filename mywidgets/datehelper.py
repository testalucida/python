from datetime import datetime, date

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

def convertEurToIso(eurstring: str) -> str:
    """
    converts an eurdatestring int an iso datestring
    ('29.08.2019' into '2019-08-29')
    :param eurstring:
    :return: a converted datestring
    """
    if not eurstring:
        return ''

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


# d1 = '23.04.1988'
# d2 = '12.03.2999'
# rc = compareEurDates(d1, d2)