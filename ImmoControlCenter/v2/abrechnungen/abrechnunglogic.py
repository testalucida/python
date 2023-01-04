import copy
from typing import List

import datehelper
from v2.abrechnungen.abrechnungdata import NKAbrechnungData, HGAbrechnungData
from v2.einaus.einausdata import EinAusData
from v2.einaus.einauslogic import EinAusLogic
from v2.icc import constants
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

################   TeilzahlungTableModel   ####################
class TeilzahlungTableModel( IccTableModel ):
    def __init__( self, rowlist:List[XTeilzahlung], jahr ):
        IccTableModel.__init__( self, rowlist, jahr )
        self.setKeyHeaderMappings2(
            ("ea_id", "betrag", "buchungsdatum", "buchungstext", "write_time" ),
            ("ea_id", "Betrag", "Buchungsdatum", "Buchungstext", "LWA" )
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
        self._hgaData = HGAbrechnungData()
        self._eaData = EinAusData()

    def getAbrechnungTableModel( self, ab_jahr:int ) -> HGAbrechnungTableModel:
        # Objekte mit Abrechnungen (soweit vorhanden) holen, ohne hga-Zahlungen
        abrlist:List[XHGAbrechnung] = self._hgaData.getObjekteUndAbrechnungen( ab_jahr ) # abrlist ist sortiert nach master_name
        # Achtung, die hga_id existiert für ein Objekt erst dann, wenn die Abrechnung gemacht wurde
        # Jetzt die Zahlungen zu den bereits erstellten Abrechnungen holen:
        for abr in abrlist:
            if abr.hga_id:
                ealist:List[XEinAus] = self._eaData.getEinAuszahlungenByHgaId( abr.hga_id )
                for ea in ealist:
                    abr.addZahlung( ea.betrag, ea.buchungsdatum, ea.buchungstext, ea.write_time, ea.ea_id )
        tm = HGAbrechnungTableModel( abrlist, ab_jahr )
        return tm

    def getTeilzahlungTableModel( self, xhga:XHGAbrechnung ) -> TeilzahlungTableModel:
        tm = TeilzahlungTableModel( xhga.teilzahlungen, xhga.ab_jahr )
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
        # Entscheiden, was genau zu tun ist: Ganze Abrechnung neu anlegen, Update auf exist. Abrechnung, Anlage/Änderung
        # einer Teilzahlung
        if xhga.hga_id > 0:
            # prüfen, ob eine Teilzahlung zu löschen ist. Dafür braucht es keine Validierung.
            msg = self._checkDeleteTeilzahlungen( xhga.hga_id, xhga.teilzahlungen )
            if msg: return msg
            # das etwaige Löschen von Teilzahlungen ist erledigt, für alles andere brauchen wir eine Validierung:
            msg = self.validateAbrechnung( xhga )
            if msg: return msg
            msg = self._updateAbrechnung( xhga )
            if msg: return msg
        else:
            # neue Abrechnung
            msg = self.validateAbrechnung( xhga )
            if msg: return msg
            msg = self._insertAbrechnung( xhga )
            if msg: return msg
        # die Abrechnung selbst ist erledigt - jetzt prüfen, ob es neue oder zu ändernde Teilzahlungen gibt:
        msg = self._checkSaveTeilzahlungen( xhga )
        if msg: return msg
        # alles gut gegangen, jetzt commit.
        # Eigtl ist es völlig egal, ob man den commit mit _eaData oder _hgaData macht. Alles läuft
        # in *einer* Transaktion. Sicherheitshalber machen wir zwei commits ;-)
        self._eaData.commit()
        self._hgaData.commit()
        return ""

    def _insertAbrechnung( self, xhga:XHGAbrechnung ) -> str:
        try:
            self._hgaData.insertAbrechnung( xhga )
            return ""
        except Exception as ex:
            self._hgaData.rollback()
            msg = "AbrechnungLogic._insertAbrechnung():\nFehler beim Insert der Abrechnung %d für " \
                  "Masterobjekt '%s'\n\nFehlermeldung:\n%s " % (xhga.ab_jahr, xhga.master_name, str( ex ))
            return msg

    def _updateAbrechnung( self, xhga:XHGAbrechnung ) -> str:
        try:
            self._hgaData.updateAbrechnung( xhga )
            return ""
        except Exception as ex:
            self._hgaData.rollback()
            msg = "AbrechnungLogic._updateAbrechnung():\nFehler beim Update der Abrechnung %d für " \
                  "Masterobjekt '%s'\n\nFehlermeldung:\n%s " % (xhga.ab_jahr, xhga.master_name, str( ex ))
            return msg

    def _checkSaveTeilzahlungen( self, xhga:XHGAbrechnung ) -> str:
        for tz in xhga.teilzahlungen:
            if tz.ea_id > 0:
                # todo: update Teilzahlung
                pass
            else:
                # Neue Teilzahlung
                # Aus dem tz-Objekt ein EinAus-Objekt machen, dann an _eaData übergeben zum Insert
                xea = self._createXeinausFromTeilzahlung( xhga, tz )
                try:
                    self._eaData.insertEinAusZahlung( xea )
                except Exception as ex:
                    self._eaData.rollback()
                    msg = "AbrechnungLogic._checkSaveTeilzahlungen():\nFehler beim Insert einer Teilzahlung für " \
                          "Masterobjekt '%s'\n\nFehlermeldung:\n%s " % (xhga.master_name, str( ex ))
                    return msg
        return ""

    def _createXeinausFromTeilzahlung( self, xhga:XHGAbrechnung, tz:XTeilzahlung ) -> XEinAus:
        xea = XEinAus()
        xea.master_name = xhga.master_name
        xea.debi_kredi = xhga.weg_name
        xea.leistung = "HGA %d" % xhga.ab_jahr
        xea.hga_id = xhga.hga_id
        xea.jahr = self._getYearForTeilzahlung( tz )
        xea.monat = self._getMonthForTeilzahlung( tz )
        xea.betrag = tz.betrag
        xea.ea_art = EinAusArt.HAUSGELD_ABRECHNG.display
        xea.buchungsdatum = tz.buchungsdatum
        xea.buchungstext = tz.buchungstext
        xea.write_time = datehelper.getCurrentTimestampIso()
        return xea

    def _getYearForTeilzahlung( self, tz:XTeilzahlung ) -> int:
        if tz.buchungsdatum:
            return int( tz.buchungsdatum[0:4] )
        else:
            return datehelper.getCurrentYear()

    def _getMonthForTeilzahlung( self, tz:XTeilzahlung ) -> str:
        if tz.buchungsdatum:
            monthIdx = int(tz.buchungsdatum[5:7])
            return constants.iccMonthShortNames[monthIdx-1]
        else:
            dic = datehelper.getCurrentYearAndMonth()
            return constants.iccMonthShortNames[dic["month"] - 1]

    def _checkDeleteTeilzahlungen( self, hga_id:int, tzlist:List[XTeilzahlung] ) -> str:
        ealist = self._eaData.getEinAuszahlungenByHgaId( hga_id )
        tz_ea_id_list = [tz.ea_id for tz in tzlist]
        for ea in ealist:
            if not ea.ea_id in tz_ea_id_list:
                # es gibt in der Datenbank eine ea_id, die in der tz_ea_id_list nicht mehr enthalten ist,
                # also eine Teilzahlung, die vom User gelöscht wurde.
                # Diese muss aus der DB gelöscht werden.
                try:
                    self._eaData.deleteEinAusZahlung( ea.ea_id )
                except Exception as ex:
                    self._eaData.rollback()
                    msg = "AbrechnungLogic._checkDeleteTeilzahlungen():\nFehler beim Löschen der Zahlung " \
                          "mit ea_id '%d'\n\nFehlermeldung:\n%s " % (ea.ea_id, str(ex))
                    return msg
        return ""

    def validateAbrechnung( self, x:XHGAbrechnung ) -> str:
        """
        Validiert ein XAbrechnung-Objekt und liefert eine Fehlermeldung zurück, wenn ein Validierungsfehler vorliegt.
        Wenn alles ok ist, wird ein Leerstring zurückgegeben.
        Vor der Validierung wird - sofern es sich nicht um einen Insert handelt - die Abrechnung aus der
        Datenbank geladen, um zu prüfen, ob überhaupt Veränderungen vorliegen.
        Gibt es keine Veränderungen, wird ein Leerstring zurückgegeben.
        :param x: zu prüfende Abrechnung
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