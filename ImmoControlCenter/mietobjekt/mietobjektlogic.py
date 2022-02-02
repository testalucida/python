from typing import List

from mietobjekt.mietobjektdata import MietobjektData


class MietobjektLogic:
    def __init__( self ):
        self._db = MietobjektData()

    def getMasterobjektNamen( self ) -> List[str]:
        masterlist = self._db.getMasterobjektNamen()
        return masterlist

    def getMietobjektNamen( self, master_name:str ) -> List[str]:
        namenlist = self._db.getMietobjektNamen( master_name )
        return namenlist

    def getMietobjekteKurzZuMaster( self, master_name:str ):
        db = MietobjektData()
        mobj_idlist = db.getMietobjekteKurzZuMaster( master_name )
        return mobj_idlist
