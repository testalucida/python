import json
from typing import List

from interfaces import XMietobjektExt
from mietobjekt.mietobjektucc import MietobjektUcc
from returnvalue import ReturnValue


class MietobjektServices:
    @staticmethod
    def getMietobjekte() -> List[XMietobjektExt]:
        mucc = MietobjektUcc()
        json_ = mucc.getMietobjekte()
        li = json.loads( json_ )

def test():
    res = MietobjektServices.getMietobjekte()