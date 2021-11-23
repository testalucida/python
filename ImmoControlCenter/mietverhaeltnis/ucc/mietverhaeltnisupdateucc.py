from interfaces import XMietverhaeltnis


class MietverhaeltnisUpdateUcc:
    def __init__( self, xmv:XMietverhaeltnis ) -> str:
        self._xmv = xmv
        raise NotImplementedError( "MietverhaeltnisUpdateUcc.__init__" )

    def processMietverhaeltnisUpdate( self ):
        raise NotImplementedError( "MietverhaeltnisUpdateUcc.processMietverhaeltnisUpdate" )
