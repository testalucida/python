from abc import abstractmethod
from typing import List

from v2.icc.iccdata import IccData
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

    def getObjekteUndAbrechnungen( self, ab_jahr:int ) -> List[XHGAbrechnung]:
        sql = "select master.master_name, vwg.vwg_id, vwg.weg_name, vwg.vw_id, " \
                "vwg.von as vwg_von, coalesce(vwg.bis, '') as vwg_bis, " \
                "hga.hga_id, hga.ab_datum, hga.forderung, coalesce(hga.entnahme_rue, '') as entnahme_rue, " \
                "hga.bemerkung, " \
                "ea.betrag as zahlung, ea.buchungsdatum, ea.write_time " \
                "from masterobjekt master " \
                "left outer join verwaltung vwg on vwg.master_name == master.master_name " \
                "left outer join hg_abrechnung hga on (hga.ab_jahr = %d and hga.vwg_id = vwg.vwg_id) " \
                "left outer join einaus ea on ea.hga_id = hga.hga_id " \
                "where master.aktiv > 0 " \
                "order by master.master_name, vwg.von " % ab_jahr
        return self.readAllGetObjectList( sql, XHGAbrechnung )


###################   NKAbrechnungData   #########################
class NKAbrechnungData( AbrechnungData ):
    def __init__( self ):
        AbrechnungData.__init__( self )

    def getObjekteUndAbrechnungen( self, jahr:int ) -> List[XNKAbrechnung]:
        pass


def test():
    data = HGAbrechnungData()
    l = data.getAbrechnungen( 2021 )
    print( l )