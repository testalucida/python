from PySide2.QtGui import QStandardItem
from PySide2.QtWidgets import QWidget
from abc import ABC, abstractmethod
from typing import List
import datetime
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from sonstausview import SonstigeAusgabenView
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus, XServiceLeistung
from servicetreemodel import ServiceTreeModel
import constants

class SonstAusController( MdiChildController ):
    """
    Controller für Rechnungen und Beiträge/Abgaben/Vers.prämien
    """
    def __init__( self ):
        MdiChildController.__init__( self )
        self._jahr:int = 0
        self._view:SonstigeAusgabenView = None

    def createView( self ) -> QWidget:
        sausview = SonstigeAusgabenView()
        self._view = sausview
        jahre = BusinessLogic.inst().getExistingJahre( constants.einausart.MIETE )
        sausview.setBuchungsjahre( jahre )
        jahr = datetime.datetime.now().year
        sausview.setBuchungsjahr( jahr )
        self._jahr = jahr
        monidx, monat = BusinessLogic.inst().getLetztenMonat()
        sausview.setBuchungsdatum( 1, monat )
        masterobjekte = BusinessLogic.inst().getMasterobjekte()
        sausview.setMasterobjekte( masterobjekte )
        kreditoren = BusinessLogic.inst().getAlleKreditoren()
        sausview.setKreditoren( kreditoren )
        self._provideBuchungstexte( masterobjekte[0], None, kreditoren[0] )
        sausview.setBuchungsjahrChangedCallback( self.onBuchungsjahrChanged )
        sausview.setMasterobjektChangedCallback( self.onMasterobjektChanged )
        sausview.setMietobjektChangedCallback( self.onMietobjektChanged )
        sausview.setKreditorChangedCallback( self.onKreditorChanged )

        return sausview

    def onBuchungsjahrChanged( self, newjahr:int ):
        print( "SonstausController.onBuchungsjahrChanged" )

    def onMasterobjektChanged( self, newname:str ):
        print( "SonstausController.onMasterobjektChanged: %s" % (newname,) )
        mietobjekte = BusinessLogic.inst().getMietobjekte( newname )
        if len( mietobjekte ) > 0:
            self._view.setMietobjekte( mietobjekte )
            #self._view.selectMietobjekt( mietobjekte[0] ) --> nein! Wir müssen die Möglichkeit haben, eine Rechnung fürs ganze Objekte zu erfassen
        kreditoren = BusinessLogic.inst().getKreditoren( newname )
        if len( kreditoren ) > 0:
            self._view.setKreditoren( kreditoren )
            self._view.selectKreditor( kreditoren[0] )

    def onMietobjektChanged( self, mobj_id:str ):
        print( "SonstausController.onMietobjektChanged: %s" % (mobj_id,) )

    def onKreditorChanged( self, master_name:str, mobj_id:str, kreditor:str ):
        print( "SonstausController.onKreditorChanged: %s, %s, %s" % (master_name, mobj_id, kreditor) )
        self._provideBuchungstexte( master_name, mobj_id, kreditor )

    def _provideBuchungstexte( self, master_name:str, mobj_id:str, kreditor:str  ):
        buchungstexte = ""
        if master_name is None or master_name == "Haus":  # kein Masterobjekt eingestellt
            buchungstexte = BusinessLogic.inst().getBuchungstexte( kreditor )
        else:
            if mobj_id:
                buchungstexte = BusinessLogic.inst().getBuchungstexteFuerMietobjekt( master_name, kreditor )
            if not buchungstexte:
                buchungstexte = BusinessLogic.inst().getBuchungstexteFuerMasterobjekt( master_name, kreditor )
        self._view.setLeistungsidentifikationen( buchungstexte )

    def onCloseSubWindow( self, window: MdiSubWindow ) -> bool:
        """
        wird als Callback-Funktion vom zu schließenden MdiSubWindow aufgerufen.
        Prüft, ob es am Model der View, die zu diesem Controller gehört, nicht gespeicherte
        Änderungen gibt. Wenn ja, wird der Anwender gefragt, ob er speichern möchte.
        :param window:
        :return: True, wenn keine Änderungen offen sind.
                 True, wenn zwar Änderungen offen sind, der Anwender sich aber für Speichern entschlossen hat und
                 erfolgreicht gespeichert wurde.
                 True, wenn der Anwender offene Änderungen verwirft
                 False, wenn der Anwender offene Änderungen nicht verwerfen aber auch nicht speichern will.

        """
        #model: CheckTableModel = self._subwin.widget().getModel()
        #i model.isChanged():
        #    return self._askWhatToDo( model )
        return True

    def getViewTitle( self ) -> str:
        return "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )

    def save( self ):
        """
        Implementation der abstrakten Methode aus MdiChildController
        :return:
        """
        print( "ServiceController.save()" )

def test():
    import sys
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication( sys.argv )
    c = SonstAusController()
    v = c.createView()
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()