from mtleinaus.mtleinauslogic import MtlEinAusLogic
from returnvalue import ReturnValue
from transaction import *

class FolgejahrNeuUcc:
    def __init__(self):
        self._mealogic = MtlEinAusLogic()

    def processFolgejahrNeu( self ) -> ReturnValue:
        BEGIN_TRANSACTION()
        try:
            jahr = self._mealogic.createFolgejahrSet()
            retval = ReturnValue( returnvalue=jahr )
            return retval
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            return ReturnValue.fromException( ex )
        COMMIT_TRANSACTION()

