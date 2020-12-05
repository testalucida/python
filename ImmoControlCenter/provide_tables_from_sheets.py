from pandas_ods_reader import read_ods
from dbaccess import DbAccess, mon_dbnames
import math
import functools
from typing import Dict, List
#
stammdatenpath = "/home/martin/Projects/python/ImmoControlCenter/Stammdaten_TEST.ods"
einaus20path = "/home/martin/Projects/python/ImmoControlCenter/Ein_Aus_2020_TEST.ods"

db = DbAccess( "immo_TEST.db")
db.open()

def provideSollmiete():
    sheetname = "sollmiete"
    df = read_ods(stammdatenpath, sheetname)
    for index, row in df.iterrows():
        d = row.to_dict()
        for k, v, in d.items():
            if v is None:
                d[k] = ''
        #TODO: re-implement insertSollmiete (data structure has changed)
        db.insertSollmiete( d, False )
    db.commit()

def provideMietverhaeltnis():
    sheet_name = "Mietverhaeltnis"
    df = read_ods(stammdatenpath, sheet_name)
    #print( df )
    for index, row in df.iterrows():
        d = row.to_dict()
        for k, v in d.items():
            if v is None:
                d[k] = ''
            if k == "anzpers":
                if math.isnan( v ): v = 1
                else: d["anzpers"] = int( v )
        db.insertMietverhaeltnis( d, False )
        # for k, v in d.items():
        #     print( k, ": ", v )
        # print("index: ", index, "; row: ", row)
    db.commit()

def provideMiete2020():
    sheet_name = "Miete_2020"
    df = read_ods( einaus20path, sheet_name )
    for index, row in df.iterrows():
        d = row.to_dict()
        print( "processing mietobjekt ", d["mietobjekt_id"] )
        for m in range( 1, 11 ): #nur bis Oktober gefüllt
            monat = mon_dbnames[m-1]
            value = d[monat.title()]
            value = 0 if math.isnan( value ) else value
            ### obsolete db.updateMtlEinAus( d["mietobjekt_id"], "miete", 2020, m, value )
    db.commit()

def provideServiceleistungen2020():
    sheet_name = "Zahlungen_2020"
    df = read_ods( einaus20path, sheet_name )
    servicelist = []
    for index, row in df.iterrows():
        d = row.to_dict()
        if d["name"] is None: continue
        #print( d )
        servicelist.append( d )
    servicelist.sort( key=functools.cmp_to_key( compareDics ) )
    for di in servicelist:
        print( di )
    print( "#######################################################################")
    servicelist = removeDuplicates( servicelist )
    for di in servicelist:
        print( di )

def compareDics( d1:Dict, d2:Dict ) -> int:
    cmp1 = compareString( d1["name"], d2["name"] )
    if cmp1 != 0: return cmp1
    cmp2 = compareString( d1["objekt"], d2["objekt"] )
    if cmp2 != 0: return cmp2
    return compareString( d1["buchungstext"], d2["buchungstext"] )

def compareString( s1:str, s2: str ) -> int:
    """
    return 1 if s1 > s2
    return 0 if s1 == s2
    return -1 if s1 < s2
    :param s1:
    :param s2:
    :return:
    """
    if s1 is None: s1 = ""
    if s2 is None: s2 = ""
    if s1 > s2: return 1
    if s1 == s2: return 0
    return -1

def removeDuplicates( l:List[Dict] ) -> List[Dict]:
    name = ""
    objekt = ""
    buchungstext = ""
    newlist = []
    for d in l:
        if name == d["name"] and objekt == d["objekt"] and buchungstext == d["buchungstext"]:
            continue
        newlist.append( d )
        name = d["name"]
        objekt = d["objekt"]
        buchungstext = d["buchungstext"]
    return newlist

if __name__ == "__main__":
    provideServiceleistungen2020()
    pass
    #provideMietverhaeltnis()
    #provideSollmiete()
    #provideMiete2020()