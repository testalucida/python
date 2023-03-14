from v2.icc.icclogic import IccLogic
from v2.icc.interfaces import XSollHausgeld
from v2.sollhausgeld.sollhausgelddata import SollHausgeldData


class SollHausgeldLogic( IccLogic ):
    def __init__( self ):
        IccLogic.__init__( self )
        self._data = SollHausgeldData()

    def getCurrentSollHausgeld( self, mobj_id:str ) -> XSollHausgeld:
        x:XSollHausgeld = self._data.getCurrentSollHausgeld( mobj_id )
        return x


###################  TEST   TEST   TEST   ##################
def test():
    logic = SollHausgeldLogic()
    x = logic.getCurrentSollHausgeld( "charlotte" )
    x.print()