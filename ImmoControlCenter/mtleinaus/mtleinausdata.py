from constants import einausart
from icc.iccdata import IccData
from dbaccess import mon_dbnames
from interfaces import XMtlEinAus


class MtlEinAusData( IccData ):
    def __init__( self ):
        IccData.__init__( self )

    def existsEinAusArt( self, eaart: einausart, jahr: int ) -> bool:
        id_ = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "select count(*) as anz from mtleinaus where jahr = %d and %s is not null" % (jahr, id_ )
        d = self.readOneGetDict( sql )
        return d["anz"] > 0

    def getJahrFromMtlEinAus( self, meinaus_id: int ) -> int:
        sql = "select jahr from mtleinaus where meinaus_id = " + str( meinaus_id )
        l = self.read( sql )
        if len( l ) > 0:
            return l[0][0]
        else:
            raise Exception( "MtlEinAusData.getJahrFromMtlEinAus():\nKeinen Satz für meinaus_id '%d' gefunden." % meinaus_id )

    def getMtlEinAus( self, meinaus_id:int ) -> XMtlEinAus:
        sql = "select meinaus_id, mv_id, vwg_id, jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez " \
              "from mtleinaus where meinaus_id = " + str( meinaus_id )
        d = self.readOneGetDict( sql )
        if d: # wir haben ein Ergebnis
            x = XMtlEinAus( d )
            return x
        else:
            raise Exception( "MtlEinAusData.getMtlEinAus():\nKeinen Satz für mtleinaus_id '%d' gefunden." % meinaus_id )

    def insertMtlEinAus( self, mv_or_vwg_id: str, eaart: einausart, jahr: int ) -> int:
        """
        legt einen Satz in der Tabelle mtleinaus an, wobei alle Monatswerte auf 0 gesetzt werden
        :param mv_or_vwg_id: je nach einausart ist das die mv_id oder die vwg_id
        :param eaart: "miete" oder "hgv"
        :param jahr:
        :param commit:
        :return:
        """
        id_ = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "insert into mtleinaus (%s, jahr) values ('%s', %d) " % (id_, mv_or_vwg_id, jahr)
        return self.write( sql )

    def updateMtlEinAus( self, meinaus_id: int, monat: int or str, value: float ) -> int:
        """
        Ändert einen Monatswert in der Tabelle mtleinaus
        :param meinaus_id: identifz. den mtleinaus-Satz, damit auch das Jahr, egal ob Miete oder HGV
        :param monat: identifiziert den Monat: 1 -> Januar, ..., 12 -> Dezember oder als string "jan",..."dez"
        :param value: der Wert, der im betreffenden Monat eingetragen werden soll
        :return:
        """
        dbval = "%.2f" % value if value != 0 else "NULL"  # value ist bei Mieten > 0, bei HGV < 0
        sMonat = mon_dbnames[monat - 1] if isinstance( monat, int ) else monat
        sql = "update mtleinaus set '%s' = %s where meinaus_id = %d  " % (sMonat, dbval, meinaus_id)
        return self.write( sql )

def test():
    data = MtlEinAusData()
    #x:XMtlEinAus = data.getMtlEinAus( 500 )
    #print( x )

    # rc = data.existsEinAusArt( einausart.MIETE, 2022 )
    # print( rc )

    j = data.getJahrFromMtlEinAus( 467 )
    print( j )