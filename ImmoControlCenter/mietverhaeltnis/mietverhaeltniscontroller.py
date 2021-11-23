from typing import Any

from PySide2.QtCore import QObject, Signal, QPoint
from PySide2.QtWidgets import QWidget, QApplication

from business import BusinessLogic
from icccontroller import IccController
from interfaces import XMietverhaeltnis
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisDialog, MietverhaeltnisView


class MietverhaeltnisController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:MietverhaeltnisView = None
        self._mv:XMietverhaeltnis = None

    def showMietverhaeltnis( self, mv_id:str, point:QPoint ):
        """
        Altlast: diese Methode wird aufgerufen, wenn in der Mieten-Tabelle per Kontextmenü
        (rechter Mausklick auf den Namen) "Mietverhältnis anzeigen" gewählt wird.
        :param mv_id:
        :param point:
        :return:
        """
        mv:XMietverhaeltnis = BusinessLogic.inst().getAktuellesOderZukuenftigesMietverhaeltnis( mv_id )
        dlg = MietverhaeltnisDialog( mv )
        dlg.exec_()

    def createView( self ) -> QWidget:
        # zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
        mietobjektAuswahl = MietobjektAuswahl()
        mobj_id = mietobjektAuswahl.selectMietobjekt()
        if not mobj_id: return
        busi = BusinessLogic.inst()
        mv_id = busi.getAktuelleMietverhaeltnisId( mobj_id )
        xmv:XMietverhaeltnis = busi.getAktuellesOderZukuenftigesMietverhaeltnis( mv_id )
        self._view = MietverhaeltnisView( xmv, withSaveButton=True )
        self._view.save.connect( self.writeChanges )
        self._mv = xmv
        return self._view

    def _validate( self ) -> bool:
        # Validierung sollte im ***Model*** sein, nicht im Controller.
        # siehe: https://stackoverflow.com/questions/5651175/mvc-question-should-i-put-form-validation-rules-in-the-controller-or-model
        # und https://stackoverflow.com/questions/5305854/best-place-for-validation-in-model-view-controller-model
        v = self._view
        msg = ""
        rc = True
        mvcopy = v.getMietverhaeltnisCopyWithChanges()
        if not mvcopy.von:
            msg = "Mietbeginn fehlt"
        if mvcopy.bis and mvcopy.bis < mvcopy.von:
            msg = "Das Mietende darf nicht vor dem Mietbeginn liegen."
        elif not mvcopy.name:
            msg = "Der Nachname des ersten Mieters fehlt."
        elif not mvcopy.vorname:
            msg = "Der Vorname des ersten Mieters fehlt."
        elif mvcopy.name2 > " " and not mvcopy.vorname2:
            msg = "Vorname des zweiten Mieters fehlt."
        elif not mvcopy.anzahl_pers or mvcopy.anzahl_pers == 0:
            msg = "Anzahl Personen muss angegeben sein."
        elif not mvcopy.nettomiete or mvcopy.nettomiete == 0 or not mvcopy.nkv or mvcopy.nkv == 0:
            msg = "Nettomiete und Nebenkosten müssen angegeben werden."

        if msg > " ":
            self.showErrorMessage( "Validierung fehlgeschlagen", msg )
            rc = False
        if not mvcopy.telefon and not mvcopy.mobil and not mvcopy.mailto:
            self.showWarningMessage( "Validierung kritisch", "Es ist keine Kontaktmöglichkeit angegeben!\n"
                                                             "Telefon, Mobilfunk und Mailadresse sind leer!" )
        return rc

    def getChanges( self ) -> Any:
        pass

    def writeChanges( self, changes: Any = None ) -> bool:
        if self._validate():
            self._view.applyChanges()
            try:
                BusinessLogic.inst().saveMietverhaeltnis( self._mv )
                return True
            except Exception as ex:
                self.showErrorMessage( "Mieterwechsel: Speichern fehlgeschlagen", str( ex ) )
                return False
        return False

    def clearChanges( self ) -> None:
        pass

    def getViewTitle( self ) -> str:
        title = "Mieterdaten von Mieter: " + self._mv.vorname + " " + self._mv.name
        if self._mv.name2: title += ( " und " + self._mv.vorname2 + " " + self._mv.vorname2 )
        return title

    def isChanged( self ) -> bool:
        xcopy = self._view.getMietverhaeltnisCopyWithChanges()
        return False if xcopy.equals( self._mv ) else True


###################################################################################
def test():
    app = QApplication()
    c = MietverhaeltnisController()
    v = c.createView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()
