import copy
from abc import abstractmethod
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
            ( "Wohnung", "WEG", "Verwalter", "Vwtg. von", "Vwtg. bis", "abgerechnet am", "Forderung", "Entn.Rü.",
              "Bemerkung", "Zahlung" )
        )

################   NKAbrechnungTableModel   ####################
class NKAbrechnungTableModel( AbrechnungTableModel ):
    def __init__(self, rowlist:List[XNKAbrechnung], jahr ):
        AbrechnungTableModel.__init__( self, rowlist, jahr )
        self.setKeyHeaderMappings2(
            ("master_name", "mobj_id", "mv_id", "von", "bis", "ab_datum", "forderung", "bemerkung", "zahlung"),
            ( "Haus", "Wohnung", "Mieter", "MV von", "MV bis", "Abr.Dt.", "Forderung", "Bemerkung", "Zahlung" )
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
        self._eaData = EinAusData()

    @staticmethod
    def _getYearForTeilzahlung( tz: XTeilzahlung ) -> int:
        if tz.buchungsdatum:
            return int( tz.buchungsdatum[0:4] )
        else:
            return datehelper.getCurrentYear()

    @staticmethod
    def _getMonthForTeilzahlung( tz: XTeilzahlung ) -> str:
        if tz.buchungsdatum:
            monthIdx = int( tz.buchungsdatum[5:7] )
            return constants.iccMonthShortNames[monthIdx - 1]
        else:
            dic = datehelper.getCurrentYearAndMonth()
            return constants.iccMonthShortNames[dic["month"] - 1]

    @staticmethod
    def getTeilzahlungTableModel( xabr: XAbrechnung ) -> TeilzahlungTableModel:
        tm = TeilzahlungTableModel( xabr.teilzahlungen, xabr.ab_jahr )
        return tm

    @staticmethod
    def validateAbrechnung( x:XAbrechnung ) -> str:
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

    def getAbrechnungTableModel( self, ab_jahr: int ) -> AbrechnungTableModel:
        # Objekte mit Abrechnungen (soweit vorhanden) holen, ohne Zahlungen
        data = self.getData()
        abrlist: List[XAbrechnung] = data.getObjekteUndAbrechnungen( ab_jahr )  # abrlist ist sortiert nach master_name
        # Achtung, die abr_id existiert für ein Objekt erst dann, wenn die Abrechnung gemacht wurde
        # Jetzt die Zahlungen zu den bereits erstellten Abrechnungen holen:
        for abr in abrlist:
            if abr.abr_id:
                ealist: List[XEinAus] = self.getEinAusZahlungen( abr.abr_id )
                for ea in ealist:
                    abr.addZahlung( ea.betrag, ea.buchungsdatum, ea.buchungstext, ea.write_time, ea.ea_id )
        #tm = AbrechnungTableModel( abrlist, ab_jahr )
        tmtype = self.getAbrechnungTableModelType()
        tm = tmtype( abrlist, ab_jahr )
        return tm

    def trySave( self, xabr:XAbrechnung ) -> str:
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
        :param xabr: das XAbrechnung-Objekt, dessen Änderungen gespeichert werden sollen.
        :return:
        """
        # Entscheiden, was genau zu tun ist: Ganze Abrechnung neu anlegen, Update auf exist. Abrechnung, Anlage/Änderung
        # einer Teilzahlung
        if xabr.abr_id > 0:
            # prüfen, ob eine Teilzahlung zu löschen ist. Dafür braucht es keine Validierung.
            msg = self._checkDeleteTeilzahlungen( xabr.abr_id, xabr.teilzahlungen )
            if msg: return msg
            # das etwaige Löschen von Teilzahlungen ist erledigt, für alles andere brauchen wir eine Validierung:
            msg = self.validateAbrechnung( xabr )
            if msg: return msg
            msg = self._updateAbrechnung( xabr )
            if msg: return msg
        else:
            # neue Abrechnung
            msg = self.validateAbrechnung( xabr )
            if msg: return msg
            msg = self._insertAbrechnung( xabr )
            if msg: return msg
        # die Abrechnung selbst ist erledigt - jetzt prüfen, ob es neue oder zu ändernde Teilzahlungen gibt:
        msg = self._checkSaveTeilzahlungen( xabr )
        if msg: return msg
        # alles gut gegangen, jetzt commit.
        # Eigtl ist es völlig egal, ob man den commit mit _eaData oder _hgaData macht. Alles läuft
        # in *einer* Transaktion. Sicherheitshalber machen wir zwei commits ;-)
        self._eaData.commit()
        #self._hgaData.commit()
        return ""

    def _checkSaveTeilzahlungen( self, xabr:XAbrechnung ) -> str:
        for tz in xabr.teilzahlungen:
            if tz.ea_id > 0:
                # update Teilzahlung
                xea = self._eaData.getEinAusZahlung( tz.ea_id )
                if tz.betrag != xea.betrag or \
                   tz.buchungsdatum != xea.buchungsdatum or tz.buchungstext != xea.buchungstext:
                    xea.betrag = tz.betrag
                    xea.buchungsdatum = tz.buchungsdatum
                    xea.buchungstext = tz.buchungstext
                    self._eaData.updateEinAusZahlung( xea )
            else:
                # Neue Teilzahlung
                # Aus dem tz-Objekt ein EinAus-Objekt machen, dann an _eaData übergeben zum Insert
                xea = self._createXeinausFromTeilzahlung( xabr, tz )
                try:
                    self._eaData.insertEinAusZahlung( xea )
                except Exception as ex:
                    self._eaData.rollback()
                    msg = "AbrechnungLogic._checkSaveTeilzahlungen():\nFehler beim Insert einer Teilzahlung für " \
                          "Masterobjekt '%s'\n\nFehlermeldung:\n%s " % (xabr.master_name, str( ex ))
                    return msg
        return ""

    def _checkDeleteTeilzahlungen( self, abr_id: int, tzlist: List[XTeilzahlung] ) -> str:
        ealist = self.getEinAusZahlungen( abr_id )
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
                          "mit ea_id '%d'\n\nFehlermeldung:\n%s " % (ea.ea_id, str( ex ))
                    return msg
        return ""

    def _createXeinausFromTeilzahlung( self, xabr:XAbrechnung, tz:XTeilzahlung ) -> XEinAus:
        xea = XEinAus()
        xea.master_name = xabr.master_name
        xea.debi_kredi = xabr.weg_name
        xea.leistung = self.getLeistungKuerzel() + (" %d" % xabr.ab_jahr)
        xea.hga_id = xabr.abr_id
        xea.jahr = self._getYearForTeilzahlung( tz )
        xea.monat = self._getMonthForTeilzahlung( tz )
        xea.betrag = tz.betrag
        xea.ea_art = self.getEinAusArt_display()
        xea.buchungsdatum = tz.buchungsdatum
        xea.buchungstext = tz.buchungstext
        xea.write_time = datehelper.getCurrentTimestampIso()
        return xea

    @abstractmethod
    def getAbrechnungTableModelType( self ) -> type:
        pass

    @abstractmethod
    def getLeistungKuerzel( self ) -> str:
        """
        Das Kürzel, das in die Tabelle <einaus> in die Spalte <leistung> eingetragen wird.
        :return:
        """
        pass

    @abstractmethod
    def getEinAusArt_display( self ):
        """
        Liefert die EinAusArt
        :return:
        """
        pass

    @abstractmethod
    def getData( self ) -> HGAbrechnungData:
        pass

    @abstractmethod
    def getEinAusZahlungen( self, abr_id:int ) -> List[XEinAus]:
        pass

    @abstractmethod
    def _updateAbrechnung( self, xabr:XAbrechnung ):
        pass

    @abstractmethod
    def _insertAbrechnung( self, xabr: XAbrechnung ):
        pass

    @abstractmethod
    def _commit( self ):
        pass

#################   HGAbrechnungTableModel   ######################
class HGAbrechnungLogic( AbrechnungLogic ):
    def __init__(self):
        AbrechnungLogic.__init__( self )
        self._hgaData = HGAbrechnungData()

    def getAbrechnungTableModelType( self ) -> type:
        return HGAbrechnungTableModel

    def getLeistungKuerzel( self ) -> str:
        """
        Das Kürzel, das in die Tabelle <einaus> in die Spalte <leistung> eingetragen wird.
        :return:
        """
        return "HGA"

    def getEinAusArt_display( self ):
        """
        Liefert die EinAusArt
        :return:
        """
        return EinAusArt.HAUSGELD_ABRECHNG.display

    def getData( self ) -> HGAbrechnungData:
        return self._hgaData

    def getEinAusZahlungen( self, abr_id ) -> List[XEinAus]:
        return  self._eaData.getEinAuszahlungenByHgaId( abr_id )

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

    def _commit( self ):
        self._hgaData.commit()



#################   NKAbrechnungTableModel   ######################
class NKAbrechnungLogic( AbrechnungLogic ):
    def __init__(self):
        AbrechnungLogic.__init__( self )
        self._nkaData = NKAbrechnungData()

    def getAbrechnungTableModelType( self ) -> type:
        return NKAbrechnungTableModel

    def getLeistungKuerzel( self ) -> str:
        """
        Das Kürzel, das in die Tabelle <einaus> in die Spalte <leistung> eingetragen wird.
        :return:
        """
        return "NKA"

    def getEinAusArt_display( self ):
        """
        Liefert die EinAusArt
        :return:
        """
        return EinAusArt.NEBENKOSTEN_ABRECHNG.display

    def getData( self ) -> NKAbrechnungData:
        return self._nkaData

    def getEinAusZahlungen( self, abr_id ) -> List[XEinAus]:
        return  self._eaData.getEinAuszahlungenByNkaId( abr_id )