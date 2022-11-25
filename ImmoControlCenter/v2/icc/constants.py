from enum import Enum, IntEnum, auto

# Monatsnamen, die den Spaltennamen in Tabelle <mtleinaus> entsprechen und in die Spalte zahlung.monat
# eingetragen werden:
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

class EinAusArt( Enum ): # EinAus-Arten, wie sie in die Tabelle einaus eingetragen werden.
    BRUTTOMIETE = "brm"
    NEBENKOSTEN_VORAUS = "nkv"
    HAUSGELD_VORAUS = "hgv"
    MTL_ABSCHLAG = "mab"
    NEBENKOSTEN_ABRECHNG = "nka"
    HAUSGELD_ABRECHNG = "hga"
    SONDERUMLAGE = "sonder"
    ALLGEMEINE_KOSTEN = "a"
    GRUNDSTEUER = "g"
    KOMMUNALE_DIENSTE = "k"  # Abschläge und Abrechnungen für Strom, Gas etc.
    REPARATUR = "r"
    DIENSTREISE = "d"
    SONSTIGE_KOSTEN = "s"
    VERSICHERUNG = "v"

    def toValue( self ) -> str:
        return self.value

    @staticmethod
    def getMemberNames() -> List[str]:
        """
        :return: ["BRUTTOMIETE", "NEBENKOSTEN_VORAUS", ...]
        """
        return list(sort( [m.name for m in EinAusArt] ))

    @staticmethod
    def getMemberNameByValue( value:str ) -> str:
        """
        :param value: z.B. "brm"
        :return: zugehörigen Namen, im Beispiel EinAusArt.BRUTTOMIETE
        """
        m = EinAusArt( value ).name
        return m

    @staticmethod
    def getValueByMemberName( name ) -> str:
        """
        :param name: z.B. EinAusArt.BRUTTOMIETE
        :return: zugehörigen value, im Beispiel "brm"
        """
        v = EinAusArt( name ).value
        return v

def test2():
    names = EinAusArt.getMemberNames()
    print( names )
    membername = EinAusArt.getMemberNameByValue( 'a' )
    print( membername )
    ea_art = EinAusArt.HAUSGELD_ABRECHNG
    val = ea_art.toValue()
    ea_art = EinAusArt.KOMMUNALE_DIENSTE
    val = ea_art.toValue()

    val = EinAusArt.getValueByMemberName( EinAusArt.HAUSGELD_ABRECHNG )
    print( val )

def test():
    # l = list(map(lambda c: c.value, EinAusArt ) )
    # print( l )
    # l = EinAusArt.getMemberNames()
    # print( l )
    #l = EinAusArt.getValueByMembername( "REPARATUR" )
    class E(Enum):
        AAA = "a"
        BBB = "b"
        CCC = "c"

    print( E.BBB.value )
    print( E.AAA.name )

    print( "end")


class abrechnung( Enum ):
    NK = 0,
    HG = 1

class tableAction( IntEnum ):
    INSERT = 0,
    UPDATE = 1,
    DELETE = 2

actionList = ( "INSERT", "UPDATE", "DELETE" )

class SollType( IntEnum ):
    MIETE_SOLL = 0,
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