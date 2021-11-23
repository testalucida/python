from PySide2.QtCore import QModelIndex, QPoint, Qt, QAbstractItemModel
from PySide2.QtWidgets import QWidget, QAbstractItemView, QAction, QMenu, QMessageBox
from typing import List, Dict, Any
import datetime
import sys
from business import BusinessLogic
from icccontroller import IccController
from qtderivates import TableViewDialog
from searchhandler import SearchHandler
from sonstaustablemodel import SonstAusTableModel
from sonstausview import SonstigeAusgabenView
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus, XSonstAusSummen, XBuchungstextMatch
import constants
from datehelper import *
from sumfieldsprovider import SumFieldsProvider
from tablecellactionhandler import TableCellActionHandler


class SonstAusController( IccController ):
    """
    Controller für Rechnungen und Beiträge/Abgaben/Vers.prämien
    """
    def __init__( self ):
        IccController.__init__( self )
        self._tableCellActionHandler: TableCellActionHandler = None
        self._jahr:int = 0
        self._title = ""
        self._view:SonstigeAusgabenView = None
        self._duplicateAction:QAction = QAction( "Dupliziere Auszahlung" )
        self._deleteAction:QAction = QAction( "Lösche Auszahlung" )
        self._computeSumAction:QAction = QAction( "Berechne Summe" )
        self._showSausIdAction:QAction = QAction( "Zeige SausId" )

    def createView( self ) -> QWidget:
        sausview = SonstigeAusgabenView()
        self._view = sausview
        sausview.setWindowTitle( self._title )
        jahre = BusinessLogic.inst().getExistingJahre( constants.einausart.MIETE )
        sausview.setBuchungsjahre( jahre )
        jahr = datetime.now().year
        sausview.setBuchungsjahr( jahr )
        self._adjustBuchungsjahr( jahr )
        ###self._setTitle( jahr )
        ###self._jahr = jahr
        masterobjekte = BusinessLogic.inst().getMasterobjekte()
        sausview.setMasterobjekte( masterobjekte )
        kreditoren = BusinessLogic.inst().getAlleKreditoren()
        sausview.setKreditoren( kreditoren )
        if len( kreditoren ) > 0:
            self._view.setKreditoren( kreditoren )
        sausview.setKostenarten( BusinessLogic.inst().getKostenartenLang() )
        ###sonstauslist = BusinessLogic.inst().getSonstigeAusgabenUndSummen( self._jahr )
        ###tm = SonstAusTableModel( sonstauslist )
        ###sausview.setAuszahlungenTableModel( tm )
        #sausview.setSummen( summen )
        tv = sausview.getAuszahlungenTableView()
        self._searchhandler = SearchHandler( tv )
        tcm = TableCellActionHandler( tv )
        tcm.addAction( self._computeSumAction, self._onComputeSum )
        tcm.addAction( self._duplicateAction, self._onDuplicateAuszahlung )
        tcm.addAction( self._deleteAction, self._onDeleteAuszahlung )
        tcm.addAction( self._showSausIdAction, self._onShowSausId )
        self._tableCellActionHandler = tcm

        ###tv.resizeColumnsToContents()
        ###tv.setSortingEnabled( True )  # Achtung: damit wirklich sortiert werden kann, muss die Sortierbarkeit im Model eingeschaltet werden
        ###tm.setSortable( True )
        tv.clicked.connect( self.onAuszahlungenLeftClick )
        ## set callbacks:
        sausview.setBuchungsjahrChangedCallback( self.onBuchungsjahrChanged )
        sausview.setSaveActionCallback( self.onSave )
        sausview.setSearchActionCallback( self._searchhandler.onSearch )
        sausview.setDbSearchActionCallback( self._onDbSearch )
        sausview.setMasterobjektChangedCallback( self.onMasterobjektChanged )
        sausview.setMietobjektChangedCallback( self.onMietobjektChanged )
        sausview.setKreditorChangedCallback( self.onKreditorChanged )
        sausview.setSubmitChangesCallback( self.onSubmitChanges )

        return sausview

    def _setTitle( self, jahr:int ):
        self._title = "Rechnungen, Abgaben, Gebühren,... " + str( jahr )

    def _adjustBuchungsjahr( self, jahr:int ):
        self._jahr = jahr
        self._title = "Rechnungen, Abgaben, Gebühren,... " + str( jahr )
        sonstauslist = BusinessLogic.inst().getSonstigeAusgabenUndSummen( jahr )
        tm = SonstAusTableModel( sonstauslist )
        self._view.setAuszahlungenTableModel( tm )
        tv = self._view.getAuszahlungenTableView()
        tv.resizeColumnsToContents()
        tv.setSortingEnabled( True )  # Achtung: damit wirklich sortiert werden kann, muss die Sortierbarkeit im Model eingeschaltet werden
        tm.setSortable( True )

    def _onDbSearch( self, searchstring:str ):
        def onSelected( indexes:List[QModelIndex] ):
            if len( indexes ) > 0:
                # übernehmen des selektierten XBuchungstextMatch in die Editfelder
                x: XBuchungstextMatch = matchModel.getXBuchungstextMatch( indexes[0].row() )
                self._view.provideEditFieldsPartly( (x.umlegbar > 0), x.master_id, x.master_name,
                                                    x.mobj_id, x.kreditor, x.kostenart_lang, x.buchungstext )
        matchModel = BusinessLogic.inst().getBuchungstextMatches( searchstring )
        dlg = TableViewDialog( self._view )
        dlg.setModal( True )
        dlg.getTableView().setSelectionBehavior( QAbstractItemView.SelectRows )
        dlg.setTableModel( matchModel )
        dlg.setSelectedCallback( onSelected )
        dlg.show()

    def onSave( self ):
        model:SonstAusTableModel = self._view.getAuszahlungenTableView().model()
        changes:Dict[str, List[XSonstAus]] = model.getChanges()
        self.writeChanges( changes )
        model.resetChanges()

    def onSearch( self, searchstring:str ):
        """
        wird bei jedem Drücken des Suchbuttons aufgerufen.
        Hier erfolgt der Suchvorgang und die Verwaltung der Treffer.
        :param searchstring:
        :return:
        """
        print( "SonstAusController.onSearch( %s )" %searchstring )

    def _dispatchSaveAction( self, actionstring:str, x:XSonstAus ):
        try:
            idx = constants.actionList.index( actionstring )
        except:
            self._view.showException( "Internal Error", "SonstAusController._dispatchSaveAction(): unknown action '%s'"
                                      % (actionstring)  )
            sys.exit()

        if idx == constants.tableAction.INSERT:
            try:
                BusinessLogic.inst().insertSonstigeAuszahlung( x )
            except Exception as e:
                self._view.showException( "SonstAusController._dispatchSaveAction()",
                                          "call BusinessLogic.inst().insertSonstigeAuszahlung(x)",
                                          str( e ) )
                sys.exit()
        elif idx == constants.tableAction.UPDATE:
            try:
                BusinessLogic.inst().updateSonstigeAuszahlung( x )
            except Exception as e:
                self._view.showException( "SonstAusController._dispatchSaveAction()",
                                          "call BusinessLogic.inst().updateSonstigeAuszahlung(x)",
                                          str( e ) )
                sys.exit()
        elif idx == constants.tableAction.DELETE:
            try:
                BusinessLogic.inst().deleteSonstigeAuszahlung( x )
            except Exception as e:
                self._view.showException( "SonstAusController._dispatchSaveAction()",
                                          "call BusinessLogic.inst().deleteSonstigeAuszahlung(x)",
                                          str( e ) )
                sys.exit()
        else:
            self._view.showException( "SonstAusController._dispatchSaveAction(): known but unhandled action '%s'" % (actionstring) )
            sys.exit()

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

    # def onAuszahlungenRightClick( self, point: QPoint ):
    #     """
    #     Kontextmenü öffnen, wenn auf eine Zeile geklickt wurde.
    #     :param index:
    #     :return:
    #     """
    #     tv = self._view.getAuszahlungenTableView()
    #     index = tv.indexAt( point )
    #     row = index.row()
    #     if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
    #     menu = QMenu()
    #     menu.addAction( self._duplicateAction )
    #     menu.addAction( self._deleteAction )
    #     action = menu.exec_( tv.viewport().mapToGlobal( point ) )
    #     if action:
    #         model:SonstAusTableModel = tv.model()
    #         x:XSonstAus = model.getXSonstAus( row )
    #         multiplik = -1
    #         if action == self._deleteAction:
    #             model.delete( x )
    #         elif action == self._duplicateAction:
    #             model.duplicate( x )
    #             multiplik = 1
    #         summen:XSonstAusSummen = self._view.getSummen()
    #         delta = int( round( x.betrag * multiplik ) )
    #         summen.summe_aus += delta
    #         if x.werterhaltend:
    #             summen.summe_werterhaltend += delta
    #         if x.umlegbar:
    #             summen.summe_umlegbar += delta
    #         self._view.setSummen( summen )
    #         self._view.setSaveButtonEnabled( True )
    #         self._setChangedFlag( True )
    #         self._view.clearEditFields()

    def _onComputeSum( self, action:QAction, point:QPoint ):
        tv = self._view.getAuszahlungenTableView()
        model: SonstAusTableModel = tv.model()
        indexes = tv.selectedIndexes()
        rows = self._getSelectedRows( indexes )
        valuelist = list()
        col = model.getBetragColumnIndex()
        for row in rows:
            idx = model.index( row, col )
            val = model.data( idx, Qt.DisplayRole )
            if not val: val = 0
            valuelist.append( float( val ) ) # val is in string format due to the 2 decimals
        sumval = sum( valuelist )
        self._tableCellActionHandler.showSumDialog( sumval )

    def _onShowSausId( self, action:QAction, point:QPoint ):
        tv = self._view.getAuszahlungenTableView()
        model: SonstAusTableModel = tv.model()
        indexes = tv.selectedIndexes()
        rows = self._getSelectedRows( indexes )
        msg = ""
        if len( rows ) > 1:
            msg = "Die SausId kann nur gezeigt werden, wenn nur 1 Zeile selektiert ist."
        else:
            x:XSonstAus = model.getXSonstAus( rows[0] )
            msg = str( x.saus_id )
        box = QMessageBox()
        box.setWindowTitle( "Info" )
        box.setIcon( QMessageBox.Information )
        box.setText( "SausId = %s" % (msg) )
        # box.setText( msg )
        box.exec_()

    def _getSelectedRows( self, indexes:List ) -> List[int]:
        rows = list()
        for idx in indexes:
            if idx.row() not in rows:
                rows.append( idx.row() )
        return rows

    def _onDeleteAuszahlung( self, action:QAction, point:QPoint ):
        tv = self._view.getAuszahlungenTableView()
        model: SonstAusTableModel = tv.model()
        idx = tv.selectedIndexes()[0]
        x: XSonstAus = model.getXSonstAus( idx.row() )
        model.delete( x )
        delta = int( round( x.betrag * (-1) ) )
        self._updateViewAfterDuplicateAndDelete( delta, x.werterhaltend, x.umlegbar )

    def _onDuplicateAuszahlung( self, action:QAction, point:QPoint ):
        tv = self._view.getAuszahlungenTableView()
        model: SonstAusTableModel = tv.model()
        idx = tv.selectedIndexes()[0]
        x: XSonstAus = model.getXSonstAus( idx.row() )
        xcopy:XSonstAus = model.duplicate( x )
        delta = int( round( x.betrag ) )
        self._updateViewAfterDuplicateAndDelete( delta, x.werterhaltend, x.umlegbar )
        # put copied x into edit fields for further processing
        self._view.provideEditFields( xcopy )

    def _updateViewAfterDuplicateAndDelete( self, delta:int, isWerterhaltend:bool, isUmlegbar:bool ):
        # summen: XSonstAusSummen = self._view.getSummen()
        # summen.summe_aus += delta
        # if isWerterhaltend:
        #     summen.summe_werterhaltend += delta
        # if isUmlegbar:
        #     summen.summe_umlegbar += delta
        # self._view.setSummen( summen )
        self._view.setSaveButtonEnabled( True )
        self._setChangedFlag( True )
        self._view.clearEditFields()


    def onBuchungsjahrChanged( self, newjahr:int ):
        self._adjustBuchungsjahr( newjahr )

    def onMasterobjektChanged( self, newname:str ):
        """
        User hat Masterobjekt geändert. Neue Mietobjekte-Liste holen.
        Eingestellten Kreditor und Buchungstext (Leistungsidentifikation) merken.
        Zum neuen Masterobjekte die passenden Kreditoren holen.
        Wenn in den neuen Kreditoren der vorher eingestellte Kreditor enthalten ist, diesen auswählen.
        Andernfalls eintragen.
        Vorher eingestellte Leistungsidentifikation eintragen.
        :param newname:
        :return:
        """
        self._view.clearMietobjekte()
        mietobjekte = BusinessLogic.inst().getMietobjekte( newname )
        if len( mietobjekte ) > 0:
            self._view.setMietobjekte( mietobjekte )
        # momentan eingestellten Kreditor und Leistungsidentifik. merken
        curr_kreditor = self._view.getCurrentKreditor()
        curr_leistident = self._view.getCurrentLeistungsidentifikation()
        self._view.clearKreditoren()
        kreditoren = BusinessLogic.inst().getKreditoren( newname )
        if len( kreditoren ) > 0:
            self._view.setKreditoren( kreditoren )
        if len( curr_kreditor ) > 0:
            self._view.setCurrentKreditor( curr_kreditor )
            if len( curr_leistident ) > 0:
                self._view.setCurrentLeistungsidentifikation( curr_leistident )

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

    def onSubmitChanges( self, x:XSonstAus ) -> bool:
        """
        wird gerufen, wenn der Anwender OK im Edit-Feld-Bereich drückt.
        Die Änderungen werden dann geprüft und in die Auszahlungentabelle übernommen.
        :param x:
        :return:
        """
        msg = self._validateEditFields( x )
        if len( msg ) == 0:
            # das master-objekt könnte sich geändert haben - wir ermitteln vorsichtshalber die master_id
            x.master_id = BusinessLogic.inst().getMasteridFromMastername( x.master_name )
            self._view.getAuszahlungenTableView().model().updateOrInsert( x )
            self._view.clearEditFields()
            kreditoren = BusinessLogic.inst().getAlleKreditoren()
            self._view.setKreditoren( kreditoren )
            self._view.setSaveButtonEnabled( True )
            self._setChangedFlag( True )
            return True
        else:
            self._view.showException( "Validation Fehler", "Falsche oder fehlende Daten bei der Erfassung der Auszahlung", msg )
            return False

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

    def isChanged( self ) -> bool:
        return self._view.getModel().isChanged()

    def getChanges( self ) -> Any:
        return self._view.getModel().getChanges()

    def clearChanges( self ) -> None:
        self._view.getModel().clearChanges()

    def writeChanges( self, changes ) -> bool:
        """
        wird von onSave aufgerufen. Veranlasst die Speicherung aller Änderungen.
        Ruft den SumFieldProvider auf, um die Summenfelder im MainWindow zu aktualisieren.
        :param changes:
        :return:
        """
        # todo: irgendwie ein try...except einbauen und nicht nur True zurückgeben
        for actionstring, xlist in changes.items():
            for x in xlist:
                self._dispatchSaveAction( actionstring, x )
        self._view.setSaveButtonEnabled( False )
        self._setChangedFlag( False )
        SumFieldsProvider.inst().setSumFields()
        return True

    def _validateEditFields( self, x:XSonstAus ) -> str:
        """
        Prüft die Edit-Felder.
        :param x: zu prüfendes XSonstAus-OBjekt
        :return: FEhlermeldung, wenn die Validierung nicht i.O. ist, sonst ""
        """
        if x.master_name in ( "Haus", "" ) :
            return "Kein Objektbezug angegeben. Im Zweifelsfall *unbekannt* einstellen."
        if x.kreditor == "":
            return "Kein Kreditor angegeben."
        if not x.buchungsdatum and not x.rgdatum:
            return "Entweder Buchungs- oder Rechnungsdatum muss angegeben werden."
        if x.kostenart_lang in ("", "Kostenart"): # "Kostenart" ist der Placeholder-Text
            return "Keine Kostenart angegeben."
        if x.betrag == 0:
            return "Kein Betrag angegeben."
        return ""

    # def exportToCsv( self ):
    #     model: QAbstractItemModel = self._view.getModel()
    #     try:
    #         BusinessLogic.inst().exportToCsv( model, "sonstaus" )
    #     except Exception as ex:
    #         self._view.showException( "Export SonstAus-Tabelle als .csv-Datei", str( ex ),
    #                                   "in SonstAusController.exportToCsv" )
    #         return

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