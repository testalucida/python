
from PySide2.QtCore import Signal, QObject, Slot, QPoint
from PySide2.QtWidgets import QApplication

from business import BusinessLogic
import datehelper
from interfaces import XMietverhaeltnis
from messagebox import ErrorBox
from mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisView, MietverhaeltnisDialog
from mietverhaeltnis.minikuendigungdlg import MiniKuendigungDlg

class MiniKuendigungsController( QObject ):
    mietverhaeltnisGekuendigt = Signal( (str, str) )

    def __init__( self, parent ):
        QObject.__init__( self )
        self._parent = parent
        self._miniDlg = None

    def kuendigeMietverhaeltnisUsingMiniDialog( self, mv_id:str ) -> None:
        @Slot()
        def onKuendigeSlot( mv_id, kuendDatum ):
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
        kuenddatTuple = self.getKuendigungsdatum( mv_id )
        if kuenddatTuple:
            dlg.setDatum( kuenddatTuple[0], kuenddatTuple[1], kuenddatTuple[2] )
        else:
            # d = getCurrentYearAndMonth()
            # dlg.setDatum( d["year"], d["month"]+3, getNumberOfDays( d["month"]+3 ) )
            lastofmonth = datehelper.getLastOfMonth()
            kuenddatum = datehelper.addMonths( lastofmonth, 3 )
            dlg.setDatum( kuenddatum.year, kuenddatum.month, kuenddatum.day )
        dlg.kuendigeMietverhaeltnis.connect( onKuendigeSlot )
        self._miniDlg = dlg
        dlg.show()

    def getKuendigungsdatum( self, mv_id:str ) -> (int, int, int) or None:
        return BusinessLogic.inst().getKuendigungsdatum2( mv_id )

    def kuendigeMietverhaeltnis( self, mv_id:str, kuendDatum:str ) -> None:
        # Kündigung in der Datenbank durchführen
        try:
            BusinessLogic.inst().kuendigeMietverhaeltnis( mv_id, kuendDatum )
            self.mietverhaeltnisGekuendigt.emit( mv_id, kuendDatum )
        except Exception as ex:
            box = ErrorBox( "Kündigung hat nicht geklappt", "MiniKuendigungsController.kuendigeMietverhaeltnis()", str( ex ) )
            box.exec_()

##########################################################################################

def onGekuendigt( mv_id, kuendDatum ):
    print( "erfolgreich gekündigt: ", mv_id, ", ", kuendDatum )


def test():
    app = QApplication()
    #dummy = QMainWindow()
    c = MiniKuendigungsController( None )
    c.kuendigeMietverhaeltnisUsingMiniDialog( "haupt_patrick" )
    c.mietverhaeltnisGekuendigt.connect( onGekuendigt )
    app.exec_()

if __name__ == "__main__":
    test()