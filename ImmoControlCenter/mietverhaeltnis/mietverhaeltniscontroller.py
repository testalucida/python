from typing import Any, List

from PySide2.QtCore import QPoint
from PySide2.QtWidgets import QWidget, QApplication

from business import BusinessLogic
from icc.icccontroller import IccController
from interfaces import XMietverhaeltnis
from messagebox import InfoBox
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisDialog, MietverhaeltnisView
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic


class MietverhaeltnisController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:MietverhaeltnisView = None
        self._mvlogic = MietverhaeltnisLogic()
        self._mvlist:List[XMietverhaeltnis] = None # Liste der Mietverhältnisse eines Mietobjekts
        self._mv: XMietverhaeltnis = None # das aktuell im View angezeigte Mietverhältnis

    def showMietverhaeltnis( self, mv_id:str, point:QPoint ):
        """
        Altlast: diese Methode wird aufgerufen, wenn in der Mieten-Tabelle per Kontextmenü
        (rechter Mausklick auf den Namen) "Mietverhältnis anzeigen" gewählt wird.
        :param mv_id:
        :param point:
        :return:
        """
        #mv:XMietverhaeltnis = BusinessLogic.inst().getAktuellesOderZukuenftigesMietverhaeltnis( mv_id )
        mv = self._mvlogic.getAktuellesMietverhaeltnis( mv_id )
        if not mv: # wenn z.B. der Mieter schon in der Tabelle erscheint, aber das Mietverhältnis noch nicht begonnen hat.
            box = InfoBox( "Sorry", "Die Daten können nicht angezeigt werden.", "Das Mietverhältnis hat noch nicht begonnen.", "OK" )
            box.exec_()
        else:
            dlg = MietverhaeltnisDialog( mv )
            dlg.exec_()

    def createView( self ) -> QWidget or None:
        # zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
        mietobjektAuswahl = MietobjektAuswahl()
        mobj_id = mietobjektAuswahl.selectMietobjekt()
        if not mobj_id: return None
        #xmv:XMietverhaeltnis = self._mvlogic.getAktuellesMietverhaeltnisByMietobjekt( mobj_id )
        self._mvlist = self._mvlogic.getMietverhaeltnisListe( mobj_id )
        # busi = BusinessLogic.inst()
        # mv_id = busi.getAktuelleMietverhaeltnisId( mobj_id )
        # xmv:XMietverhaeltnis = busi.getAktuellesOderZukuenftigesMietverhaeltnis( mv_id )
        self._mv = self._mvlist[0]
        self._view = MietverhaeltnisView( self._mv , withSaveButton=True )
        self._view.save.connect( self.writeChanges )
        self._view.prevMv.connect( self.onPrevMv )
        self._view.nextMv.connect( self.onNextMv )
        return self._view

    def onPrevMv( self ):
        self._browse( False )

    def onNextMv( self ):
        self._browse( True )

    def _browse( self, next:bool ):
        if len( self._mvlist ) < 2:
            box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.", "Es gibt nur ein Mietverhältnis.", "OK" )
            box.exec_()
            return
        idx = self._mvlist.index( self._mv )
        max = len( self._mvlist ) - 1
        if next: # "next" geklickt
            if idx == 0:
                box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.",
                               "Das jüngste Mietverhältnis wird angezeigt.", "OK" )
                box.exec_()
                return
            self._mv = self._mvlist[idx-1]
            self._view.clear()
            self._view.setMietverhaeltnisData( self._mv )
        else: # "previous" geklickt
            if idx == max:
                box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.",
                               "Das älteste Mietverhältnis wird angezeigt.", "OK" )
                box.exec_()
                return
            self._mv = self._mvlist[idx+1]
            self._view.clear()
            self._view.setMietverhaeltnisData( self._mv )



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
                self._view.resetChangeFlag()
                return True
            except Exception as ex:
                self.showErrorMessage( "Mietverhältnis: Speichern fehlgeschlagen", str( ex ) )
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
