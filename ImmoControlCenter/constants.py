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