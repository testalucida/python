from typing import Any


class ReturnValue:
    def __init__( self, exceptiontype:str="", errormessage:str= "", returnvalue:Any=None ):
        self.exceptiontype:str = exceptiontype # wird nur bei einer Exception gefüllt, nicht bei sonstigen Fehlern
        self.errormessage:str = errormessage # wird bei jeder Art von Fehler versorgt
        self.returnvalue:Any = returnvalue # hier sollten keine Fehlermeldungen eingetragen werden

    def missionAccomplished( self ) -> bool:
        return (not self.exceptiontype and not self.errormessage)

    @classmethod
    def fromException( cls, ex:Exception, returnvalue:Any=None ):
        inst = cls()
        inst.exceptiontype = type( ex ).__name__
        inst.errormessage = str( ex )
        inst.returnvalue = returnvalue
        return inst

    @classmethod
    def fromValue( cls, value:Any ):
        inst = cls()
        inst.returnvalue = value
        return inst

    @classmethod
    def fromError( cls, errormessage:str ):
        inst = cls()
        inst.errormessage = errormessage
        return inst

def test():
    rv = ReturnValue( "")
    ok = rv.missionAccomplished()
    if not ok:
        print( "NOK" )
    else:
        print( "OK" )