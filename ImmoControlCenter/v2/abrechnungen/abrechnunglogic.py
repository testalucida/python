import copy
from typing import List

from v2.abrechnungen.abrechnungdata import NKAbrechnungData, HGAbrechnungData
from v2.einaus.einausdata import EinAusData
from v2.einaus.einauslogic import EinAusLogic
from v2.icc.constants import EinAusArt
from v2.icc.icclogic import IccLogic, IccTableModel
from v2.icc.interfaces import XAbrechnung, XHGAbrechnung, XNKAbrechnung, XVerwaltung, XEinAus, XTeilzahlung

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
             "bemerkung", "zahlung" ),
            ( "Objekt", "WEG", "Verwalter", "Vwtg. von", "Vwtg. bis", "abgerechnet am", "Forderung", "Entn.Rü.",
              "Bemerkung", "Zahlung" )
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
        # Objekte mit Abrechnungen (soweit vorhanden) holen, ohne hga-Zahlungen
        abrlist:List[XHGAbrechnung] = self._data.getObjekteUndAbrechnungen( ab_jahr ) # abrlist ist sortiert nach master_name
        # Achtung, die hga_id existiert für ein Objekt erst dann, wenn die Abrechnung gemacht wurde
        # Jetzt die Zahlungen zu den bereits erstellten Abrechnungen holen:
        eadata = EinAusData()
        for abr in abrlist:
            if abr.hga_id:
                ealist:List[XEinAus] = eadata.getEinAuszahlungenByHgaId( abr.hga_id )
                for ea in ealist:
                    abr.addZahlung( ea.betrag, ea.buchungsdatum, ea.buchungstext, ea.write_time, ea.ea_id )
        tm = HGAbrechnungTableModel( abrlist, ab_jahr )
        return tm

    def trySave( self, xhga:XHGAbrechnung ) -> str:
        """
        An einem Abrechnungsobjekt können Abrechnungsdaten und Zahlungsdaten (x.teilzahlungen) geändert werden.
        Geänderte Abrechnungsdaten werden in Tabelle hg_abrechnung gespeichert, neue/geänderte/gelöschte Teilzahlungen
        in Tabelle einaus.
        Um zu erkennen, ob ein Teilzahlungsobjekt gelöscht werden soll, werden alle Teilzahlungen dieser
        Abrechnung aus <einaus> gelesen. Objekte, die in dieser Liste vorhanden sind, in x.teilzahlungen aber nicht,
        müssen gelöscht werden.
        Insert/Update:
        Vor dem Speichern wird validiert. Das Validierungsergebnis wird zurückgeliefert.
        Gab es keinen Validierungsfehler wird gespeichert und ein Leerstring zurückgegeben.
        Gibt es ein Teilzahlungsobjekt mit ea_id == 0, handelt es sich um eine neue, noch nicht gespeicherte
        Teilzahlung. Es erfolgt ein Insert in einaus.
        Ein Teilzahlungsobjekt mit ea_id > 0 ist bereits gespeichert. Das entsprechende XEinaus-Objekt wird aus
        einaus gelesen und mit dem Teilzahlungsobjekt verglichen. Gibt es Unterschiede, erfolgt ein Update.
        :param xhga: das XHGAbrechnung-Objekt, dessen Änderungen gespeichert werden sollen.
        :return:
        """
        # erst prüfen, ob eine Teilzahlung zu löschen ist. Dafür braucht es keine Validierung.
        msg = self._checkDeleteTeilzahlungen( xhga.hga_id, xhga.teilzahlungen )
        msg = self.validateAbrechnung( xhga )
        return "not yet implemented"

    def _checkDeleteTeilzahlungen( self, hga_id:int, tzlist:List[XTeilzahlung] ) -> str:
        eadata = EinAusData()
        ealist = eadata.getEinAuszahlungenByHgaId( hga_id )

        return "not yet implemented"

    def validateAbrechnung( self, x:XHGAbrechnung ) -> str:
        """
        Validiert ein XAbrechnung-Objekt und liefert eine Fehlermeldung zurück, wenn ein Validierungsfehler vorliegt.
        Wenn alles ok ist, wird ein Leerstring zurückgegeben.
        :param x:
        :return: Fehlermeldung oder Leerstring
        """
        if not x.master_name: return "Mastername fehlt"
        if not x.ab_jahr: return "Abrechnungsjahr fehlt"
        if not x.ab_datum: return "Erstellungsdatum der Abrechnung fehlt"
        if not x.forderung: return "Forderung aus Abrechnung fehlt"
        if len( x.teilzahlungen ) > 0:
            for tz in x.teilzahlungen:
                if not tz.betrag:
                    msg = "Teilzahlungsbetrag '0' unzulässig"
                    if tz.ea_id: return msg + "(ea_id: '%d')" % tz.ea_id
                    return msg
        return ""



#################   NKAbrechnungTableModel   ######################
class NKAbrechnungLogic( AbrechnungLogic ):
    def __init__(self):
        AbrechnungLogic.__init__( self )
        self._data = NKAbrechnungData()

    def getAbrechnungTableModel( self, jahr:int ) -> NKAbrechnungTableModel:
        pass