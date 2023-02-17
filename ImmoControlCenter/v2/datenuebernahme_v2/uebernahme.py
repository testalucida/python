import numbers
import sqlite3
from typing import List, Dict, Tuple

from PySide2.QtWidgets import QApplication

from base.messagebox import WarningBox, InfoBox, ErrorBox
from messagebox import MessageBox
from v2.icc.constants import EinAusArt, Umlegbar
from v2.icc.definitions import DATENUEBERNAHME_DIR, ROOT_DIR
from v2.icc.iccdata import IccData


class Data:
    def __init__( self, pathToDb ):
        self._pathToDb = pathToDb
        self._sqliteCon: sqlite3.dbapi2.Connection = sqlite3.connect( pathToDb )

    def selectTable( self, tablename, whereCond: str = "" ) -> List[Dict]:
        sql = "select * from " + tablename + " " + whereCond
        return self.readAllGetDict( sql )

    def read( self, sql: str ) -> List[Tuple]:
        cur = self._sqliteCon.cursor() # sieht umständlich aus, muss aber so gemacht werden:
                                 # mit jedem cursor()-call wird ein neuer Cursor erzeugt!
        cur.execute( sql )
        records = cur.fetchall()
        cur.close()
        return records

    @staticmethod
    def dict_factory( cursor, row ):
        d = { }
        for idx, col in enumerate( cursor.description ):
            d[col[0]] = row[idx]
        return d

    def readAllGetDict( self, sql: str ) -> List[Dict] or None:
        self._sqliteCon.row_factory = self.dict_factory
        cur = self._sqliteCon.cursor()
        cur.execute( sql )
        dicList = cur.fetchall()
        self._sqliteCon.row_factory = None
        cur.close()
        return dicList

    def readOneGetDict( self, sql: str ) -> Dict or None:
        self._sqliteCon.row_factory = self.dict_factory
        cur = self._sqliteCon.cursor()
        cur.execute( sql )
        dic = cur.fetchone()
        self._sqliteCon.row_factory = None
        cur.close()
        return dic

class SrcData( Data ):
    """
    Zugriffe auf die alte Datenbank - nur lesend
    """
    def __init__(self, pathToSrcDb ):
        Data.__init__( self, pathToSrcDb )

    def selectMietobjekte( self ):
        sql = "select mobj.mobj_id, mobj.master_id, master.master_name, mobj.whg_bez, mobj.qm, mobj.container_nr, " \
              "mobj.bemerkung, mobj.aktiv " \
              "from mietobjekt mobj " \
              "inner join masterobjekt master on master.master_id = mobj.master_id " \
              "where mobj_id > ' ' and mobj_id not like '%*' "
        return self.readAllGetDict( sql )

    def selectVerwaltung( self ):
        sql = "select vwg.master_id, vwg.mobj_id, vwg.vw_id, vwg.weg_name, vwg.von, vwg.bis, master.master_name " \
              "from verwaltung vwg " \
              "inner join masterobjekt master on master.master_id = vwg.master_id "
        return self.readAllGetDict( sql )

    def selectMieten( self ):
        sql = "select 'bruttomiete' as ea_art, " \
              "z.mobj_id, master.master_name, mea.mv_id as debi_kredi, " \
              "z.jahr, z.monat, z.betrag, z.write_time " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "inner join mtleinaus mea on mea.meinaus_id = z.meinaus_id " \
              "where z.zahl_art = 'bruttomiete' "
        return self.readAllGetDict( sql )

    def selectSollHausgeld( self ):
        sql = "select soll.vwg_id, master.master_name, soll.von, soll.bis, soll.netto, soll.ruezufue, soll.bemerkung, " \
                "vwg.mobj_id, vwg.vw_id, vwg.weg_name " \
                "from sollhausgeld soll " \
                "inner join verwaltung vwg on vwg.vwg_id = soll.vwg_id " \
                "inner join masterobjekt master on master.master_id = vwg.master_id "
        return self.readAllGetDict( sql )

    def selectHgvZahlungen( self ):
        sql = "select 'hgv' as ea_art, " \
              "z.mobj_id, master.master_name, vwg.weg_name as debi_kredi, " \
              "z.jahr, z.monat, z.betrag, z.write_time " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "inner join mtleinaus mea on mea.meinaus_id = z.meinaus_id " \
              "inner join verwaltung vwg on vwg.vwg_id = mea.vwg_id " \
              "where z.zahl_art = 'hgv' " \
              "and z.mobj_id not like '%*' "
        return self.readAllGetDict( sql )

    def selectNkaZahlungen( self ):
        sql = "select 'nka' as ea_art, " \
              "z.nka_id, z.mobj_id, z.jahr, z.monat, z.betrag, z.write_time, " \
              "nka.ab_jahr, nka.mv_id as debi_kredi, " \
              "master.master_name " \
              "from zahlung z " \
              "inner join nk_abrechnung nka on nka.nka_id = z.nka_id " \
              "inner join mietobjekt mo on mo.mobj_id = z.mobj_id " \
              "inner join masterobjekt master on master.master_id = mo.master_id "
        return self.readAllGetDict( sql )

    def selectHga( self ):
        sql = "select ab_jahr, hga.vwg_id, vwg.vw_id, vwg.mobj_id, betrag as forderung, entnahme_rue, ab_datum, bemerkung " \
              "from hg_abrechnung hga " \
              "inner join verwaltung vwg on vwg.vwg_id = hga.vwg_id "
        return self.readAllGetDict( sql )

    def selectNka( self ):
        sql = "select ab_jahr, mv_id, betrag as forderung, ab_datum, bemerkung " \
              "from nk_abrechnung "
        return self.readAllGetDict( sql )

    def selectHgaZahlungen( self ):
        sql = "select 'hga' as ea_art, z.mobj_id, z.hga_id, z.jahr, z.monat, z.betrag, z.buchungsdatum, " \
              "z.write_time, " \
              "hga.ab_jahr, vwg.weg_name as debi_kredi, master.master_name " \
              "from zahlung z " \
              "inner join hg_abrechnung hga on hga.hga_id = z.hga_id " \
              "inner join verwaltung vwg on vwg.vwg_id = hga.vwg_id " \
              "inner join masterobjekt master on master.master_id = vwg.master_id " \
              "where zahl_art = 'hga'"
        return self.readAllGetDict( sql )

    def selectSonstAusZahlungen( self ):
        sql = "select z.kostenart as ea_art, z.mobj_id, z.hga_id, z.jahr, z.monat, z.betrag, z.umlegbar, " \
              "z.buchungstext as zbuchungstext, z.buchungsdatum, z.write_time, " \
              "sa.kreditor as debi_kredi, sa.buchungstext, sa.rgtext, sa.verteilen_auf_jahre as verteilt_auf, " \
              "master.master_name " \
              "from zahlung z " \
              "inner join sonstaus sa on sa.saus_id = z.saus_id " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "where zahl_art = 'sonstaus' " \
              "and z.kostenart <> 'sam' " \
              "and z.mobj_id not like '%*' "
        return self.readAllGetDict( sql )

#################################################################
class DestData( Data ):
    """
    Zugriffe auf die neue v2-Datenbank -- schreibend
    """
    def __init__(self, pathToDestDb ):
        Data.__init__( self, pathToDestDb )
        self._sqliteCon.isolation_level = None
        self._cursor = self._sqliteCon.cursor()
        self._cursor.execute( "begin" )

    def selectHgaKerndaten( self ):
        sql = "select hga.hga_id, hga.ab_jahr, hga.vwg_id, vwg.weg_name, vwg.mobj_id, ab_datum " \
              "from hg_abrechnung hga " \
              "inner join verwaltung vwg on vwg.vwg_id = hga.vwg_id "
        return self.readAllGetDict( sql )

    def selectNkaKerndaten( self ):
        sql = "select nka_id, ab_jahr, mv_id " \
              "from nk_abrechnung "
        return self.readAllGetDict( sql )

    def clearTable( self, tablename:str ):
        sql = "delete from " + tablename
        self._cursor.execute( sql )

    def getColumnNames( self, table:str ) -> List:
        sql = "select sql from sqlite_master where type = 'table' and tbl_name = '%s' " % table
        dic = self.readOneGetDict( sql )
        create_stmt = dic["sql"]
        return self._createColumnNameList( create_stmt )

    @staticmethod
    def _createColumnNameList( create_stmt:str ) -> List:
        l = list()
        p1 = create_stmt.find( "(" )
        p2 = create_stmt.find( ")" )
        s = create_stmt[p1:p2]
        p1 = s.find( '"' )
        p2 = s.find( '"', p1 + 1 )
        while p1 > -1 and p2 > -1 :
            col = s[p1+1:p2]
            print( col )
            p1 = s.find( '"', p2+1 )
            p = s.find( "AUTOINCREMENT", p2, p1 )
            if p < 0:
                l.append( col )
            p2 = s.find( '"', p1+1 )
        return l

    @staticmethod
    def createInsertStatement( dest_table: str, dest_columns: List[str], row: [Dict] ) -> str:
        columns = list()
        values = list()
        for col in dest_columns:
            try:
                # prüfen, ob die Spalte auch in der Src-Tabelle enthalten ist. Wenn nein, übergehen wir
                # diese Spalte und kommen zur nächsten
                val = row[col]
                if not val is None:
                    if not isinstance( val, numbers.Number ):
                        val = "'" + val + "'"
                    columns.append( col )
                    values.append( val )
                else:
                    # wenn der Wert in der Src-Tabelle None (NULL) ist, hoffen wir mal, dass die
                    # entsprechende Spalte in der Dest-Tabelle auch Nullable ist und lassen sie aus
                    # dem Insert-Stmt raus.
                    continue
            except Exception as ex:
                # dürfte eigtl. nur auftreten, wenn die Spalte in der Dest-Tabelle, aber nicht in der Src-Tabelle
                # vorhanden ist. Dann wird sie beim Insert ignoriert.
                # (Sie ist dann hoffentlich in der Dest-Tabelle nullable, sonst knallt's beim Insert.)
                print( "DestData.createInsertStatment():\n", str(ex) )
                continue

        anz_cols = len( columns )
        if anz_cols <= 0:
            raise Exception( "DestData.createInsertStatment():\nTabelle '%s' hat keine Spalten" % dest_table )
        stmt = "insert into " + dest_table + "("
        for col in columns:
            stmt += (col + ",")
        stmt = stmt[:-1]
        stmt += ") values ("
        for val in values:
            if isinstance( val, numbers.Number ):
                stmt += str(val)
            else:
                stmt += val
            stmt += ","
        stmt = stmt[:-1]
        stmt += ")"
        return stmt

    def insert( self, stmt:str ):
        c = self._cursor.execute( stmt )
        return c.lastrowid

    def commit( self ):
        self._cursor.execute( "commit" )

    def rollback( self ):
        self._cursor.execute( "rollback" )

##################################################################
class DatenUebernahmeLogic:
    def __init__(self, pathToSrcDb, pathToDestDb ):
        self._srcData = SrcData( pathToSrcDb ) # die "alte" Datenbank mit den zu übernehmenden Daten ("Quelle") -- LESEZUGRIFF
        self._destData = DestData( pathToDestDb )  # die "neue" v2-Datenbank, in die die Daten geschrieben werden ("Ziel")
                                                                                                # -- SCHREIBZUGRIFF
    def run( self ):
        # 1.) Daten der Master-Tabelle übernehmen
        #self._copyMaster()     --> done
        #self._copyMietobjekt()  --> done
        # self._copyMietverhaeltnisse() --> done
        #self._copyVerwalter()  --> done
        #self._copyVerwaltung()  --> done
        #self._copySollHausgeld()  --> done
        # self._copySollMiete() --> done
        #self._copyAbrechnungen() --> done
        #self._copyZahlungen()
        self._destData.commit()

    def _copySollMiete( self ):
        table = "sollmiete"
        dictlist = self._srcData.selectTable( table )
        self._writeDestTable( table, dictlist )

    def _copySollHausgeld( self ):
        table = "sollhausgeld"
        shglist = self._srcData.selectSollHausgeld()
        # die Soll-Hausgelder haben alle die "alte" vwg_id.
        # wir müssen die in der dest-Datenbank bereits angelegten Verwaltungen holen, die "neuen" vwg_id entnehmen und
        # in die Soll-Hausgelder der shglist eintragen.
        shglist = sorted( shglist, key=lambda d: d["weg_name"]  )
        dest_vwglist = self._destData.selectTable( "verwaltung" )
        dest_vwglist = sorted( dest_vwglist, key=lambda d: d["weg_name"] )
        for shg in shglist:
            for dest_vwg in dest_vwglist:
                if shg["weg_name"] == dest_vwg["weg_name"] \
                and shg["master_name"] == dest_vwg["master_name"] \
                and shg["mobj_id"] == dest_vwg["mobj_id"] \
                and shg["vw_id"] == dest_vwg["vw_id"]:
                    shg["vwg_id"] = dest_vwg["vwg_id"]
                    break
        self._writeDestTable( table, shglist )

    def _copyAbrechnungen( self ):
        self._copyHga()
        self._copyNka()
        pass

    def _copyNka( self ):
        nkalist = self._srcData.selectNka()
        self._writeDestTable( "nk_abrechnung", nkalist )

    def _copyHga( self ):
        hgalist = self._srcData.selectHga()
        # jetzt die vw_id in den einzelnen hga-Objekten umsetzen auf die neue vw_id
        vwglist = self._destData.selectTable( "verwaltung" )
        for hga in hgalist:
            for vwg in vwglist:
                if hga["mobj_id"] == vwg["mobj_id"] \
                and hga["vw_id"] == vwg["vw_id"]:
                    hga["vwg_id"] = vwg["vwg_id"]
                    break
        self._writeDestTable( "hg_abrechnung", hgalist )

    def _copyZahlungen( self ):
        # überträgt die Daten aus Tabelle zahlung in Tabelle einaus in mehreren Schritten
        self._copyMieten( True ) # --> done
        self._copyHgvZahlungen() # --> done
        self._copyHgaZahlungen() # --> done
        self._copyNkaZahlungen() # --> done
        self._copySonstAus()  # --> done
        # todo: Sammelabgaben splitten!

    def _copySonstAus( self, clearBefore=False ):
        zlist = self._srcData.selectSonstAusZahlungen()
        for z in zlist:
            if z["ea_art"] == "a":
                z["ea_art"] = EinAusArt.ALLGEMEINE_KOSTEN.dbvalue
            elif z["ea_art"] == "g":
                z["ea_art"] = EinAusArt.GRUNDSTEUER.dbvalue
            elif z["ea_art"] == "s":
                z["ea_art"] = EinAusArt.SONSTIGE_KOSTEN.dbvalue
            elif z["ea_art"] == "r":
                z["ea_art"] = EinAusArt.REPARATUR.dbvalue
            elif z["ea_art"] == "v":
                z["ea_art"] = EinAusArt.VERSICHERUNG.dbvalue
            butext = z["zbuchungstext"] # !Z!
            if butext is None:
                butext = ""
            if len( butext ) > 0:
                if z["buchungstext"]:
                    if not butext == z["buchungstext"]:
                        butext += ( "\n" + z["buchungstext"] )
            if z["rgtext"]:
                butext += ( "\n" + z["rgtext"] )
            z["buchungstext"] = butext
            if z["umlegbar"] == 1:
                z["umlegbar"] = Umlegbar.JA.value
            else:
                z["umlegbar"] = Umlegbar.NEIN.value
        self._writeDestTable( "einaus", zlist, clearBefore )

    def _copyNkaZahlungen( self, clearBefore=False ):
        dictlist = self._srcData.selectNkaZahlungen()
        nkalist = self._destData.selectNkaKerndaten()
        for dic in dictlist:
            for nka in nkalist:
                if dic["debi_kredi"] == nka["mv_id"] \
                and dic["ab_jahr"] == nka["ab_jahr"]:
                    dic["nka_id"] = nka["nka_id"]
                    dic["leistung"] = "NKA " + str(dic["ab_jahr"])
        self._writeDestTable( "einaus", dictlist, clearBefore )

    def _copyHgaZahlungen( self,  clearBefore=False ):
        dictlist = self._srcData.selectHgaZahlungen()
        # die gelieferten Sätze haben alle die alte hga_id an Bord, die muss ausgetauscht werde
        hgalist = self._destData.selectHgaKerndaten()
        for dic in dictlist:
            for hga in hgalist:
                if dic["mobj_id"] == hga["mobj_id"] \
                and dic["debi_kredi"] == hga["weg_name"] \
                and dic["ab_jahr"] == hga["ab_jahr"]:
                    dic["hga_id"] = hga["hga_id"]
                    dic["leistung"] = "HGA " + str(dic["ab_jahr"])
                    break
        self._writeDestTable( "einaus", dictlist, clearBefore )

    def _copyHgvZahlungen( self, clearBefore=False ):
        dictlist = self._srcData.selectHgvZahlungen()
        self._writeDestTable( "einaus", dictlist, clearBefore )

    def _copyMieten( self, clearBefore=False ):
        dictlist = self._srcData.selectMieten()
        self._writeDestTable( "einaus", dictlist , clearBefore )

    def _copyVerwaltung( self ):
        dictlist = self._srcData.selectVerwaltung()
        self._writeDestTable( "verwaltung", dictlist )

    def _copyVerwalter( self ):
        table = "verwalter"
        dictlist = self._srcData.selectTable( table )
        self._writeDestTable( table, dictlist )

    def _copyMietverhaeltnisse( self ):
        table = "mietverhaeltnis"
        dictlist = self._srcData.selectTable( table )
        self._writeDestTable( table, dictlist )

    def _copyMietobjekt( self ):
        table = "mietobjekt"
        dictlist = self._srcData.selectMietobjekte()
        self._writeDestTable( table, dictlist )

    def _copyMaster( self ):
        table = "masterobjekt"
        dictlist = self._srcData.selectTable( table, "where master_name not like '%*'" )
        self._writeDestTable( table, dictlist )

    def _writeDestTable( self, table:str, srcContent:List[Dict], clearTableBeforeWrite=True ):
        if clearTableBeforeWrite:
            self._destData.clearTable( table )
        destcols = self._destData.getColumnNames( table )
        for dic in srcContent:
            # for k, v in dic.items():
                # print( "key: ", k, " - value: ", v,
                #        " - is None: ", v is None,
                #        " - isNumeric: ", isinstance( v, numbers.Number ) )
            insert_stmt = self._destData.createInsertStatement( table, destcols, dic )
            # insert:
            try:
                lastrowid = self._destData.insert( insert_stmt )
            except Exception as ex:
                box = ErrorBox( "Insert-Fehler", str( ex ), "" )
                box.exec_()
                return


def runUebernahme():
    app = QApplication()
    print( ROOT_DIR )
    pathFile = DATENUEBERNAHME_DIR + "/datenuebernahmeTEST.path"
    f = open( pathFile, "r" )
    paths = f.read()
    paths = paths.split( "\n" )
    print( paths )
    srcpath = paths[0].split( "=" )[1] + "immo.db"
    print( "SourcePath = ", srcpath )
    destpath = paths[1].split( "=" )[1] + "immo.db"
    print( "DestPath = ", destpath )
    more = "Quelle: %s\n\nZiel: %s\n" % (srcpath, destpath)
    box = WarningBox( "Datenübernahme", "\nBei Drücken von OK startet die Datenübernahme!\n\n", more, "OK", "KREIIISCH NEIN" )
    if box.exec_() != MessageBox.Yes:
        return
    due = DatenUebernahmeLogic( srcpath, destpath )
    due.run()
    box = InfoBox( "Datenübernahme", "Die Datenübernahme ist beendet.", "", "OK" )
    box.exec_()

def test():
    runUebernahme()