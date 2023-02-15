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

    @abstractmethod
    def getAbrechnung( self, hga_id:int ) -> XAbrechnung:
        pass

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
        xhga.abr_id = inserted_id
        return inserted_id

    def updateAbrechnung( self, xhga:XHGAbrechnung ) -> int:
        oldX = self.getAbrechnung( xhga.abr_id )
        if oldX.ab_jahr == xhga.ab_jahr \
        and oldX.vwg_id == xhga.vwg_id \
        and oldX.forderung == xhga.forderung \
        and oldX.entnahme_rue == xhga.entnahme_rue \
        and oldX.ab_datum == xhga.ab_datum \
        and oldX.bemerkung == xhga.bemerkung:
            bemerkung = "NULL" if not xhga.bemerkung else ("'%s'" % xhga.bemerkung)
            sql = "update hg_abrechnung " \
                  "set ab_jahr = %d, " \
                  "vwg_id = %d, " \
                  "forderung = %.2f, " \
                  "entnahme_rue = %.2f, " \
                  "ab_datum = '%s', " \
                  "bemerkung = %s " \
                  "where hga_id = %d " % (xhga.ab_jahr, xhga.vwg_id, xhga.forderung, xhga.entnahme_rue, xhga.ab_datum,
                                          bemerkung, xhga.abr_id)
            rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "hg_abrechnung", "hga_id", xhga.abr_id,
                                             newvalues=xhga.toString( True ), oldvalues=oldX.toString( True ) )
            return rowsAffected
        return 0

    def getObjekteUndAbrechnungen( self, ab_jahr:int ) -> List[XHGAbrechnung]:
        sql = "select master.master_name, " \
              "vwg.vwg_id, coalesce(vwg.weg_name, '') as weg_name, coalesce(vwg.mobj_id, '') as mobj_id, " \
              "coalesce(vwg.vw_id, '') as vw_id, " \
              "coalesce(vwg.von, '') as vwg_von, coalesce(vwg.bis, '') as vwg_bis, " \
              "coalesce(hga.hga_id, 0) as abr_id, coalesce(hga.ab_datum, '') as ab_datum, " \
              "coalesce(hga.forderung, 0) as forderung, coalesce(hga.entnahme_rue, 0) as entnahme_rue, " \
              "coalesce(hga.bemerkung, '') as bemerkung " \
                "from masterobjekt master " \
                "inner join verwaltung vwg on (vwg.master_name = master.master_name and hga_relevant = 1) " \
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

    def insertAbrechnung( self, xnka: XNKAbrechnung ) -> int:
        bemerkung = "NULL" if not xnka.bemerkung else ("'%s'" % xnka.bemerkung)
        sql = "insert into nk_abrechnung " \
              "(ab_jahr, mv_id, forderung, ab_datum, bemerkung) " \
              "values " \
              "(   %d,     '%s',  %.2f,      '%s',     %s )" % (xnka.ab_jahr, xnka.mv_id,
                                                                  xnka.forderung, xnka.ab_datum, bemerkung)
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "nk_abrechnung", "nka_id", 0,
                                        newvalues=xnka.toString( printWithClassname=True ), oldvalues=None )
        xnka.abr_id = inserted_id
        return inserted_id

    def updateAbrechnung( self, xnka:XNKAbrechnung ) -> int:
        oldX = self.getAbrechnung( xnka.abr_id )
        bemerkung = "NULL" if not xnka.bemerkung else ("'%s'" % xnka.bemerkung)
        sql = "update nk_abrechnung " \
              "set ab_jahr = %d, " \
              "mv_id = '%s', " \
              "forderung = %.2f, " \
              "ab_datum = '%s', " \
              "bemerkung = %s " \
              "where nka_id = %d " % (xnka.ab_jahr, xnka.mv_id, xnka.forderung, xnka.ab_datum,
                                      bemerkung, xnka.abr_id)
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "nk_abrechnung", "nka_id", xnka.abr_id,
                                         newvalues=xnka.toString( True ), oldvalues=oldX.toString( True ) )
        return rowsAffected


    def getObjekteUndAbrechnungen( self, ab_jahr:int ) -> List[XNKAbrechnung]:
        sql = "select master.master_name, " \
              "mo.mobj_id, mv.mv_id, mv.von, coalesce(mv.bis, '') as bis, " \
              "coalesce(nka.nka_id, 0) as abr_id, coalesce(nka.ab_datum, '') as ab_datum, " \
              "coalesce(nka.forderung, 0) as forderung, " \
              "coalesce(nka.bemerkung, '') as bemerkung " \
              "from masterobjekt master " \
              "inner join mietobjekt mo on mo.master_name = master.master_name " \
              "inner join mietverhaeltnis mv on (mv.mobj_id = mo.mobj_id and nka_relevant = 1) " \
              "left outer join nk_abrechnung nka on (nka.ab_jahr = %d and nka.mv_id = mv.mv_id) " \
              "where master.aktiv > 0 " \
              "order by master.master_name, mv.von desc " % ab_jahr
        return self.readAllGetObjectList( sql, XNKAbrechnung )

    def getAbrechnung( self, nka_id: int ) -> XNKAbrechnung:
        sql = "select nka_id, ab_jahr, mv_id, forderung, ab_datum, bemerkung " \
              "from nk_abrechnung " \
              "where nka_id = %d " % nka_id
        x = self.readOneGetObject( sql, XNKAbrechnung )
        return x


def test():
    data = NKAbrechnungData()
    l = data.getObjekteUndAbrechnungen( 2021 )
    print( l )