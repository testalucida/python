from abc import abstractmethod
from typing import Dict, List, Any
from base.interfaces import XBase


#################  XDatum  ##############################
from v2.icc.constants import iccMonthIdxToShortName, iccMonthShortNames


class XDateParts:
    y:int = 0
    m:int = 0
    d:int = 0

#########################################################
class XEinAus( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.ea_id = 0
        self.master_name = ""
        self.mobj_id = ""
        self.debi_kredi = ""
        self.leistung = ""
        self.sab_id = 0
        self.jahr = 0
        self.monat = ""
        self.betrag = 0.0
        self.ea_art = ""
        self.verteilt_auf:int = 1
        self.umlegbar = ""
        self.buchungsdatum = ""
        self.buchungstext = ""
        self.mehrtext = ""
        self.write_time = ""
        if valuedict:
            self.setFromDict( valuedict )

    def getMonthIdx( self ) -> int:
        return iccMonthShortNames.index( self.monat )

#####################################################################
class XMtlZahlung( XBase ):
    """
    Ein XMtlZahlung-Objekt repräsentiert z.B. eine Zeile in der Tabelle der Mieteingänge
    """
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.mobj_id = ""
        self.soll = 0.0 # Soll-Betrag des eingestellten Monats. Ändert sich mit jeder Änderung des "Checkmonats".
        ## vonMonat und bisMonat beziehen sich auf das Jahr, für das dieses Objekt angelegt wird.
        ## Läuft ein MV z.B. von Januar bis Oktober, wird in vonMonat 'jan' und in bisMonat 'okt' eingetragen.
        ## Das dient dazu, dass in der Tabelle die Monate, in denen keine Zahlung erwartet werden kann,
        ## mit einem anderen Hintergrund dargestellt werden können als die anderen Monate.
        self.vonMonat = "" # aktiv ab Monat im betreff. Jahr
        self.bisMonat = "" # aktiv bis Monat im betreff. Jahr
        self.jan = 0.0
        self.feb = 0.0
        self.mrz = 0.0
        self.apr = 0.0
        self.mai = 0.0
        self.jun = 0.0
        self.jul = 0.0
        self.aug = 0.0
        self.sep = 0.0
        self.okt = 0.0
        self.nov = 0.0
        self.dez = 0.0
        self.summe = 0.0
        if valuedict:
            self.setFromDict( valuedict )

    def getMonthValue( self, m:int ) -> float:
        """
        :param m: index of month: 0 to 11
        :return: float
        """
        monthname = iccMonthIdxToShortName[m]
        return self.__dict__[monthname]

    def setMonthValue( self, m:int, value:float ):
        """
        :param m: index of month: 0 to 11
        :param value: float value to set
        :return: None
        """
        monthname = iccMonthIdxToShortName[m]
        self.__dict__[monthname] = value

    def computeSum( self ):
        self.summe = self.jan + self.feb + self.mrz + self.apr + self.mai + self.jun + \
                     self.jul + self.aug + self.sep + self.okt + self.nov + self.dez

###########################   XMtlMiete   ######################
class XMtlMiete( XMtlZahlung ):
    def __init__( self, valuedict:Dict=None ):
        XMtlZahlung.__init__( self, valuedict )
        self.mv_id = ""
        if valuedict:
            self.setFromDict( valuedict )

###########################   XMtlHausgeld   ######################
class XMtlHausgeld( XMtlZahlung ):
    def __init__( self, valuedict:Dict=None ):
        XMtlZahlung.__init__( self, valuedict )
        self.master_name = ""
        self.weg_name = "" # Name der Wohnungseigentümergemeinschaft / des Hauses
        if valuedict:
            self.setFromDict( valuedict )

###########################   XMtlAbschlag   ######################
class XMtlAbschlag( XMtlZahlung ):
    def __init__( self, valuedict:Dict=None ):
        XMtlZahlung.__init__( self, valuedict )
        self.sab_id = 0
        self.kreditor = "" # Name des Kreditors (des Lieferanten)
        self.vnr =  ""
        self.leistung = ""
        self.master_name = ""
        if valuedict:
            self.setFromDict( valuedict )

##################   XGrundbesitzabgabe   ####################
class XGrundbesitzabgabe( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )#
        self.id = 0
        self.master_name = ""
        self.grundsteuer:float = 0.0
        self.abwasser:float = 0.0
        self.strassenreinigung:float = 0.0
        self.summe:float = 0.0 # der Jahresgesamtbetrag
        self.betrag_vierteljhrl:float = 0.0 # dieser Betrag wird vierteljährlich eingezogen
        self.bemerkung:str = ""
        if valuedict:
            self.setFromDict( valuedict )

    def computeSum( self ):
        self.summe = self.grundsteuer + self.abwasser + self.strassenreinigung
        self.betrag_vierteljhrl = round( self.summe/4, 2 )

class XSammelabgabe( XBase ):
    def __init__( self ):
        XBase.__init__( self )
        self.grundbesitzabgabeList:List[XGrundbesitzabgabe] = list()
        self.betrag = 0.0 # der Betrag, der eff. von der Stadt NK eingezogen wurde für alle Objekte,
                          # die in in der GrundbesitzabgabeListe enthalten sind.

#####################  Mietverhältnis Kurz  ######################
class XMietverhaeltnisKurz( XBase ):
    def __init__( self, valuedict: Dict = None ):
        XBase.__init__( self )
        self.id = 0
        self.mv_id = ""
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        if valuedict:
            self.setFromDict( valuedict )

#####################  WEG  ######################
class XVerwaltung( XBase ):
    def __init__( self, valuedict: Dict = None ):
        XBase.__init__( self )
        self.vwg_id = 0
        self.master_name = ""
        self.mobj_id = ""
        self.weg_name = ""
        self.vw_id = ""
        self.von = ""
        self.bis = ""
        if valuedict:
            self.setFromDict( valuedict )

#######################################################################
class XHandwerkerKurz( XBase ):
    def __init__(self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.id = 0
        self.name = ""
        self.branche = ""
        self.adresse = ""
        if valuedict:
            self.setFromDict( valuedict )

#################  XSollMiete  ############################
class XSollMiete( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.sm_id = 0
        self.mv_id = ""
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        self.netto = 0.0
        self.nkv:float = 0.0
        self.brutto:float = 0.0 # Summe von netto + nkv
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

#################  XSollHausgeld  ############################
class XSollHausgeld( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.shg_id = 0
        self.vwg_id = 0
        self.weg_name = ""
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        self.netto = 0.0
        self.ruezufue = 0.0
        self.brutto = 0.0 # Summe von netto + nkv
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

#################  XSollAbschlag  ############################
class XSollAbschlag( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.sab_id = 0
        self.kreditor = "" # z.B. KEW, Gaswerk Illingen
        self.vnr = "" # Vertragsnummer des Kreditors
        self.leistung = "" # Gas, Strom, Wasser
        self.master_name = ""
        self.mobj_id = "" # nur erforderlich für eine Leerstehende Wohnung. Dann werden die Verträge auf mich abgeschlossen.
        self.von = ""
        self.bis = ""
        self.betrag = 0.0
        self.umlegbar = 0
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

class XMasterobjekt( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.master_id = 0
        self.master_name = ""
        self.lfdnr = 0
        self.strasse_hnr = ""
        self.plz = ""
        self.ort = ""
        self.gesamt_wfl = 0
        self.anz_whg = 0
        self.afa_wie_vj = "X"
        self.afa = 0
        self.afa_proz = 0.0
        self.hauswart = ""
        self.hauswart_telefon = ""
        self.hauswart_mailto = ""
        self.heizung = ""
        self.angeschafft_am = ""
        self.veraeussert_am = ""
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

class XMietobjekt( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.mobj_id = ""
        self.whg_bez = ""
        self.qm = 0
        self.container_nr = ""
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

class XLeistung( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.leistung = ""
        self.umlegbar = 0
        self.ea_art = ""
        if valuedict:
            self.setFromDict( valuedict )

class XKreditorLeistung( XLeistung ):
    def __init__( self, valuedict:Dict=None ):
        XLeistung.__init__( self )
        self.kredleist_id = 0
        self.master_name = ""
        self.mobj_id = ""
        self.kreditor = ""
        # self.leistung = ""
        # self.umlegbar = 0
        # self.ea_art = ""
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )



#####################################################################################################################

def test():
    d = {"id": 11, "name" : "kendel, martin", "branche" : "Klempner", "adresse" : "Birnenweg 2, Kleinsendelbach"}
    x = XHandwerkerKurz( d )
    x.print()