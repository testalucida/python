from typing import Dict

from PySide2.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, QWidget, QMainWindow

from datehelper import getCurrentYearAndMonth, getNumberOfDays
from minikuendigungdlg import MiniKuendigungDlg

class MietverhaeltnisController:
    def __init__( self, parent ):
        self._parent = parent
        self._miniDlg = None

    def kuendigeMietverhaeltnisUsingMiniDialog( self, mv_id:str ) -> None:
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
        dlg.kuendigeMietverhaeltnis.connect( self.onKuendigeMietverhaeltnis )
        self._miniDlg = dlg
        dlg.show()

    def onKuendigeMietverhaeltnis( self, kuendDatum:str ) -> None:
        print( "MietverhaeltnisController.kuendigeMietverhaeltnis zum ", kuendDatum )



def test():
    app = QApplication()
    #dummy = QMainWindow()
    c = MietverhaeltnisController( None )
    c.kuendigeMietverhaeltnisUsingMiniDialog( "haupt_patrick" )

    app.exec_()

if __name__ == "__main__":
    test()