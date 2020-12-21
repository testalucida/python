from PySide2.QtCore import QModelIndex, QPoint
from PySide2.QtWidgets import QWidget, QAbstractItemView, QAction, QMenu
from typing import List, Dict
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
        self._title = "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )
        self._view:SonstigeAusgabenView = None
        self._duplicateAction:QAction = QAction( "Auszahlung duplizieren" )
        self._deleteAction:QAction = QAction( "Auszahlung löschen" )

    def createView( self ) -> QWidget:
        sausview = SonstigeAusgabenView()
        self._view = sausview
        sausview.setWindowTitle( self._title )
        jahre = BusinessLogic.inst().getExistingJahre( constants.einausart.MIETE )
        sausview.setBuchungsjahre( jahre )
        jahr = datetime.datetime.now().year
        sausview.setBuchungsjahr( jahr )
        self._jahr = jahr
        monidx, monat = BusinessLogic.inst().getLetztenMonat()
        sausview.setBuchungsdatum( 1, monat )
        masterobjekte = BusinessLogic.inst().getMasterobjekte()
        sausview.setMasterobjekte( masterobjekte )
        #kreditoren = BusinessLogic.inst().getAlleKreditoren()
        #sausview.setKreditoren( kreditoren )
        #self._provideBuchungstexte( masterobjekte[0], None, kreditoren[0] )
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
        tm.setSortable( True )
        tv.clicked.connect( self.onAuszahlungenLeftClick )
        tv.customContextMenuRequested.connect( self.onAuszahlungenRightClick )
        ## set callbacks:
        sausview.setBuchungsjahrChangedCallback( self.onBuchungsjahrChanged )
        sausview.setSaveActionCallback( self.onSave )
        sausview.setMasterobjektChangedCallback( self.onMasterobjektChanged )
        sausview.setMietobjektChangedCallback( self.onMietobjektChanged )
        sausview.setKreditorChangedCallback( self.onKreditorChanged )
        sausview.setSubmitChangesCallback( self.onSubmitChanges )

        return sausview

    def onSave( self ):
        model:SonstAusTableModel = self._view.getAuszahlungenTableView().model()
        changes:Dict[str, List[XSonstAus]] = model.getChanges()
        self.writeChanges( changes )
        model.resetChanges()

    def _dispatchSaveAction( self, actionstring:str, x:XSonstAus ):
        try:
            idx = constants.actionList.index( actionstring )
        except:
            raise Exception( "SonstAusController._dispatchSaveAction(): unknown action '%s'" % (actionstring) )
        if idx == constants.tableAction.INSERT:
            BusinessLogic.inst().insertSonstigeAuszahlung( x )
        elif idx == constants.tableAction.UPDATE:
            BusinessLogic.inst().updateSonstigeAuszahlung( x )
        elif idx == constants.tableAction.DELETE:
            BusinessLogic.inst().deleteSonstigeAuszahlung( x )
        else:
            raise Exception( "SonstAusController._dispatchSaveAction(): known but unhandled action '%s'" % (actionstring) )

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

    def onAuszahlungenRightClick( self, point: QPoint ):
        """
        Kontextmenü öffnen, wenn auf eine Zeile geklickt wurde.
        :param index:
        :return:
        """
        tv = self._view.getAuszahlungenTableView()
        index = tv.indexAt( point )
        row = index.row()
        if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
        menu = QMenu()
        menu.addAction( self._duplicateAction )
        menu.addAction( self._deleteAction )
        action = menu.exec_( tv.viewport().mapToGlobal( point ) )
        if action:
            model:SonstAusTableModel = tv.model()
            x:XSonstAus = model.getXSonstAus( row )
            if action == self._deleteAction:
                model.delete( x )
            elif action == self._duplicateAction:
                model.duplicate( x )
            self._view.setSaveButtonEnabled( True )
            self._setChangedFlag( True )
            self._view.clearEditFields()

    def onBuchungsjahrChanged( self, newjahr:int ):
        print( "SonstausController.onBuchungsjahrChanged" )

    def onMasterobjektChanged( self, newname:str ):
        #print( "SonstausController.onMasterobjektChanged: %s" % (newname,) )
        self._view.clearMietobjekte()
        mietobjekte = BusinessLogic.inst().getMietobjekte( newname )
        if len( mietobjekte ) > 0:
            self._view.setMietobjekte( mietobjekte )
        self._view.clearKreditoren()
        kreditoren = BusinessLogic.inst().getKreditoren( newname )
        if len( kreditoren ) > 0:
            self._view.setKreditoren( kreditoren )

    def onMietobjektChanged( self, mobj_id:str ):
        print( "SonstausController.onMietobjektChanged: %s" % (mobj_id,) )

    def onKreditorChanged( self, master_name:str, mobj_id:str, kreditor:str ):
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
            self._setChangedFlag( True )
        else:
            self._view.showException( "Validation Fehler", "Falsche oder fehlende Daten bei der Erfassung der Auszahlung", msg )

    def getViewTitle( self ) -> str:
        return self._title

    def _setChangedFlag( self, on:bool=True ):
        if on:
            if self._title.endswith( "*" ): return
            self._title += " *"
            if self.changedCallback:
                # MainController informieren
                self.changedCallback()
        else:
            self._title = self._title[:-2]
            if self.savedCallback:
                # Main Controller informieren
                self.savedCallback()
        self._view.setWindowTitle( self._title )

    def save( self ):
        """
        Implementation der abstrakten Methode aus MdiChildController
        :return:
        """
        print( "SonstAusController.save()" )

    def writeChanges( self, changes ) -> None:
        for actionstring, xlist in changes.items():
            for x in xlist:
                self._dispatchSaveAction( actionstring, x )
        self._view.setSaveButtonEnabled( False )
        self._setChangedFlag( False )

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