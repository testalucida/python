from enum import Enum, IntEnum

class einausart( Enum ):
    MIETE = 1,
    HGV = 2

class tableAction( IntEnum ):
    INSERT = 0,
    UPDATE = 1,
    DELETE = 2

actionList = ( "INSERT", "UPDATE", "DELETE" )

class SollType( IntEnum ):
    MIETE_SOLL = 0,
    HAUSGELD_SOLL = 1