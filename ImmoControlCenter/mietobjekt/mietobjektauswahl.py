##############  MietobjektAuswahlDialog  #######################
from typing import List, Tuple

from PySide2.QtWidgets import QDialog

from business import BusinessLogic
from qtderivates import AuswahlDialog

############## MietobjektAuswahlDialog ###########################
class MietobjektAuswahldialog( AuswahlDialog ):
    def __init__(self, parent=None):
        AuswahlDialog.__init__( self, "Auswahl des Mietobjekts", parent )

##############  MietobjektAuswahl  #########################
class MietobjektAuswahl():
    def selectMietobjekt( self ) -> str:
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
                    return mobj_id
            raise Exception( "MietobjektAuswahl.selectMietobjekt: interner Fehler" )
        return ""