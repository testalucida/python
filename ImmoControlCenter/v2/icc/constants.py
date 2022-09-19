from enum import Enum, IntEnum

# Monatsnamen, die den Spaltennamen in Tabelle <mtleinaus> entsprechen und in die Spalte zahlung.monat
# eingetragen werden:
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
    BRUTTOMIETE = "brm",
    NEBENKOSTEN_VORAUS = "nkv"
    HAUSGELD_VORAUS = "hgv",
    NEBENKOSTEN_ABRECHNG = "nka",
    HAUSGELD_ABRECHNG = "hga",
    ALLGEMEINE_KOSTEN = "a",
    GRUNDSTEUER = "g",
    KOMMUNALE_DIENSTE = "k",
    REPARATUR = "r",
    SONSTIGE_KOSTEN = "s",
    VERSICHERUNG = "v"

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