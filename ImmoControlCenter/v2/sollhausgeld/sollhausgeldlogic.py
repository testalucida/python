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

    def getSollHausgeldAm( self, mobj_id:str, jahr: int, monthNumber: int ) -> XSollHausgeld or None:
        """
        :param mobj_id:
        :param jahr:
        :param monthNumber: 1 -> Januar,..., 12 -> Dezember
        :return:
        """
        return self._data.getSollHausgeldAm( mobj_id, jahr, monthNumber )


###################  TEST   TEST   TEST   ##################
def test():
    logic = SollHausgeldLogic()
    x = logic.getCurrentSollHausgeld( "charlotte" )
    x.print()