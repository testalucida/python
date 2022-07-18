import jsonpickle

from interfaces import XMietobjektExt
from mietobjekt.mietobjektlogic import MietobjektLogic
from returnvalue import ReturnValue
from base.transaction import BEGIN_TRANSACTION, COMMIT_TRANSACTION, ROLLBACK_TRANSACTION


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

    def modifyObjekt( self, x:XMietobjektExt ) -> str:
        BEGIN_TRANSACTION()
        try:
            self._logic.modifyObjekt( x )
            COMMIT_TRANSACTION()
            return ""
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            return str( ex )


