from enum import Enum, IntEnum, auto
from typing import List
from numpy import sort

iccMonthShortNames = ("jan", "feb", "mrz", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez")
iccMonthIdxToShortName = {
    0 : iccMonthShortNames[0],
    1 : iccMonthShortNames[1],
    2 : iccMonthShortNames[2],
    3 : iccMonthShortNames[3],
    4 : iccMonthShortNames[4],
    5 : iccMonthShortNames[5],
    6 : iccMonthShortNames[6],
    7 : iccMonthShortNames[7],
    8 : iccMonthShortNames[8],
    9 : iccMonthShortNames[9],
    10 : iccMonthShortNames[10],
    11 : iccMonthShortNames[11]
}
# monthNameToIdx = {
#     monthnames[0],
#     monthnames[1],
#     monthnames[2],
#     monthnames[3],
#     monthnames[4],
#     monthnames[5],
#     monthnames[6],
#     monthnames[7],
#     monthnames[8],
#     monthnames[9],
#     monthnames[10],
#     monthnames[11]
# }

class Action( IntEnum ):
    SHOW_MASTEROBJEKT = auto()
    SHOW_MIETOBJEKT = auto()
    SHOW_MIETVERHAELTNIS = auto()
    SHOW_NETTOMIETE_UND_NKV = auto()
    SHOW_NEBENKOSTEN_ABRECHNUNG = auto()
    SHOW_WEG_UND_VERWALTER = auto()
    SHOW_HAUSGELD_UND_RUEZUFUE = auto()
    SHOW_HAUSGELD_ABRECHNUNG = auto()
    SHOW_LEISTUNGSVERTRAG = auto()
    DUPLICATE_AND_SAVE = auto()
    DUPLICATE_AND_EDIT = auto()
    COMPUTE_SUMME = auto()
    COPY = auto() # Kopiere ganze Selektion
    COPY_CELL = auto() # Kopiere nur den Wert der geklickten Zelle

class ValueMapper:
    def __init__( self, display, dbvalue ):
        self.display = display
        self.dbvalue = dbvalue


class Modus:
    NEW = "new"
    MODIFY = "mod"
    UNK = "unk"

class Umlegbar( Enum ):
    NEIN = "nein"
    JA = "ja"
    NONE = ""

class EinAusArt: # EinAus-Arten, wie sie in die Tabelle einaus eingetragen werden.
    BRUTTOMIETE = ValueMapper( "Bruttomiete", "brm" )
    NEBENKOSTEN_VORAUS = ValueMapper( "Nebenkostenvorauszahlung", "nkv" )
    HAUSGELD_VORAUS = ValueMapper( "Hausgeldvorauszahlung", "hgv" )
    MTL_ABSCHLAG = ValueMapper( "Mtl. Abschlag", "mab" )
    NEBENKOSTEN_ABRECHNG = ValueMapper( "Nebenkostenabrechnung", "nkv" )
    HAUSGELD_ABRECHNG = ValueMapper( "Hausgeldabrechnung", "hga" )
    SONDERUMLAGE = ValueMapper( "Sonderumlage", "sonder" )
    ALLGEMEINE_KOSTEN = ValueMapper( "Allgemeine Hauskosten", "allg" )
    GRUNDSTEUER = ValueMapper( "Grundsteuer", "gs" )
    KOMMUNALE_DIENSTE = ValueMapper( "Kommunale Dienste", "komm" )  # Abschläge und Abrechnungen für Strom, Gas etc.
    REPARATUR = ValueMapper( "Reparatur", "rep" )
    DIENSTREISE = ValueMapper( "Dienstreise", "reise" )
    SONSTIGE_KOSTEN = ValueMapper( "Sonstige Kosten", "sonst" )
    VERSICHERUNG = ValueMapper( "Versicherung", "vers" )

    @staticmethod
    def getDisplayValues( issorted:bool = True ) -> List[str]:
        l = list()
        for attr in EinAusArt.__dict__.values():
            if isinstance( attr, ValueMapper ):
                l.append( attr.display )
        if issorted:
            l = list( sort( l ) )
        return l

    @staticmethod
    def getDbValue( display:str ) -> str:
        for attr in EinAusArt.__dict__.values():
            if isinstance( attr, ValueMapper ):
                if attr.display == display:
                    return attr.dbvalue
        raise Exception( "EinAusArt.getDbValue():\nDisplay value '%s' nicht gefunden." % display )

    @staticmethod
    def getDisplay( dbvalue:str ) -> str:
        for attr in EinAusArt.__dict__.values():
            if isinstance( attr, ValueMapper ):
                if attr.dbvalue == dbvalue:
                    return attr.display
        raise Exception( "EinAusArt.getDisplay():\nDB-Value '%s' nicht gefunden." % dbvalue )



def testEinAusArtNeu():
    print( EinAusArt.BRUTTOMIETE.display )
    l = EinAusArt.getDisplayValues()
    print( l )
    dbv = EinAusArt.getDbValue( EinAusArt.REPARATUR.display )
    print( dbv )

# class EinAusArt( Enum ): # EinAus-Arten, wie sie in die Tabelle einaus eingetragen werden.
#     """
#     Erläuterung:
#     Jeder Aufzählungspunkt ist ein MEMBER namens EinAusArt.BRUTTOMIETE etc.
#     Jedes Member hat einen NAMEN wie z.B. BRUTTOMIETE (das führende EinAusArt. fehlt)
#     Jedes Member hat einen VALUE wie z.B. "brm"
#     Die Members kann man auflisten mit [m for m in EinAusArt]
#     """
#     BRUTTOMIETE = "brm"
#     NEBENKOSTEN_VORAUS = "nkv"
#     HAUSGELD_VORAUS = "hgv"
#     MTL_ABSCHLAG = "mab"
#     NEBENKOSTEN_ABRECHNG = "nka"
#     HAUSGELD_ABRECHNG = "hga"
#     SONDERUMLAGE = "sonder"
#     ALLGEMEINE_KOSTEN = "a"
#     GRUNDSTEUER = "g"
#     KOMMUNALE_DIENSTE = "k"  # Abschläge und Abrechnungen für Strom, Gas etc.
#     REPARATUR = "r"
#     DIENSTREISE = "d"
#     SONSTIGE_KOSTEN = "s"
#     VERSICHERUNG = "v"
#
#     @staticmethod
#     def getMemberNames( sorted:bool=True) -> List[str]:
#         """
#         Liefert eine Liste von Member-Namen, auf Wunsch sortiert nach Alphabet
#         :param sorted: wenn True, werden die Liste nach Namen sortiert
#         :return: ["BRUTTOMIETE", "NEBENKOSTEN_VORAUS", ...]
#         """
#         l = [m.name for m in EinAusArt]
#         if sorted:
#             l = list( sort( l ) )
#         return l
#
#     @staticmethod
#     def getMembers() -> List:
#         """
#         Liefert eine Liste von EinAusArt-Members
#         :return: [<EinAusArt.BRUTTOMIETE: 'brm'>, <EinAusArt.NEBENKOSTEN_VORAUS: 'nkv'>,
#                   <EinAusArt.HAUSGELD_VORAUS: 'hgv'>, <EinAusArt.MTL_ABSCHLAG: 'mab'>, ...]
#         """
#         return [m for m in EinAusArt]
#
#     @staticmethod
#     def getMemberNameByValue( value:str ) -> str:
#         """
#         :param value: z.B. "brm"
#         :return: zugehörigen Namen, im Beispiel BRUTTOMIETE
#         """
#         m = EinAusArt( value ).name
#         return m
#
#     @staticmethod
#     def getMemberByValue( value: str ) -> str:
#         """
#         :param value: z.B. "brm"
#         :return: zugehörigen Namen, im Beispiel EinAusArt.BRUTTOMIETE
#         """
#         m = EinAusArt( value )
#         return m
#
#     @staticmethod
#     def getValueByMemberName( name ) -> str:
#         """
#         :param name: z.B. "BRUTTOMIETE"
#         :return: zugehörigen value, im Beispiel "brm"
#         """
#         member = EinAusArt.__getattr__( name )
#         v = member.value
#         return v
#
#     @staticmethod
#     def getValueByMember( member ) -> str:
#         """
#         :param member: z.B. EinAusArt.BRUTTOMIETE (nicht als string!)
#         :return: zugehörigen value, im Beispiel "brm"
#         """
#         v = member.value
#         return v
#
# def test5():
#     m = EinAusArt.getMemberByValue( "brm" )
#     print( m )
#     n = EinAusArt.getMemberNameByValue( "brm" )
#     print( n )
#
# def test4():
#     l = EinAusArt.getMembers()
#     print( l )
#
# def test3():
#     v = EinAusArt.getValueByMemberName( "BRUTTOMIETE")
#     print( v )
#     v2 = EinAusArt.getValueByMember( EinAusArt.BRUTTOMIETE )
#     print( v2 )
#
# def test2():
#     print( EinAusArt.getMemberNames() ) # -> ['ALLGEMEINE_KOSTEN', 'BRUTTOMIETE', ...]
#     members = EinAusArt.__members__
#     print( members )
#     members2 = [m for m in EinAusArt]
#     for m in members2:
#         print( m ) # -> z.B. EinAusArt.BRUTTOMIETE
#         print( m.name ) # -> z.B. BRUTTOMIETE
#     print( members2 )
#     print( EinAusArt.__members__ ) # -> {'BRUTTOMIETE': <EinAusArt.BRUTTOMIETE: 'brm'>, 'NEBENKOSTEN_VORAUS': <EinAusArt.NEBENKOSTEN_VORAUS: 'nkv'>,}
#     print( EinAusArt.__getattribute__( EinAusArt, "BRUTTOMIETE" ) )
#     ea_art = EinAusArt( "brm" ) # -> y: EinAusArt.BRUTTOMIETE
#     print( ea_art ) # -> EinAusArt.BRUTTOMIETE
#     print( str(ea_art)) # -> EinAusArt.BRUTTOMIETE
#     name = EinAusArt( "brm" ).name # -> BRUTTOMIETE
#     print( name )

class abrechnung( Enum ):
    NK = 0
    HG = 1

class tableAction( IntEnum ):
    INSERT = 0
    UPDATE = 1
    DELETE = 2

actionList = ( "INSERT", "UPDATE", "DELETE" )

class SollType( IntEnum ):
    MIETE_SOLL = 0
    HAUSGELD_SOLL = 1

class DetailLink( Enum ):
    ERHALTUNGSKOSTEN = "REP",
    ZU_VERTEIL_GESAMTKOSTEN_VJ = "VJ_GES", # Zu verteilende Aufwände, die im Veranlag.jahr entstanden sind
    ERHALTUNGSKOSTEN_VERTEILT = "VREP",   # Teilbeträge der im Veranlagg.jahr zu berücksichtigenden Aufwände, die im VJ
                                         # oder in den zurückliegenden 4 Jahren entstanden und zu verteilen sind.
    MIETEN = "ME",
    HAUSGELD = "HG",
    ALLGEMEINE_KOSTEN = "AK",
    SONSTIGE_KOSTEN = "SK"