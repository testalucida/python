from pandas_ods_reader import read_ods
from dbaccess import DbAccess, mon_dbnames
import math
from typing import Dict
#
stammdatenpath = "/home/martin/Projects/python/ImmoControlCenter/Stammdaten_TEST.ods"
einaus20path = "/home/martin/Projects/python/ImmoControlCenter/Ein_Aus_2020_TEST.ods"

db = DbAccess()
db.open()

def provideSollmiete():
    sheetname = "sollmiete"
    df = read_ods(stammdatenpath, sheetname)
    for index, row in df.iterrows():
        d = row.to_dict()
        for k, v, in d.items():
            if v is None:
                d[k] = ''
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
            db.updateMtlEinAus( d["mietobjekt_id"], "miete", 2020, m, value )
    db.commit()

if __name__ == "__main__":
    #provideMietverhaeltnis()
    #provideSollmiete()
    provideMiete2020()