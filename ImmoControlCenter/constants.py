from enum import Enum, IntEnum

class einausart( Enum ):
    MIETE = 1,
    HGV = 2

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

class Zahlart( IntEnum ):
    BRUTTOMIETE = 0,
    NKA = 1,
    HGV = 2,
    HGA = 3,
    SONSTAUS = 4

zahlartstrings = ("bruttomiete", "nka", "hgv", "hga", "sonstaus")

class Sonstaus_Kostenart( Enum ):
    ALLGEMEIN = "a",
    GRUNDSTEUER = "g",
    REPARATUR = "r",
    SAMMEL = "sam",
    SONSTIGE = "s",
    VERSICHERUNG = "v"

class DetailLink( Enum ):
    ERHALTUNGSKOSTEN = "REP",
    ZU_VERTEIL_GESAMTKOSTEN_VJ = "VJ_GES", # Zu verteilende Aufwände, die im Veranlag.jahr entstanden sind
    ERHALTUNGSKOSTEN_VERTEILT = "VREP",   # Teilbeträge der im Veranlagg.jahr zu berücksichtigenden Aufwände, die im VJ
                                         # oder in den zurückliegenden 4 Jahren entstanden und zu verteilen sind.
    ALLGEMEINE_KOSTEN = "AK",
    SONSTIGE_KOSTEN = "SK"