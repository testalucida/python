import json
from typing import List

import jsonpickle

from interfaces import XMietobjektExt
from mietobjekt.mietobjektucc import MietobjektUcc
from returnvalue import ReturnValue


class MietobjektServices:

    @staticmethod
    def getMasterobjektNamen() -> ReturnValue:
        mucc = MietobjektUcc()
        jsn = mucc.getMasterobjektNamen()
        rv:ReturnValue = jsonpickle.decode( jsn )
        return rv

    @staticmethod
    def getMietobjektNamen( master_name:str ) -> ReturnValue:
        mucc = MietobjektUcc()
        jsn = mucc.getMietobjektNamen( master_name )
        rv: ReturnValue = jsonpickle.decode( jsn )
        return rv

    @staticmethod
    def getMietobjekte() -> List[XMietobjektExt]:
        mucc = MietobjektUcc()
        raise NotImplementedError( "MietobjektServices.getMietobjekte()" )

def test():
    res = MietobjektServices.getMietobjekte()