from PySide2.QtCore import QObject, Signal

from v2.icc.interfaces import XEinAus


class EinAusWriteDispatcher( QObject ):
    ea_inserted = Signal( XEinAus )
    ea_updated = Signal( XEinAus )
    ea_deleted = Signal( int )
    __instance = None
    def __init__( self ):
        QObject.__init__( self )
        if EinAusWriteDispatcher.__instance:
            raise Exception( "EinAusWriteDispatcher is a Single. It may only be instantiated once." )
        else:
            EinAusWriteDispatcher.__instance = self

    @staticmethod
    def inst() -> __instance:
        if EinAusWriteDispatcher.__instance is None:
            EinAusWriteDispatcher()
        return EinAusWriteDispatcher.__instance

    def einaus_inserted( self, x:XEinAus ):
        self.ea_inserted.emit( x )

    def einaus_updated( self, x:XEinAus ):
        self.ea_updated.emit( x )

    def einaus_deleted( self, ea_id:int ):
        self.ea_deleted.emit( ea_id )