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
        Macht keinen Commit.
        :param x: Daten der Zahlung
        :return: die id des neu angelegten einaus-Satzes
        """
        sab_id = "NULL" if not x.sab_id else str( x.sab_id )
        verteilt_auf = "NULL" if not x.verteilt_auf else str( x.verteilt_auf )
        umlegbar = "NULL" if not x.umlegbar else str( x.umlegbar )
        buchungsdatum = "NULL" if not x.buchungsdatum else "'" + x.buchungsdatum + "'"
        buchungstext = "NULL" if not x.buchungstext else "'" + x.buchungstext + "'"
        mehrtext = "NULL" if not x.mehrtext else "'" + x.mehrtext + "'"
        writetime = datehelper.getCurrentTimestampIso()
        sql = "insert into einaus " \
              "( master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, umlegbar, " \
              "  buchungsdatum, buchungstext, mehrtext, write_time ) " \
              "values" \
              "(   '%s',      '%s',       '%s',     %s,     %d,   '%s',    %.2f,   '%s',     %s,           %s," \
              "    %s,         %s,         %s,     '%s' ) " % ( x.master_name, x.mobj_id, x.debi_kredi, sab_id,
                                                                   x.jahr, x.monat, x.betrag,
                                                                   x.ea_art, verteilt_auf, umlegbar,
                                                                   buchungsdatum, buchungstext, mehrtext,
                                                                   writetime )
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "einaus", "ea_id", 0,
                                        newvalues=x.toString( printWithClassname=True ), oldvalues=None )
        return inserted_id

    def updateEinAusZahlung( self, x:XEinAus ) -> int:
        """
        Ändert die Ein-Aus-Zahlung mit der ID x.ea_id mit den in <x> enthaltenen Werten.
        :param x:
        :return: die Anzahl der geänderten Sätze, also 1 bzw. 0, wenn es die angegebene x.ea_id nicht gibt.
        """
        # den alten Zustand lesen, er wird in die Log-Tabelle geschrieben
        oldX = self.getEinAusZahlung( x.ea_id )
        sab_id = "NULL" if not x.sab_id else str( x.sab_id )
        verteilt_auf = "NULL" if not x.verteilt_auf else str( x.verteilt_auf )
        umlegbar = "NULL" if not x.umlegbar else str( x.umlegbar )
        buchungsdatum = "NULL" if not x.buchungsdatum else "'" + x.buchungsdatum + "'"
        buchungstext = "NULL" if not x.buchungstext else "'" + x.buchungstext + "'"
        mehrtext = "NULL" if not x.mehrtext else "'" + x.mehrtext + "'"
        writetime = datehelper.getCurrentTimestampIso()
        sql = "update einaus " \
              "set " \
              "master_name = '%s', " \
              "mobj_id = '%s', " \
              "debi_kredi = '%s', " \
              "sabid = %s, " \
              "jahr = %d, " \
              "monat = '%s', " \
              "betrag = %.2f, " \
              "ea_art = '%s', " \
              "verteilt_auf = %s, " \
              "umlegbar = %s, " \
              "buchungsdatum = %s, " \
              "buchungstext = %s, " \
              "mehrtext = %s, " \
              "write_time = '%s' " \
              "where ea_id = %d " % (x.master_name, x.mobj_id, x.debi_kredi, x.sab_id,
                                       x.jahr, x.monat, x.betrag,
                                       x.ea_art, verteilt_auf, umlegbar,
                                       buchungsdatum, buchungstext, mehrtext,
                                       writetime, x.ea_id )
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "einaus", "ea_id", x.ea_id,
                                         newvalues=x.toString( True ), oldvalues=oldX.toString( True ) )
        return rowsAffected

    def deleteEinAusZahlung( self, ea_id:int ):
        """
        Löscht eine Zahlung aus <einaus>.
        Macht keinen Commit.
        :param ea_id:
        :return:
        """
        x = self.getEinAusZahlung( ea_id )
        sql = "delete from einaus where ea_id = %d" % ea_id
        self.writeAndLog( sql, DbAction.DELETE, "einaus", "ea_id", ea_id,
                          newvalues=None, oldvalues=x.toString( printWithClassname=True )  )

    def getEinAusZahlung( self, ea_id:int ) -> XEinAus:
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where ea_id = %d " % ea_id
        x = self.readOneGetObject( sql, XEinAus )
        return x

    def getEinAuszahlungenJahr( self, jahr:int ) -> List[XEinAus]:
        """
        Liefert alle Ein- und Auszahlungen im jahr <jahr>
        :param jahr: z.B. 2022
        :return:
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, " \
              "coalesce(verteilt_auf, '') as verteilt_auf, umlegbar, " \
              "coalesce( buchungsdatum, '') as buchungsdatum, coalesce(buchungstext, '') as buchungstext, " \
              "coalesce(mehrtext, '') as mehrtext, write_time " \
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
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
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
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sabid, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and mobj_id = '%s' " \
              "and ea_art = '%s' " % (jahr, monat, mobj_id, ea_art)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist

    def getEinAuszahlungen3( self, ea_art:str, jahr:int, monat:str, debikredi:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art: EinAusArt
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param mv_id: ID des Mieters
        :return: List[XEinAus]
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and debi_kredi = '%s' " \
              "and ea_art = '%s' " % (jahr, monat, debikredi, ea_art)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist

    def getEinAuszahlungen4( self, sab_id:int, jahr:int, monat:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art: EinAusArt
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param mv_id: ID des Mieters
        :return: List[XEinAus]
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and sab_id = %d " % (jahr, monat, sab_id )
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