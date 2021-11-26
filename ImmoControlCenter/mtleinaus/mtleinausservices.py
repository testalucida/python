from mtleinaus.ucc.folgejahrneuucc import FolgejahrNeuUcc
from returnvalue import ReturnValue


class MtlEinAusServices:
    @staticmethod
    def processFolgejahrNeu() -> ReturnValue:
        folgejahrUcc = FolgejahrNeuUcc()
        return folgejahrUcc.processFolgejahrNeu()