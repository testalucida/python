from business import BusinessLogic
from offene_posten.offenepostengui import OffenePostenDialog


class OffenePostenController:
    def __init__( self ):
        self._dlg:OffenePostenDialog = None

    def createDialog( self, parent ) -> OffenePostenDialog:
        model = BusinessLogic.inst().getOposModel()
        self._dlg = OffenePostenDialog( parent )
        return self._dlg