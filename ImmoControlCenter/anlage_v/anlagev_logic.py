from typing import List, Dict

from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from anlage_v.anlagev_interfaces import XObjektStammdaten, XAnlageV_Zeile, XZeilendefinition


class AnlageV_Logic:
    __instance = None

    def __init__(self):
        if AnlageV_Logic.__instance != None:
            raise Exception( "You can't instantiate AnlageV_Logic more than once." )
        else:
            AnlageV_Logic.__instance = self
        self._db: AnlageV_DataAccess
        self._steuerpflichtiger:Dict = dict() #keys: name, vorname, steuerpflichtiger
        self._objektStammdatenList:List[XObjektStammdaten] = list()
        self._anlageV_zeilendefinitionen:List[XZeilendefinition] = list()

    @staticmethod
    def inst() -> __instance:
        if AnlageV_Logic.__instance == None:
            AnlageV_Logic()
            AnlageV_Logic.inst()._prepare()
        return AnlageV_Logic.__instance

    def _prepare(self):
        dbname = "../immo.db"
        #dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"
        self._db = AnlageV_DataAccess( dbname )
        self._db.open()
        self._steuerpflichtiger = self._db.getSteuerpflichtige()[0]
        self._objektStammdatenList:List[XObjektStammdaten] = self._db.getObjektStammdaten()
        self._anlageV_zeilendefinitionen:List[XZeilendefinition] = self._db.getAnlageV_Zeilendefinitionen()

    def terminate(self):
        self._db.close()

    def _getZeilenDef( self, feld_id:str ) -> XZeilendefinition:
        """
        liefert zur feld_id (Bsp: "vorname" die Nummer der entsprechenden Zeile in der Anlage V
        :param feld_id:
        :return:
        """
        for defi in self._anlageV_zeilendefinitionen:
            if defi.feld_id == feld_id:
                return defi
        raise Exception( "AnlageV_Logic._getZeilenDef(): kann Feld_Id '%s' nicht finden." % (feld_id) )

    def _createAnlageV_Zeile( self, feld_id:str, val:str ) -> XAnlageV_Zeile:
        defi = self._getZeilenDef( feld_id )
        x = XAnlageV_Zeile()
        x.nr = defi.nr
        x.feld_id = feld_id
        x.text = val
        x.printX = defi.printX
        x.printY = defi.printY
        return x

    def _addFirstSteuerpflichtigen( self, anlagev_zeilen:List[XAnlageV_Zeile] ) -> None:
        """
        liefert den ersten Eintrag der Tabelle steuerpflichtiger.
        Das bin ich ;-)  Ich mach das nur, um meinen Namen u. meine Steuernummer nicht im Programm verdrahten zu müssen.
        Geliefert wird ein Dictionary mit den Keys name, vorname, steuernummer
        :return:
        """
        ld:List[Dict] = self._db.getSteuerpflichtige()
        d = ld[0] # das bin ich
        x = self._createAnlageV_Zeile( "name", d["name"] )
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "vorname", d["vorname"] )
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "steuernummer", d["steuernummer"] )
        anlagev_zeilen.append( x )

    def _getObjekt( self, master_name:str ) -> XObjektStammdaten:
        for o in self._objektStammdatenList:
            if o.master_name == master_name: return o
        raise Exception( "AnlageV_Logic._getObjekt(): "
                         "Objekt '%s' nicht in der Objektliste gefunden." % (master_name) )

    def _addObjekt( self, master_name:str, anlagev_zeilen:List[XAnlageV_Zeile] ) -> None:
        """
        fügt der Liste der AnlageV-Zeilen die 6 objektspezifischen Felder hinzu
        :param master_name: Identifikation des Mietobjekts
        :param anlagev_zeilen:
        :return:
        """
        o = self._getObjekt( master_name )
        x = self._createAnlageV_Zeile( "obj_str_hnr", o.strasse_hnr )
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "angeschafft_am", o.angeschafft_am )
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "obj_plz", o.plz )
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "obj_ort", o.ort )
        anlagev_zeilen.append( x )

    def getObjektStammdatenList( self ) -> List[XObjektStammdaten]:
        return self._objektStammdatenList

    def getObjektNamen( self ) -> List[str]:
        """
        Liefert alle master_name aus der Tabelle masterobjekt,
        sortiert nach Name aufsteigend OHNE Namen wie "**alle**"
        :return:
        """
        return self._db.getObjektNamen()

    def getAnlageV_Zeilen( self, master_name:str ) -> List[XAnlageV_Zeile]:
        """
        liefert alle Zeilen für die AnlageV des Objekts master_name (N_Stadtpark etc.)
        :param master_name:
        :return:
        """
        l:List[XAnlageV_Zeile] = list()
        self._addFirstSteuerpflichtigen( l )
        self._addObjekt( master_name, l )
        return l


def test():
    busi = AnlageV_Logic.inst()
    zeilenlist = busi.getAnlageV_Zeilen( "BUEB_Saargemuend" )
    # d = busi.getFirstSteuerpflichtigen()
    # print( d )
    # o = busi.getObjektStammdaten()
    # print( o )
    busi.terminate()

if __name__ == "__main__":
    test()