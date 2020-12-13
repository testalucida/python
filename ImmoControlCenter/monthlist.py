
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

def getMonatsletzter( monat:str ):
    return monatsletzte[monat]

