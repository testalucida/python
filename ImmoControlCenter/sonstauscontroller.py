from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QStandardItem, Qt
from PySide2.QtWidgets import QWidget, QAbstractItemView
from abc import ABC, abstractmethod
from typing import List
import datetime
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from sonstaustablemodel import SonstAusTableModel
from sonstausview import SonstigeAusgabenView
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus
import constants
import datehelper

class SonstAusController( MdiChildController ):
    """
    Controller für Rechnungen und Beiträge/Abgaben/Vers.prämien
    """
    def __init__( self ):
        MdiChildController.__init__( self )
        curr = datehelper.getCurrentYearAndMonth()
        self._jahr:int = curr["year"]
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
        sonstauslist = BusinessLogic.inst().getSonstigeAusgaben( self._jahr )
        tm = SonstAusTableModel( sonstauslist )
        sausview.setAuszahlungenTableModel( tm )
        tv = sausview.getAuszahlungenTableView()
        tv.setSelectionBehavior( QAbstractItemView.SelectRows )
        tv.setAlternatingRowColors( True )
        tv.verticalHeader().setVisible( False )
        tv.horizontalHeader().setMinimumSectionSize( 0 )
        tv.resizeColumnsToContents()
        tv.setSortingEnabled( True )  # Achtung: damit wirklich sortiert werden kann, muss die Sortierbarkeit im Model eingeschaltet werden
        tv.clicked.connect( self.onAuszahlungenLeftClick )
        tv.customContextMenuRequested.connect( self.onAuszahlungenRightClick )
        sausview.setBuchungsjahrChangedCallback( self.onBuchungsjahrChanged )
        sausview.setMasterobjektChangedCallback( self.onMasterobjektChanged )
        sausview.setMietobjektChangedCallback( self.onMietobjektChanged )
        sausview.setKreditorChangedCallback( self.onKreditorChanged )
        sausview.setSubmitChangesCallback( self.onSubmitChanges )

        return sausview

    def onAuszahlungenLeftClick( self, index: QModelIndex ):
        """
        Die Daten der ersten markierten Zeile werden zur Bearbeitung in die
        Edit-Felder übernommen.
        :param index:
        :return:
        """
        tv = self._view.getAuszahlungenTableView()
        model = tv.model()
        #val = model.data( index, Qt.DisplayRole )
        x:XSonstAus = model.getXSonstAus( index.row() )
        self._view.provideEditFields( x )
        #print( "SONSTAUSCONTROLLER: index %d/%d clicked. Value=%s" % (index.row(), index.column(), str( val )) )

    def onAuszahlungenRightClick( self, index: QModelIndex ):
        tv = self._view.getAuszahlungenTableView()
        for index in tv.selectedIndexes():
            print( "SONSTAUSCONTROLLER: cell %d/%d RIGHT clicked." % (index.row(), index.column()) )

    def onBuchungsjahrChanged( self, newjahr:int ):
        print( "SonstausController.onBuchungsjahrChanged" )

    def onMasterobjektChanged( self, newname:str ):
        print( "SonstausController.onMasterobjektChanged: %s" % (newname,) )
        self._view.clearMietobjekte()
        mietobjekte = BusinessLogic.inst().getMietobjekte( newname )
        if len( mietobjekte ) > 0:
            self._view.setMietobjekte( mietobjekte )

        #kreditoren = BusinessLogic.inst().getKreditoren( newname )
        # if len( kreditoren ) > 0:
        #     self._view.setKreditoren( kreditoren )
        #     self._view.selectKreditor( kreditoren[0] )
        self._view.resetKreditoren()

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

    def onSubmitChanges( self, x:XSonstAus ):
        """
        wird gerufen, wenn der Anwender OK im Edit-Feld-Bereich drückt.
        Die Änderungen werden dann geprüft und in die Auszahlungentabelle übernommen.
        :param x:
        :return:
        """
        msg = self._validateEditFields( x )
        if len( msg ) == 0:
            self._view.getAuszahlungenTableView().model().updateOrInsert( x )
            self._view.clearEditFields()
            self._view.setSaveButtonEnabled( True )
        else:
            self._view.showException( "Validation Fehler", "Falsche oder fehlende Daten bei der Erfassung der Auszahlung", msg )

    def getViewTitle( self ) -> str:
        return "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )

    def save( self ):
        """
        Implementation der abstrakten Methode aus MdiChildController
        :return:
        """
        print( "ServiceController.save()" )

    def _validateEditFields( self, x:XSonstAus ) -> str:
        """
        Prüft die Edit-Felder.
        :param x: zu prüfendes XSonstAus-OBjekt
        :return: FEhlermeldung, wenn die Validierung nicht i.O. ist, sonst ""
        """
        if x.master_name == "Haus":
            return "Kein Objektbezug angegeben."
        if x.kreditor == "":
            return "Kein Kreditor angegeben."
        if not x.buchungsdatum and not x.rgdatum:
            return "Entweder Buchungs- oder Rechnungsdatum muss angegeben werden."
        print( "betrag: ", x.betrag )
        if x.betrag == 0:
            return "Kein Betrag angegeben."
        return ""

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