import json

from interfaces import XMietverhaeltnis
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from returnvalue import ReturnValue
from transaction import *

class MietverhaeltnisGetUcc:
    """
    Sammelbecken für alle lesenden Mietverhältnis-Zugriffe.
    """
    def __init__( self):
        pass

    def getAktuellesMietverhaeltnis( self, mv_id:str ) -> str:
        mvlogic = MietverhaeltnisLogic()
        try:
            x:XMietverhaeltnis = mvlogic.getAktuellesMietverhaeltnis( mv_id )
            json_ = json.dumps( x.__dict__ )
        except Exception as ex:
            raise NotImplementedError( "MietverhaeltnisGetUcc.getAktuellesMietverhaeltnis() -- EXCEPTION-Handling")


def test():
    pass