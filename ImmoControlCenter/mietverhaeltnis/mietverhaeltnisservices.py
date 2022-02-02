from interfaces import XMietverhaeltnis, XMieterwechsel
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from mietverhaeltnis.ucc.mieterwechselucc import MieterwechselUcc
from returnvalue import ReturnValue


class MietverhaeltnisServices:
    @staticmethod
    def processMieterwechsel( xmw:XMieterwechsel ) -> ReturnValue:
        mucc = MieterwechselUcc( xmw )
        return mucc.processMieterwechsel()

    # @staticmethod
    # def processNeuesMietverhaeltnis( xmv:XMietverhaeltnis ) -> ReturnValue:
    #     mucc = MietverhaeltnisNeuUcc( xmv )
    #     return mucc.processMietverhaeltnisNeu()

    # @staticmethod
    # def getAktuellesMietverhaeltnis( mv_id:str ) -> ReturnValue:
    #     raise NotImplementedError( "MietverhaeltnisServices.getAktuellesMietverhaeltnis()" )


def test1():
    xmv_alt = XMietverhaeltnis()
    xmv_alt.id = 11
    xmv_alt.mv_id = "knacker_panzer"
    xmv_alt.von = "2021-11-01"
    xmv_alt.bis = "2021-11-02"

    xmv_neu = XMietverhaeltnis()
    xmv_neu.id = 0
    xmv_neu.mv_id = ""
    xmv_neu.mobj_id = "bueb"
    xmv_neu.von = "2022-11-02"
    xmv_neu.name = "Schnörpfel"
    xmv_neu.vorname = "Schnurpf"
    xmv_neu.nettomiete = 500.00
    xmv_neu.nkv = 100.00

    mwdata = XMieterwechsel( xmv_alt, xmv_neu )

    retVal: ReturnValue = MietverhaeltnisServices.processMieterwechsel( mwdata )
    print( retVal.exceptiontype, ": ", retVal.errormessage )

def test2():
    xmv_alt = XMietverhaeltnis()
    xmv_alt.id = 11
    xmv_alt.mv_id = "amaral_cynthia"
    xmv_alt.von = "2019-01-01"
    xmv_alt.bis = "2021-12-31" # <--- sei durch den Dialog so eingestellt

    xmv_neu = XMietverhaeltnis()
    xmv_neu.id = 0
    xmv_neu.mv_id = "angstrumpf_pippi"
    xmv_neu.mobj_id = "kleist_32"
    xmv_neu.von = "2022-01-01"
    xmv_neu.name = "Angstrumpf"
    xmv_neu.vorname = "Pippi"
    xmv_neu.nettomiete = 300.0
    xmv_neu.nkv = 88.00

    mwdata = XMieterwechsel( xmv_alt, xmv_neu )

    retVal:ReturnValue = MietverhaeltnisServices.processMieterwechsel( mwdata )
    print( retVal.exceptiontype, ": ", retVal.errormessage )

if __name__ == "__main__":
    test1()