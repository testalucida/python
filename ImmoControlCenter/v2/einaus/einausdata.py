from typing import List, Dict

import datehelper

from v2.icc.constants import EinAusArt, Umlegbar
from v2.icc.iccdata import IccData, DbAction
from v2.icc.interfaces import XEinAus


class EinAusData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def insertEinAusZahlung( self, x:XEinAus ):
        """
        Fügt der Tabelle <einaus> eine Zahlung hinzu.
        Macht keinen Commit.
        :param x: Daten der Zahlung
        :return: die id des neu angelegten einaus-Satzes
        """
        sab_id = "NULL" if not x.sab_id else str( x.sab_id )
        ea_art_db = EinAusArt.getDbValue( x.ea_art )
        verteilt_auf = "NULL" if not x.verteilt_auf else str( x.verteilt_auf )
        umlegbar = "NULL" if not x.umlegbar else "'" + x.umlegbar + "'"
        buchungsdatum = "NULL" if not x.buchungsdatum else "'" + x.buchungsdatum + "'"
        buchungstext = "NULL" if not x.buchungstext else "'" + x.buchungstext + "'"
        leistung = "NULL" if not x.leistung else "'" + x.leistung + "'"
        writetime = datehelper.getCurrentTimestampIso()
        sql = "insert into einaus " \
              "( master_name, mobj_id, debi_kredi, leistung, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, umlegbar, " \
              "  buchungsdatum, buchungstext, write_time ) " \
              "values" \
              "(   '%s',      '%s',       '%s',     %s,   %s,     %d,   '%s',    %.2f,   '%s',     %s,           %s," \
              "    %s,         %s,        '%s' ) " % ( x.master_name, x.mobj_id, x.debi_kredi, leistung, sab_id,
                                                                   x.jahr, x.monat, x.betrag,
                                                                   ea_art_db, verteilt_auf, umlegbar,
                                                                   buchungsdatum, buchungstext, writetime )
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "einaus", "ea_id", 0,
                                        newvalues=x.toString( printWithClassname=True ), oldvalues=None )
        x.ea_id = inserted_id
        x.write_time = writetime

    def updateEinAusZahlung( self, x:XEinAus ) -> int:
        """
        Ändert die Ein-Aus-Zahlung mit der ID x.ea_id mit den in <x> enthaltenen Werten.
        :param x:
        :return: die Anzahl der geänderten Sätze, also 1 bzw. 0, wenn es die angegebene x.ea_id nicht gibt.
        """
        # den alten Zustand lesen, er wird in die Log-Tabelle geschrieben
        oldX = self.getEinAusZahlung( x.ea_id )
        oldX.ea_art = EinAusArt.getDbValue( oldX.ea_art )
        sab_id = "NULL" if not x.sab_id else str( x.sab_id )
        ea_art_db = EinAusArt.getDbValue( x.ea_art )
        verteilt_auf = "NULL" if not x.verteilt_auf else str( x.verteilt_auf )
        umlegbar = "NULL" if x.umlegbar == Umlegbar.NONE else "'" + x.umlegbar + "'"
        buchungsdatum = "NULL" if not x.buchungsdatum else "'" + x.buchungsdatum + "'"
        buchungstext = "NULL" if not x.buchungstext else "'" + x.buchungstext + "'"
        leistung = "NULL" if not x.leistung else "'" + x.leistung + "'"
        writetime = datehelper.getCurrentTimestampIso()
        sql = "update einaus " \
              "set " \
              "master_name = '%s', " \
              "mobj_id = '%s', " \
              "debi_kredi = '%s', " \
              "leistung = %s, " \
              "sab_id = %s, " \
              "jahr = %d, " \
              "monat = '%s', " \
              "betrag = %.2f, " \
              "ea_art = '%s', " \
              "verteilt_auf = %s, " \
              "umlegbar = %s, " \
              "buchungsdatum = %s, " \
              "buchungstext = %s, " \
              "write_time = '%s' " \
              "where ea_id = %d " % (x.master_name, x.mobj_id, x.debi_kredi, leistung, sab_id,
                                       x.jahr, x.monat, x.betrag,
                                       ea_art_db, verteilt_auf, umlegbar,
                                       buchungsdatum, buchungstext,
                                       writetime, x.ea_id )
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "einaus", "ea_id", x.ea_id,
                                         newvalues=x.toString( True ), oldvalues=oldX.toString( True ) )
        x.write_time = writetime
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
        sql = "select ea_id, master_name, mobj_id, debi_kredi, leistung, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, write_time " \
              "from einaus " \
              "where ea_id = %d " % ea_id
        x = self.readOneGetObject( sql, XEinAus )
        self._mapDbValueToDisplay( (x,) )
        return x

    def getEinAuszahlungenJahr( self, jahr:int ) -> List[XEinAus]:
        """
        Liefert alle Ein- und Auszahlungen im jahr <jahr>
        :param jahr: z.B. 2022
        :return:
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, coalesce(leistung, '') as leistung, " \
              "sab_id, jahr, monat, betrag, ea_art, " \
              "coalesce(verteilt_auf, '') as verteilt_auf, umlegbar, " \
              "coalesce( buchungsdatum, '') as buchungsdatum, coalesce(buchungstext, '') as buchungstext, " \
              "write_time " \
              "from einaus " \
              "where jahr = %d "  % jahr
        xlist = self.readAllGetObjectList( sql, XEinAus )
        self._mapDbValueToDisplay( xlist )
        return xlist

    def getEinAusZahlungen( self, ea_art_display:str, jahr: int ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art_display: erwartet wird hier der display-Wert der versch. EinAusArten, z.B. "Bruttomiete"
        :param jahr: yyyy
        :return:  List[XEinAus]
        """
        ea_art_db = EinAusArt.getDbValue( ea_art_display )
        sql = "select ea_id, master_name, mobj_id, debi_kredi, leistung, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and ea_art = '%s' " % ( jahr, ea_art_db )
        xlist = self.readAllGetObjectList( sql, XEinAus )
        self._mapDbValueToDisplay( xlist )
        return xlist

    def getEinAuszahlungen2( self, ea_art_display:str, jahr:int, monat:str, mobj_id:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art_display: EinAusArt
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param mobj_id: z.B. "thomasmann"
        :return: List[XEinAus]
        """
        ea_art_db = EinAusArt.getDbValue( ea_art_display )
        sql = "select ea_id, master_name, mobj_id, debi_kredi, leistung, sabid, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and mobj_id = '%s' " \
              "and ea_art = '%s' " % (jahr, monat, mobj_id, ea_art_db)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        self._mapDbValueToDisplay( xlist )
        return xlist

    def getEinAuszahlungen3( self, ea_art_display:str, jahr:int, monat:str, debikredi:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param ea_art_display: display value (string) der EinAusArt
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param debikredi: ID des Mieters oder Name der WEG oder Firma
        :return: List[XEinAus]
        """
        ea_art_db = EinAusArt.getDbValue( ea_art_display )
        sql = "select ea_id, master_name, mobj_id, debi_kredi, leistung, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and debi_kredi = '%s' " \
              "and ea_art = '%s' " % (jahr, monat, debikredi, ea_art_db)
        xlist = self.readAllGetObjectList( sql, XEinAus )
        self._mapDbValueToDisplay( xlist )
        return xlist

    def getEinAuszahlungen4( self, sab_id:int, jahr:int, monat:str ) -> List[XEinAus]:
        """
        Liefert eine Liste von XEinAus-Objekten, die den gegebenen Kriterien genügen
        :param sab_id: SollAbschlag-ID
        :param jahr: yyyy
        :param monat: z.B. "jan", "mrz",... siehe iccMonthShortNames
        :param mv_id: ID des Mieters
        :return: List[XEinAus]
        """
        sql = "select ea_id, master_name, mobj_id, debi_kredi, leistung, sab_id, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, write_time " \
              "from einaus " \
              "where jahr = %d " \
              "and monat = '%s' " \
              "and sab_id = %d " % (jahr, monat, sab_id )
        xlist = self.readAllGetObjectList( sql, XEinAus )
        self._mapDbValueToDisplay( xlist )
        return xlist

    def _mapDbValueToDisplay( self, xlist:List[XEinAus] ):
        for x in xlist:
            if x.ea_art:
                x.ea_art = EinAusArt.getDisplay( x.ea_art )

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
    x.ea_art = EinAusArt.BRUTTOMIETE.dbvalue

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
    x = XEinAus()
    x.master_name = "ER_Heuschlag"
    x.mobj_id = "heuschlag"
    x.ea_art = EinAusArt.ALLGEMEINE_KOSTEN.display
    x.jahr = 2022
    x.monat = "nov"
    x.umlegbar = "nein"
    x.verteilt_auf = 1
    x.buchungsdatum = "2022-11-29"
    x.betrag = 100.0

    data = EinAusData()
    try:
        data.insertEinAusZahlung( x )
        data.commit()
    except Exception as ex:
        print( str(ex) )