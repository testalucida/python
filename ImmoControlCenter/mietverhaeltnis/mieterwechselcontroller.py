from typing import List, Dict, Tuple

from PySide2.QtWidgets import QApplication, QDialog

from business import BusinessLogic
from interfaces import XMietverhaeltnis
from mietverhaeltnis.mieterwechselgui import MietobjektAuswahldialog, MieterwechselDialog


class MieterwechselController:
    def __init__( self ):
        pass

    def startWork( self ):
        dlg = MietobjektAuswahldialog()
        itemtext_list, mobj_list = BusinessLogic.inst().getAllMietobjekte()
        dlg.appendItemList( itemtext_list )
        if dlg.exec_() == QDialog.Accepted:
            auswahl:List[Tuple] = dlg.getSelection()
            itemtext = auswahl[0][0]
            mobj_id = ""
            for n in range( len( itemtext_list ) ):
                if itemtext_list[n] == itemtext:
                    mobj_id = mobj_list[n]
                    break
            self._doWechsel( mobj_id )

    def _doWechsel( self, mobj_id:str ):
        busi:BusinessLogic = BusinessLogic.inst()
        mv_id = busi.getAktuelleMietverhaeltnisId( mobj_id )
        xmv_akt:XMietverhaeltnis = busi.getAktuellesMietverhaeltnis( mv_id )
        xmv_neu = XMietverhaeltnis()
        dlg = MieterwechselDialog( "Mieterwechsel:  " + mobj_id )
        dlg.setAktuellesMietverhaeltnis( xmv_akt )
        dlg.setNeuesMietverhaeltnis( xmv_neu )
        if dlg.exec_() == QDialog.Accepted:
            pass

def test():
    app = QApplication()
    c = MieterwechselController()
    c.startWork()

if __name__ == "__main__":
    test()