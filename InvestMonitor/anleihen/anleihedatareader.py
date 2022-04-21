from functools import cmp_to_key
from typing import List

from pandas_ods_reader import read_ods
from interface.interfaces import PopoTable, PortfolioPosition
import os

path="/home/martin/Documents/AA_Vermoegen/DKB/"

def getDepotDownloads():
    dirlist = os.listdir( path )
    for entry in dirlist:
        item = os.path.join( path, entry )
        print( item )



def getDKBAnleihen( df ) -> PopoTable:
    """
    Creates a PopoTable from the given DataFrame and returns that PopoTable
    :param df:
    :return:
    """
    popoTable = None
    idxIsin, idxBez, idxKurs, idxKurswert, idxBestand = -1, -1, -1, -1, -1
    for index, row in df.iterrows():
        # index: zero based row number
        # row: class 'pandas.core.series.Series'
        d = row.to_dict()
        values = list( d.values() ) # all cell values in <row>
        if isinstance( values[0], str ) and values[0].startswith( "Depotgesamtwert per" ):
            timestamp = values[1]
            popoTable = PopoTable( timestamp )
        if idxIsin < 0:
            # find interesting columns
            try:
                idxIsin = values.index( "ISIN / WKN" )
                idxBez = values.index( "Bezeichnung" )
                idxKurs = values.index( "Kurs" )
                idxKurswert = values.index( "Kurswert in Euro" )
                idxBestand = values.index( "Bestand" )
                continue
            except:
                continue
        else:
            if not values[idxBez].startswith( "AMUNDI" ):
                popo = PortfolioPosition()
                popo.bezeichnung = values[idxBez]
                popo.isin = values[idxIsin]
                popo.kurs = values[idxKurs]
                popo.kurswert = values[idxKurswert]
                popo.nennwert = values[idxBestand]
                popoTable.addPopo( popo )
    return popoTable

def snapshotCompare( p1:PopoTable, p2:PopoTable ) -> int:
    d1 = p1.getSnapshotDate()
    d2 = p2.getSnapshotDate()
    t1 = p1.getSnapshotTime()
    t2 = p2.getSnapshotTime()
    if d1 > d2: return 1
    if d1 == d2:
        if t1 > t2: return 1
        if t1 == t2: return 0
        if t1 < t2: return -1
    if d1 < d2: return -1

def getAllDKBAnleihen() -> List[PopoTable]:
    """
    returns a List containing PopoTable's sorted by snapshot ascending
    :return:
    """
    sheet_idx = 1
    popotableList = list()
    dirlist = os.listdir( path )
    for entry in dirlist:
        item = os.path.join( path, entry )
        if not item.endswith( ".ods" ):
            continue
        print( item )
        df = read_ods( item, sheet_idx )
        popotable = getDKBAnleihen( df )
        popotableList.append( popotable )
    popotableList = sorted( popotableList, key=cmp_to_key( snapshotCompare ) )
    return popotableList

def test1():
    popotableList = getAllDKBAnleihen()
    print( popotableList )

def test2():
    path = "../testdata/Depotstand_20220330.ods"
    # load a sheet based on its index (1 based)
    sheet_idx = 1
    df = read_ods(path, sheet_idx)
    popotable = getDKBAnleihen( df )
    popotable.print()