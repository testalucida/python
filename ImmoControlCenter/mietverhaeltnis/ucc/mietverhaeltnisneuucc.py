from interfaces import XMietverhaeltnis
from returnvalue import ReturnValue
from transaction import *

class MietverhaeltnisNeuUcc:
    def __init__( self, xmv:XMietverhaeltnis ):
        self._xmv = xmv
        raise NotImplementedError( "MietverhaeltnisNeuUcc.__init__" )

    def processMietverhaeltnisNeu( self ):
        raise NotImplementedError( "MietverhaeltnisNeuUcc.processMietverhaeltnisNeu()" )