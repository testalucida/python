from typing import List

from v2.abrechnungen.abrechnungdata import NKAbrechnungData, HGAbrechnungData
from v2.einaus.einauslogic import EinAusLogic
from v2.icc.constants import EinAusArt
from v2.icc.icclogic import IccLogic, IccTableModel
from v2.icc.interfaces import XAbrechnung, XHGAbrechnung, XNKAbrechnung, XVerwaltung, XEinAus

################   AbrechnungTableModel   ####################
from verwaltung.verwaltungdata import VerwaltungData


class AbrechnungTableModel( IccTableModel ):
    def __init__( self, rowlist:List[XAbrechnung], jahr ):
        IccTableModel.__init__( self, rowlist, jahr )

################   HGAbrechnungTableModel   ####################
class HGAbrechnungTableModel( AbrechnungTableModel ):
    def __init__(self, rowlist:List[XHGAbrechnung], jahr ):
        AbrechnungTableModel.__init__( self, rowlist, jahr )
        self.setKeyHeaderMappings2(
            ("master_name", "weg_name", "vw_id", "vwg_von", "vwg_bis", "ab_datum", "forderung", "entnahme_rue",
             "bemerkung", "zahlung", "buchungsdatum", "write_time"),
            ( "Objekt", "WEG", "Verwalter", "Vwtg. von", "Vwtg. bis", "abgerechnet am", "Forderung", "Entn.Rü.",
              "Bemerkung", "Zahlung", "gebucht am", "LWA" )
        )

################   NKAbrechnungTableModel   ####################
class NKAbrechnungTableModel( AbrechnungTableModel ):
    def __init__(self, rowlist:List[XNKAbrechnung], jahr ):
        AbrechnungTableModel.__init__( self, rowlist, jahr )
        self.setKeyHeaderMappings2(
            ("master_name", "weg_name", "vw_id", "ab_datum", "forderung", "entnahme_rue", "buchungsdatum",
             "bemerkung", "write_time"),
            ( "Objekt", "WEG", "Verwalter", "Abr.Dt.", "Forderung", "Entn.Rü.", "gebucht am", "Bemerkung", "LWA" )
        )

################   Base class AbrechnungLogic   ##################
class AbrechnungLogic( IccLogic ):
    def __init__(self):
        IccLogic.__init__( self )

    @staticmethod
    def getAbrechnungTableModel( self, jahr:int ) -> AbrechnungTableModel:
        pass

#################   HGAbrechnungTableModel   ######################
class HGAbrechnungLogic( AbrechnungLogic ):
    def __init__(self):
        AbrechnungLogic.__init__( self )
        self._data = HGAbrechnungData()

    def getAbrechnungTableModel( self, ab_jahr:int ) -> HGAbrechnungTableModel:
        abrlist:List[XAbrechnung] = self._data.getObjekteUndAbrechnungen( ab_jahr )
        tm = HGAbrechnungTableModel( abrlist, ab_jahr )
        return tm

#################   NKAbrechnungTableModel   ######################
class NKAbrechnungLogic( AbrechnungLogic ):
    def __init__(self):
        AbrechnungLogic.__init__( self )
        self._data = NKAbrechnungData()

    def getAbrechnungTableModel( self, jahr:int ) -> NKAbrechnungTableModel:
        pass