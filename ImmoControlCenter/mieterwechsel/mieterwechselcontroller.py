from typing import List, Dict, Tuple

from PySide2.QtWidgets import QApplication, QDialog

from business import BusinessLogic
from mieterwechsel.mieterwechselgui import MietobjektAuswahldialog, MieterwechselDialog


class MieterwechselController:
    def __init__( self ):
        pass

    def startWork( self ):
        dlg = MietobjektAuswahldialog()
        mobj_list:List[str] = BusinessLogic.inst().getAllMietobjekte()
        dlg.appendItemList( mobj_list )
        if dlg.exec_() == QDialog.Accepted:
            auswahl:List[Tuple] = dlg.getSelection()
            self._doWechsel( auswahl[0][0] )

    def _doWechsel( self, mobj_id:str ):
        dlg = MieterwechselDialog( "Mieterwechsel:  " + mobj_id )
        if dlg.exec_() == QDialog.Accepted:
            pass

def test():
    app = QApplication()
    c = MieterwechselController()
    c.startWork()

if __name__ == "__main__":
    test()