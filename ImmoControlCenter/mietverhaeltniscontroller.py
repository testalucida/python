from typing import Dict, Tuple

from PySide2.QtCore import Signal, QObject, Slot
from PySide2.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, QWidget, QMainWindow

from business import BusinessLogic
from datehelper import getCurrentYearAndMonth, getNumberOfDays
from minikuendigungdlg import MiniKuendigungDlg

class MietverhaeltnisController( QObject ):
    mietverhaeltnisGekuendigt = Signal( (str, str) )
    def __init__( self, parent ):
        QObject.__init__( self )
        self._parent = parent
        self._miniDlg = None

    def kuendigeMietverhaeltnisUsingMiniDialog( self, mv_id:str ) -> None:
        @Slot()
        def onKuendigeSlot( mv_id, kuendDatum ):
            print( "onKuendigeSlot: kündige zum ", kuendDatum, " für ", mv_id )
            self.kuendigeMietverhaeltnis( mv_id, kuendDatum )
        """
        Öffnet einen MiniKuendigungDlg und lässt den Anwender die Kündigungsdaten für mv_id erfassen.
        Nach Drücken von "Kündigen" wird die Kündigung in die Datenbank geschrieben
        und das Kündigungsdatum an den Aufrufer zurückgeliefert.
        Ein Aufrufer ist der CheckController. Er muss mit dem zurückgegebenen Datum sein TableModel aktualisieren.
        :param mv_id: ID des Mieters, der zu kündigen ist
        """
        dlg = MiniKuendigungDlg( self._parent )
        dlg.setName( mv_id )
        d = getCurrentYearAndMonth()
        dlg.setDatum( d["year"], d["month"]+3, getNumberOfDays( d["month"]+3 ) )
        #dlg.kuendigeMietverhaeltnis.connect( self.onKuendigeMietverhaeltnis )
        dlg.kuendigeMietverhaeltnis.connect( onKuendigeSlot )
        self._miniDlg = dlg
        dlg.show()

    def kuendigeMietverhaeltnis( self, mv_id:str, kuendDatum:str ) -> None:
        # Kündigung in der Datenbank durchführen
        BusinessLogic.inst().kuendigeMietverhaeltnis( mv_id, kuendDatum )
        self.mietverhaeltnisGekuendigt.emit( mv_id, kuendDatum )

##########################################################################################

def onGekuendigt( mv_id, kuendDatum ):
    print( "erfolgreich gekündigt: ", mv_id, ", ", kuendDatum )


def test():
    app = QApplication()
    #dummy = QMainWindow()
    c = MietverhaeltnisController( None )
    c.kuendigeMietverhaeltnisUsingMiniDialog( "haupt_patrick" )
    c.mietverhaeltnisGekuendigt.connect( onGekuendigt )
    app.exec_()

if __name__ == "__main__":
    test()