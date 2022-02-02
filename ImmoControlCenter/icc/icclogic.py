from typing import List

from icc.iccdata import IccData
from interfaces import XHandwerkerKurz


class IccLogic:
    def __init__( self ):
        self._db = IccData()

    def getHandwerkerNachBranchen( self ) -> List[str]:
        """
        Gibt eine Liste von strings zurück, von denen jeder aus Branche, Name und Adresse (Ort) zusammengesetzt ist.
        Sortiert nach Branche.
        :return:
        """
        def compose( x:XHandwerkerKurz ) -> str:
            s = x.branche + ": " + x.adresse + " >>> " + x.name
            return s
        xlist:List[XHandwerkerKurz] = self._db.getHandwerkerKurz( "branche, adresse" )
        strlist = [compose( x ) for x in xlist]
        return strlist