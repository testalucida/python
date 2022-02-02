from typing import List

import jsonpickle

from icc.iccucc import IccUcc
from returnvalue import ReturnValue


class IccBaseServices:
    @staticmethod
    def getExistingYears() -> List[int]:
        # todo
        return [2021, 2022]

    @staticmethod
    def getHandwerkerNachBranchen() -> ReturnValue:
        jsn = IccUcc.getHandwerkerNachBranchen()
        rv = jsonpickle.decode( jsn )
        return rv

def test():
    rv = IccBaseServices.getHandwerkerNachBranchen()
    print( rv )