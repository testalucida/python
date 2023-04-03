from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QDialog

from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame, IccTableView
from v2.icc.interfaces import XMtlZahlung, XEinAus, XSollMiete


#############  SollMieteController  #####################
from v2.sollhausgeld.sollhausgeldlogic import SollHausgeldLogic
from v2.sollmiete.sollmieteeditcontroller import SollMieteEditController
from v2.sollmiete.sollmietelogic import SollmieteLogic
from v2.sollmiete.sollmieteview import SollMieteView, SollMieteDialog


class SollHausgeldController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = SollHausgeldLogic()

    def createGui( self ) -> IccCheckTableViewFrame:
        pass


    def showHgvAndRueZuFue( self, weg_name:str, jahr:int, monthNumber:int ):
        """
        Zeigt die SollHausgeld-View mit den gewünschten Daten
        :param weg_name: WEG, der beauskunftet werden soll
        :param jahr:
        :param monthNumber: 1 -> Januar, ... , 12 -> Dezember
        :return:
        """
        print( "showHgvAndRueZuFue ", weg_name )

def test():
    app = QApplication()
    ctrl = SollHausgeldController()
    ctrl.showHgvAndRueZuFue( "WEG Remigiusstr. 17-23", 2023, 3 )

    app.exec_()