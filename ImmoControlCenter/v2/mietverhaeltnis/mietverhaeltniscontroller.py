from PySide2.QtWidgets import QWidget

from base.messagebox import InfoBox
from v2.icc.icccontroller import IccController


class MietverhaeltnisController( IccController ):
    def __init__( self, mv_id:str=None ):
        IccController.__init__( self )
        self._mv_id = mv_id

    def createGui( self ) -> QWidget:
        box = InfoBox( "Noch nicht realisiert", "Hieraus wird später die MietverhaeltnisView.", "", "OK" )
        box.exec_()
        return QWidget()

    @classmethod
    def fromMietverhaeltnis( cls, mv_id:str ):
        inst = cls()
        inst._mv_id = mv_id
        return inst

