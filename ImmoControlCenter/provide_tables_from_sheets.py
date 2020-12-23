from pandas_ods_reader import read_ods
from dbaccess import DbAccess, mon_dbnames
import math
import functools
from typing import Dict, List
#
stammdatenpath = "/home/martin/Projects/python/ImmoControlCenter/Stammdaten_TEST.ods"
einaus20path = "/home/martin/Projects/python/ImmoControlCenter/Ein_Aus_2020_TEST.ods"

db = DbAccess( "immo.db")
db.open()

def provideMietobjekte():
    sheetname = "Wohnung"
    df = read_ods( stammdatenpath, sheetname )
    for index, row in df.iterrows():
        d = row.to_dict()
        d["master_id"] = 0
        d["aktiv"] = 1
        d["container_nr"] = ""
        if math.isnan( d["qm"] ): d["qm"] = 0
        db.insertMietobjekt( d, False )
        print( d )
    db.commit()


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
    for index, row in df.iterrows():
        d = row.to_dict()
        d["mv_id"] = create_mv_id( d["name"], d["vorname"] )
        d["bis"] = ""
        for k, v in d.items():
            if v is None:
                d[k] = ''
            if k == "anzahl_pers":
                if math.isnan( v ):
                    d["anzahl_pers"] = 1
                else:
                    d["anzahl_pers"] = int( v )
        db.insertMietverhaeltnis( d, False )
    db.commit()

def create_mv_id( name:str, vorname:str ) -> str:
    if not name:
        raise Exception( "No name given" )
    if not vorname: vorname = ""
    name = name.lower()
    vorname = vorname.lower()
    charlist = ( "ä", "ö", "ü", "ß" )
    if any( x in name for x in charlist ):
        name = replaceUmlaute( name )
    if any( x in vorname for x in charlist ):
        vorname = replaceUmlaute( vorname )
    name = name.replace( " ", "" )
    name = name.replace( "-", "" )
    name = name.replace( "+", "" )
    vorname = vorname.replace( " ", "" )
    vorname = vorname.replace( "-", "" )
    return name if not vorname else name + "_" + vorname


def replaceUmlaute( s:str ) -> str:
    # Funktion geht davon aus, dass s in Kleinbuchstaben ankommt, also ohen Ä, Ö, Ü
    chars = { 'ö': 'oe', 'ä': 'ae', 'ü': 'ue', 'ß': 'ss' }
    for char in chars:
        s = s.replace( char, chars[char] )
    return s

def provideVerwaltung():
    sheet_name = "Wohnung"
    df = read_ods( stammdatenpath, sheet_name )
    for index, row in df.iterrows():
        d = row.to_dict()
        d["von"] = "2019-01-01"
        d["bis"] = ""
        if not d["vw_id"]: continue
        db.insertVerwaltung( d, False )
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


############################## provideServiceleistungen2020  A N F A N G #############################
def provideServiceleistungen2020():
    sheet_name = "Zahlungen_2020"
    df = read_ods( einaus20path, sheet_name )
    servicelist = []
    for index, row in df.iterrows():
        d = row.to_dict()
        if d["name"] is None: continue
        d["name"] = d["name"].strip()
        if d["objekt"] is None:
            d["objekt"] = ""
        else:
            d["objekt"] = d["objekt"].strip()
        servicelist.append( d )
    servicelist.sort( key=functools.cmp_to_key( compareDics ) )
    servicelist = removeDuplicates( servicelist )
    insertIntoServiceleistung( servicelist )

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

def insertIntoServiceleistung( servicelist:List[Dict] ) -> None:
    for s in servicelist:
        print( s )
        db.insertServiceleistung( s["name"], s["objekt"], s["buchungstext"], 0, False )
    db.commit()

############################## provideServiceleistungen2020 E N D E #############################

if __name__ == "__main__":
    pass
    #provideVerwaltung()
    #provideServiceleistungen2020()
    #provideMietobjekte()
    #pass
    #provideMietverhaeltnis()
    #provideSollmiete()
    #provideMiete2020()