from abc import abstractmethod
from typing import List

from v2.icc.iccdata import IccData, DbAction
from v2.icc.interfaces import XAbrechnung, XHGAbrechnung, XNKAbrechnung

##################   Base class AbrechnungData   ###################
class AbrechnungData( IccData ):
    def __init__( self ):
        IccData.__init__( self )

    @abstractmethod
    def getObjekteUndAbrechnungen( self, ab_jahr:int ) -> List[XAbrechnung]:
        """
        Liefert eine Liste aller aktiven Objekte mit Verwaltungs- und Abrechnungsdaten für das Jahr <ab_jahr>,
        soweit vorhanden. Die Liste enthält alle Objekte, egal, ob schon eine Abrechnung erstellt wurde oder nicht.
        :param ab_jahr:
        :return:
        """

###################   HGAbrechnungData   #########################
class HGAbrechnungData( AbrechnungData ):
    def __init__( self ):
        AbrechnungData.__init__( self )

    def insertAbrechnung( self, xhga:XHGAbrechnung ) -> int:
        vwg_id = "NULL" if not xhga.vwg_id else str(xhga.vwg_id)
        bemerkung = "NULL" if not xhga.bemerkung else ("'%s'" % xhga.bemerkung)
        sql = "insert into hg_abrechnung " \
              "(ab_jahr, vwg_id, forderung, entnahme_rue, ab_datum, bemerkung) " \
              "values " \
              "(   %d,     %s,      %.2f,      %.2f,         '%s',     %s )" % (xhga.ab_jahr, vwg_id,
                                                                                xhga.forderung, xhga.entnahme_rue,
                                                                                xhga.ab_datum, bemerkung)
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "hg_abrechnung", "hga_id", 0,
                                        newvalues=xhga.toString( printWithClassname=True ), oldvalues=None )
        xhga.hga_id = inserted_id
        return inserted_id

    def updateAbrechnung( self, xhga:XHGAbrechnung ) -> int:
        oldX = self.getAbrechnung( xhga.hga_id )
        bemerkung = "NULL" if not xhga.bemerkung else ("'%s'" % xhga.bemerkung)
        sql = "update hg_abrechnung " \
              "set ab_jahr = %d, " \
              "vwg_id = %d, " \
              "forderung = %.2f, " \
              "entnahme_rue = %.2f, " \
              "ab_datum = '%s', " \
              "bemerkung = %s " \
              "where hga_id = %d " % (xhga.ab_jahr, xhga.vwg_id, xhga.forderung, xhga.entnahme_rue, xhga.ab_datum,
                                      bemerkung, xhga.hga_id)
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "einaus", "ea_id", xhga.hga_id,
                                         newvalues=xhga.toString( True ), oldvalues=oldX.toString( True ) )
        return rowsAffected

    def getObjekteUndAbrechnungen( self, ab_jahr:int ) -> List[XHGAbrechnung]:
        sql = "select master.master_name, " \
              "vwg.vwg_id, coalesce(vwg.weg_name, '') as weg_name, coalesce(vwg.vw_id, '') as vw_id, " \
              "coalesce(vwg.von, '') as vwg_von, coalesce(vwg.bis, '') as vwg_bis, " \
              "coalesce(hga.hga_id, 0) as hga_id, coalesce(hga.ab_datum, '') as ab_datum, " \
              "coalesce(hga.forderung, 0) as forderung, coalesce(hga.entnahme_rue, 0) as entnahme_rue, " \
              "coalesce(hga.bemerkung, '') as bemerkung " \
                "from masterobjekt master " \
                "left outer join verwaltung vwg on vwg.master_name == master.master_name " \
                "left outer join hg_abrechnung hga on (hga.ab_jahr = %d and hga.vwg_id = vwg.vwg_id) " \
                "where master.aktiv > 0 " \
                "order by master.master_name, vwg.von " % ab_jahr
        return self.readAllGetObjectList( sql, XHGAbrechnung )

    def getAbrechnung( self, hga_id:int ) -> XHGAbrechnung:
        sql = "select hga_id, ab_jahr, vwg_id, forderung, entnahme_rue, ab_datum, bemerkung " \
              "from hg_abrechnung " \
              "where hga_id = %d " % hga_id
        x = self.readOneGetObject( sql, XHGAbrechnung )
        return x


###################   NKAbrechnungData   #########################
class NKAbrechnungData( AbrechnungData ):
    def __init__( self ):
        AbrechnungData.__init__( self )

    def getObjekteUndAbrechnungen( self, jahr:int ) -> List[XNKAbrechnung]:
        pass


def test():
    data = HGAbrechnungData()
    l = data.getObjekteUndAbrechnungen( 2021 )
    print( l )