from v2.einaus.einauslogic import EinAusLogic
from v2.icc.constants import EinAusArt
from v2.icc.icclogic import IccLogic
from v2.icc.interfaces import XSummen


class MainLogic( IccLogic ):
    def __init__( self ):
        IccLogic.__init__( self )

    def exportDatabaseToServer( self ):
        #todo
        pass

    def importDatabaseFromServer( self ):
        #todo
        pass

    def getSummen( self, jahr:int ) -> XSummen:
        ea_logic = EinAusLogic()
        x = XSummen()
        x.sumEin = round( ea_logic.getEinzahlungenSumme( jahr ) )
        x.sumHGV = round( ea_logic.getHGVAuszahlungenSumme( jahr ) )
        x.sumSonstAus = round( ea_logic.getAuszahlungenSummeOhneHGV( jahr ) )
        x.saldo = x.sumEin + x.sumHGV + x.sumSonstAus
        return x