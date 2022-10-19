from PySide2.QtWidgets import QWidget

from base.messagebox import InfoBox
from v2.icc.icccontroller import IccController


class MietobjektController( IccController ):
    def __init__( self, mobj_id:str=None ):
        IccController.__init__( self )
        self._mobj_id = mobj_id

    def createGui( self ) -> QWidget:
        box = InfoBox( "Noch nicht realisiert", "Hieraus wird später die MietobjektView.", "", "OK" )
        box.exec_()
        return QWidget()

    @classmethod
    def fromMietobjekt( cls, mobj_id:str ):
        inst = cls()
        inst._mobj_id = mobj_id
        return inst

