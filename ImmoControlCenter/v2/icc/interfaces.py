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
        self.jahr = 0
        self.monat = ""
        self.betrag = 0.0
        self.ea_art = ""
        self.verteilt_auf:int = None
        self.umlegbar:int = None
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
        self.mv_id = ""
        self.verwalter = ""
        self.weg = "" # Name der Wohnungseigentümergemeinschaft
        self.vonMonat = ""  # aktiv ab Monat im betreff. Jahr
        self.bisMonat = ""  # aktiv bis Monat im betreff. Jahr
        self.soll = 0.0 # hängt ab vom eingestellten Monat
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


#####################################################################################################################

def test():
    d = {"id": 11, "name" : "kendel, martin", "branche" : "Klempner", "adresse" : "Birnenweg 2, Kleinsendelbach"}
    x = XHandwerkerKurz( d )
    x.print()