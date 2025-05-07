from pandas_ods_reader import read_ods
import math
from typing import Dict
#
anlagevpath = "/home/martin/kendelweb.de/.private/vermietung/saar/Anlagen_V/2019/AnlagenV_2019.ods"

def read_anlagevsheets():
    for sheet in range( 1, 19 ):
        #sheet = 1
        df = read_ods( anlagevpath, sheet )
        for index, row in df.iterrows():
            print( "index: ", index )
            if index == 14:
                d = row.to_dict()
                for k, v, in d.items():
                    print( "key: ", k, "; value: ", v )


def read_anlagevsheets2():
    for sheet in range( 1, 19 ):
        df = read_ods( anlagevpath, sheet )

        for index, row in df.iterrows():
            print( "index: ", index )
            d = row.to_dict()
            val = d["Zeile"]
            if not math.isnan( val ):
                val = int( val )
                if val == 23:
                    print( "sheet ", index, ": ", d["Text"], ": ", val )

def read_anlagevsheets3():
    ueberschuss = 0
    afa = 0
    for sheet in range( 1, 19 ):
        df = read_ods( anlagevpath, sheet )
        for index, row in df.iterrows():
            d = row.to_dict()
            #print( index, ": ", d )
            if d["Zeile"] == 23:
                ueberschuss += d["Betrag im Vj"]
                print( sheet, "  Überschuss: ", d["Betrag im Vj"] )
            if d["Zeile"] == 33:
                afa += d["Betrag im Vj"]
                print(sheet, "  AfA: ", d["Betrag im Vj"])
                break

    print( "Gesamtüberschuss: ", ueberschuss, "---GesamtAfA: ", afa )


if __name__ == "__main__":
    #provideMietverhaeltnis()
    #provideSollmiete()
    read_anlagevsheets3()