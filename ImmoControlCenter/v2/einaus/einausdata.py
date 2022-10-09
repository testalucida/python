from typing import List, Dict

import datehelper

from v2.icc.constants import EinAusArt
from v2.icc.iccdata import IccData, DbAction
from v2.icc.interfaces import XEinAus


class EinAusData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def insertEinAusZahlung( self, x:XEinAus ) -> int:
        """
        Fügt der Tabelle <einaus> eine Zahlung hinzu.
        :param x: Daten der Zahlung
        :return: die id des neu angelegten einaus-Satzes
        """
        verteilt_auf = "NULL" if not x.verteilt_auf else x.verteilt_auf
        umlegbar = "NULL" if not x.umlegbar else x.umlegbar
        writetime = datehelper.getCurrentTimestampIso()
        sql = "insert into einaus " \
              "( master_name, mobj_id, debi_kredi, jahr, monat, betrag, ea_art, verteilt_auf, umlegbar, " \
              "  buchungsdatum, buchungstext, mehrtext, write_time ) " \
              "values" \
              "(   '%s',      '%s',       '%s',     %d,   '%s',    %.2f,   '%s',     %s,           %s," \
              "    '%s',      '%s',       '%s',    '%s' ) " % ( x.master_name, x.mobj_id, x.debi_kredi,
                                                                   x.jahr, x.monat, x.betrag,
                                                                   x.ea_art, verteilt_auf, umlegbar,
                                                                   x.buchungsdatum, x.buchungstext, x.mehrtext,
                                                                   writetime )
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "einaus", "ea_id", 0, x.toString( printWithClassname=True ) )
        return inserted_id

    def getEinAuszahlungenJahr( self, jahr:int ) -> List[XEinAus]:
        """
        Liefert alle Ein- und Auszahlungen im jahr <jahr>
        :param jahr: z.B. 2022
        :return:
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d "  % (jahr)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist

    def getEinAusZahlungen( self, ea_art:str, jahr: int ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art: EinAusArt
        :param jahr: yyyy
        :return:  List[XEinAus]
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and ea_art = '%s' " % (jahr, ea_art)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist

    def getEinAuszahlungen2( self, ea_art:str, jahr:int, monat:str, mobj_id:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art: EinAusArt
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param mobj_id: z.B. "thomasmann"
        :return: List[XEinAus]
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and mobj_id = '%s' " \
              "and ea_art = '%s' " % (jahr, monat, mobj_id, ea_art)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist


######################################################################

def test3():
    data = EinAusData()
    try:
        master = data.getMastername( "remgius" )
        print( master )
    except Exception as ex:
        print( "Exception: " + str(ex) )


def test2():
    x = XEinAus()
    x.master_name = "GULP"
    x.mobj_id = "schluck"
    x.debi_kredi = "hans_otto"
    x.jahr = 2022
    x.monat = "okt"
    x.betrag = 234.55
    x.ea_art = EinAusArt.BRUTTOMIETE.value[0]

    data = EinAusData()
    try:
        #data.begin_transaction()
        data.insertEinAusZahlung( x )
        data.commit()
        #data.commit_transaction()
    except Exception as ex:
        print( str(ex) )

def test1():
    #db = DatabaseCommon( "/home/martin/Projects/python/ImmoControlCenter/v2/icc/immo.db" )
    data = EinAusData()
    sql = "update einaus set ea_art = 'lfdskj' where ea_id = 3 "
    ret = data.write( sql )
    print( ret )
    #data.commit()
    data.rollback()


def test():
    ea_art = EinAusArt.BRUTTOMIETE
    print( ea_art.value[0] )

    data = EinAusData()
    l = data.getJahre()
    print( l )
    l = data.getEinAusZahlungen( EinAusArt.BRUTTOMIETE, 2022 )
    print( l )