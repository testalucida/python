from typing import Any, List

from PySide2.QtCore import QPoint, Slot
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QWidget, QApplication, QMenu, QDialog

from base.baseqtderivates import BaseAction, BaseEdit, FloatEdit, IntEdit, SmartDateEdit
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from base.messagebox import InfoBox, ErrorBox
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XMietverhaeltnis
from v2.mietobjekt.mietobjektcontroller import MietobjektAuswahl
from v2.mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisView, MietverhaeltnisDialog, \
    MietverhaeltnisKuendigenDialog
from v2.mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic


class MietverhaeltnisController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:MietverhaeltnisView = None
        self._mvlogic = MietverhaeltnisLogic()
        self._mvlist:List[XMietverhaeltnis] = None # Liste der Mietverhältnisse eines Mietobjekts
        self._mv: XMietverhaeltnis = None # das aktuell im View angezeigte Mietverhältnis

    def createGui( self ) -> QWidget:
        pass

    def getMenu( self ) -> QMenu or None:
        """
        Jeder Controller liefert dem MainController ein Menu, das im MainWindow in der Menubar angezeigt wird
        :return:
        """
        menu = QMenu( "Mietverhältnis" )
        action = BaseAction( "Neues Mietverhältnis anlegen...", parent=menu )
        action.triggered.connect( self.onMietverhaeltnisNeu )
        menu.addAction( action )
        action = BaseAction( "Mietverhältnis anschauen und bearbeiten...", parent=menu )
        action.triggered.connect( self.onMietverhaeltnisShow )
        menu.addAction( action )
        action = BaseAction( "Mietverhältnis kündigen...", parent=menu ) #
        action.triggered.connect( self.onMietverhaeltnisKuendigen )
        menu.addAction( action )
        return menu

    @Slot()
    def onMietverhaeltnisNeu( self, mobj_id:str=None ):
        """
        Wird aufgerufen, wenn in der Menübar der Anwendung "Mietverhältnis anzeigen und bearbeiten..." geklickt wurde
        :return:
        """
        if not mobj_id:
            # zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
            mietobjektAuswahl = MietobjektAuswahl()
            xmo = mietobjektAuswahl.selectMietobjekt()
            if not xmo: return None
            mobj_id = xmo.mobj_id
        # letztes Mietverhältnis holen
        xmv:XMietverhaeltnis = self._mvlogic.getAktuellesMietverhaeltnisByMietobjekt( mobj_id )
        self.createMvView( mobj_id )
        dlg = MietverhaeltnisDialog( self._view )
        dlg.exec_()

    @Slot()
    def onMietverhaeltnisShow( self, mv_id:str = None ):
        """
        Wird aufgerufen, wenn in der Menübar der Anwendung "Mietverhältnis anzeigen und bearbeiten..." geklickt wurde
        :return:
        """
        mobj_id = ""
        if not mv_id:
            # zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
            mietobjektAuswahl = MietobjektAuswahl()
            xmo = mietobjektAuswahl.selectMietobjekt()
            if not xmo: return None
            mobj_id = xmo.mobj_id
        else:
            xmv = self._mvlogic.getAktuellesMietverhaeltnis( mv_id )
            mobj_id = xmv.mobj_id
        self.createMvView( mobj_id )
        dlg = MietverhaeltnisDialog( self._view )
        dlg.exec_()

    @Slot()
    def onMietverhaeltnisKuendigen( self, mv_id:str=None ):
        """
        Wird aufgerufen, wenn in der Menübar der Anwendung "Mietverhältnis kündigen..." geklickt wurde
        :param mv_id: ist versorgt, wenn der Aufruf dieses Slots aus dem Context-Menü der Miete-TableView kommt.
                      Wenn der Aufruf aus der Toolbar der Anwendung kommt, ist mv_id leer.
        :return:
        """
        ctrl = MietverhaeltnisKuendigenController()
        ctrl.processKuendigung( mv_id )

    def showMietverhaeltnis( self, mv_id:str ):
        """
        Methode wird aus aer Mieten-Tabelle aufgerufen, nach Mausklick auf Kontextmenü "Mietverhältnis anzeigen"
        :param mv_id:
        :param point:
        :return:
        """
        #mv:XMietverhaeltnis = BusinessLogic.inst().getAktuellesOderZukuenftigesMietverhaeltnis( mv_id )
        xmv:XMietverhaeltnis = self._mvlogic.getAktuellesMietverhaeltnis( mv_id )
        if not xmv: # wenn z.B. der Mieter schon in der Tabelle erscheint, aber das Mietverhältnis noch nicht begonnen hat.
            box = InfoBox( "Sorry...", "Die Daten können nicht angezeigt werden.",
                           "Das Mietverhältnis hat noch nicht begonnen.", "OK" )
            box.exec_()
        else:
            dlg = MietverhaeltnisDialog.fromMietverhaeltnis( xmv )
            dlg.exec_()

    def createMvView( self, mobj_id:str ):
        self._mvlist = self._mvlogic.getMietverhaeltnisListe( mobj_id )
        mvlist_len = len( self._mvlist )
        if mvlist_len > 0:
            self._mv = self._mvlist[0]
            enableBrowsing = True if mvlist_len > 1 else False
            self._view = MietverhaeltnisView( self._mv, enableBrowsing=enableBrowsing )
            self._view.prevMv.connect( self.onPrevMv )
            self._view.nextMv.connect( self.onNextMv )
        else:
            box = InfoBox( "Mietverhältnis anzeigen", "Das Objekt '" + mobj_id + "' ist nicht vermietet.", "", "OK" )
            box.moveToCursor()
            box.exec_()

    def onPrevMv( self ):
        self._browse( False )

    def onNextMv( self ):
        self._browse( True )

    def _browse( self, next:bool ):
        if len( self._mvlist ) < 2:
            box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.", "Es gibt nur ein Mietverhältnis.", "OK" )
            box.moveToCursor()
            box.exec_()
            return
        idx = self._mvlist.index( self._mv )
        max = len( self._mvlist ) - 1
        if next: # "next" geklickt
            if idx == 0:
                box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.",
                               "Das jüngste Mietverhältnis wird angezeigt.", "OK" )
                box.moveToCursor()
                box.exec_()
                return
            self._mv = self._mvlist[idx-1]
            self._view.clear()
            self._view._setMietverhaeltnisData( self._mv )
        else: # "previous" geklickt
            if idx == max:
                box = InfoBox( "Blättern in Mietverhältnissen", "Blättern nicht möglich.",
                               "Das älteste Mietverhältnis wird angezeigt.", "OK" )
                box.moveToCursor()
                box.exec_()
                return
            self._mv = self._mvlist[idx+1]
            self._view.clear()
            self._view._setMietverhaeltnisData( self._mv )

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

    def getViewTitle( self ) -> str:
        title = "Mieterdaten von Mieter: " + self._mv.vorname + " " + self._mv.name
        if self._mv.name2: title += ( " und " + self._mv.vorname2 + " " + self._mv.vorname2 )
        return title

    def isChanged( self ) -> bool:
        xcopy = self._view.getMietverhaeltnisCopyWithChanges()
        return False if xcopy.equals( self._mv ) else True


#####################   MietverhaeltnisKuendigenController   #############
class MietverhaeltnisKuendigenController:
    def __init__( self ):
        self._view:MietverhaeltnisView = None
        self._mvlogic = MietverhaeltnisLogic()
        # self._mv: XMietverhaeltnis = None # das aktuell im View angezeigte Mietverhältnis

    def processKuendigung( self, mv_id:str=None ):
        if not mv_id:
            # zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
            mietobjektAuswahl = MietobjektAuswahl()
            xmo = mietobjektAuswahl.selectMietobjekt()
            if not xmo: return None
            mv_id = xmo.mv_id
        xmv:XMietverhaeltnis = self._mvlogic.getAktuellesMietverhaeltnis( mv_id )
        self.showDialog( xmv )

    def showDialog( self, xmv ):
        def validate():
            v = dlg.getDynamicAttributeView()
            xcopy:XMietverhaeltnis = v.getModifiedXBaseCopy()
            return self._mvlogic.validateKuendigungDaten( xcopy )
        xui = XBaseUI( xmv )
        vislist = (VisibleAttribute( "name_vorname", BaseEdit, "Mieter: ", editable=False, nextRow=True, columnspan=4 ),
                   VisibleAttribute( "nettomiete", FloatEdit, "Nettomiete (€): ", widgetWidth=80, editable=False, nextRow=False ),
                   VisibleAttribute( "nkv", FloatEdit, "NKV (€): ", widgetWidth=80, editable=False ),
                   VisibleAttribute( "kaution", IntEdit, "Kaution (€): ", editable=False, widgetWidth=50 ),
                   VisibleAttribute( "bis", SmartDateEdit, "Ende des Mietverhältnisses: ", widgetWidth=80 ) )
        xui.addVisibleAttributes( vislist )
        dlg = DynamicAttributeDialog( xui, "Kündigen eines Mietverhältnisses" )
        dlg.getApplyButton().setEnabled( False )
        dlg.setCallbacks( beforeAcceptCallback=validate )
        if dlg.exec_() == QDialog.Accepted:
            v = dlg.getDynamicAttributeView()
            v.updateData()  # Validierung war ok, also Übernahme der Änderungen ins XBase-Objekt
            try:
                self._mvlogic.kuendigeMietverhaeltnis( xmv )
            except Exception as ex:
                box = ErrorBox( "MietverhaeltnisKuendigenController.showDialog():\n"
                                "Fehler beim Speichern der Kündigung", str( ex ), xmv.toString( True ) )
                box.exec_()
                return
        else:
            # cancelled
            return


###################################################################################

def testKuendigen():
    app = QApplication()
    c = MietverhaeltnisKuendigenController()
    c.processKuendigung()

    app.exec_()

def test():
    app = QApplication()
    c = MietverhaeltnisController()
    c.onMietverhaeltnisShow()
    #c.showMietverhaeltnis( "pfeifer_martina" )
    # v = c.createView()
    #v.show()
    app.exec_()
#
# if __name__ == "__main__":
#     test()
