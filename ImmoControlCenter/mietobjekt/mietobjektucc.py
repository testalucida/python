import jsonpickle

from mietobjekt.mietobjektlogic import MietobjektLogic
from returnvalue import ReturnValue


class MietobjektUcc:
    """
    Sammelbecken für alle Mietobjekt-Prozesse.
    """
    def __init__( self):
        self._logic = MietobjektLogic()

    def getMasterobjektNamen( self ) -> str:
        try:
            namenlist = self._logic.getMasterobjektNamen()
            rv: ReturnValue = ReturnValue.fromValue( namenlist )
        except Exception as ex:
            rv: ReturnValue = ReturnValue.fromException( ex )
        jsn = jsonpickle.encode( rv )
        return jsn

    def getMietobjektNamen( self, master_name:str ) -> str:
        try:
            namenlist = self._logic.getMietobjektNamen( master_name )
            rv: ReturnValue = ReturnValue.fromValue( namenlist )
        except Exception as ex:
            rv: ReturnValue = ReturnValue.fromException( ex )
        jsn = jsonpickle.encode( rv )
        return jsn

    def getMietobjekte( self, mv_id:str ) -> str:
        raise NotImplementedError( "MietobjektUcc.getMietobjekte()")