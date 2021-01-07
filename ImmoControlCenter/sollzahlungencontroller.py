from enum import IntEnum
from typing import Dict, List

from PySide2.QtCore import QPoint, QModelIndex, QDate
from PySide2.QtWidgets import QAction, QWidget, QMenu, QMessageBox, QInputDialog

import constants
from business import BusinessLogic
from constants import SollType
from datehelper import getIsoStringFromQDate
from mdichildcontroller import MdiChildController
from qtderivates import CalendarDialog
from sollzahlungenview import SollzahlungenView
from sollzahlungentablemodel import SollzahlungenTableModel, SollmietenTableModel, SollHGVTableModel
from interfaces import XSollzahlung, XSollHausgeld

class SollzahlungenController( MdiChildController ):
    """
    Controller für Soll-Mieten und Soll-HG-Vorauszahlungen
    """
    def __init__( self, soll_type: SollType ):
        MdiChildController.__init__( self )
        self._type:SollType = soll_type
        self._view:SollzahlungenView = None
        self._nextSollAction = QAction( "Folge-Soll erfassen" )
        self._tm:SollzahlungenTableModel = None
        self._newSollAction: QAction = QAction( "Dieses Soll-Intervall beenden und ein neues anlegen" )
        self._editSollAction: QAction = QAction( "Dieses Soll-Intervall bearbeiten (Daten dieses Intervalls werden überschrieben)" )
        self._nChanges = 0
        self._editingFlag = 0
        self._sollInProcess: XSollzahlung = None
        self._actionInProgress: QAction = None
        self._sollToTerminate:XSollzahlung

    def save( self ):
        changes: Dict[str, List] = self._tm.getChanges()
        self.writeChanges( changes )

    def writeChanges( self, changes ) -> None:
        for actionstring, xlist in changes.items():
            if len( xlist ) > 0:
                self._dispatchSaveAction( actionstring, xlist )
        self._view.setSaveButtonEnabled( False )
        self._nChanges = 0

        self._tm.resetChanges()

    def _dispatchSaveAction( self, actionstring: str, xlist: List[XSollzahlung] ):
        try:
            idx = constants.actionList.index( actionstring )
        except:
            raise Exception( "SollzahlungenController._dispatchSaveAction(): unknown action '%s'" % (actionstring) )
        if idx == constants.tableAction.INSERT:
            if self._type == SollType.MIETE_SOLL:
                BusinessLogic.inst().insertSollmieten( xlist )
            else:
                BusinessLogic.inst().insertSollHausgelder( xlist )
        elif idx == constants.tableAction.UPDATE:
            if self._type == SollType.MIETE_SOLL:
                BusinessLogic.inst().updateSollmieten( xlist )
            else:
                BusinessLogic.inst().updateSollHausgelder( xlist )
        else:
            raise Exception(
                "SollzahlungenController._dispatchSaveAction(): known but unhandled action '%s'" % (actionstring) )

    def createView( self ) -> QWidget:
        view = self._view = SollzahlungenView( self._type )
        view.setSubmitChangesCallback( self.onSubmitChanges )
        view.setSaveActionCallback( self.onSave )
        view.setSaveButtonEnabled( False )
        tv = view.getTableView()
        tv.clicked.connect( self.onSollTableViewLeftClick )
        tv.customContextMenuRequested.connect( self.onSollTableViewRightClick )
        if self._type == SollType.MIETE_SOLL:
            self._tm = SollmietenTableModel()
        else:  # SollType.HAUSGELD_SOLL
            sollHG = BusinessLogic.inst().getAlleSollHausgelder()
            self._tm = SollHGVTableModel( sollHG )
            view.setSollzahlungenTableModel( self._tm )
        return view

    def onSave( self ):
        self.save()

    def onSollTableViewLeftClick( self, index: QModelIndex ):
        """
        Die Daten der Edit-Felder löschen
        :param index:
        :return:
        """
        self._view.clearEditFields()

    def onSubmitChanges( self, soll:XSollzahlung ):
        """
        Callback function, die gerufen wird, wenn im View der Button "Submit Changes" gedrückt wird
        :param soll: das editierte oder neue Intervall
        :return:
        """
        if self._actionInProgress == self._editSollAction:
            self._tm.update( soll )
        elif self._actionInProgress == self._newSollAction:
            # zuerst das alte Soll, das wir uns gemerkt haben, stillegen
            x:XSollzahlung = self._sollToTerminate
            #x.bis = ????
            self._tm.update( x )
            #self._tm.insert( soll )
            self._sollToTerminate = None
        else:
            raise Exception( "SollzahlungenController.onSubmitChanges(): unbekannte Action: %s" % (self._actionInProgress.text() ) )
        self._view.clearEditFields()
        self._view.setSaveButtonEnabled( True )

    def getViewTitle( self ) -> str:
        return "Soll-Mieten" if self._type == SollType.MIETE_SOLL else "Soll-Hausgelder"

    def onSollTableViewRightClick( self, point: QPoint ):
        """
        Kontextmenü öffnen, wenn auf eine Zeile mit der rechten Maustaste geklickt wurde.
        :param index:
        :return:
        """
        tv = self._view.getTableView()
        index = tv.indexAt( point )
        row = index.row()
        if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
        menu = QMenu()
        menu.addAction( self._newSollAction )
        menu.addAction( self._editSollAction )
        action = menu.exec_( tv.viewport().mapToGlobal( point ) )
        if action:
            if self._editingFlag:
                # User fragen, ob Änderungen verworfen werden sollen
                # wenn JA
                self._view.clearEditFields()
                # wenn NEIN:
                #return
            # selektierten Satz aus dem Model holen:
            self._sollInProcess = self._tm.getXSollzahlung( row )
            self._actionInProgress = action
            if action == self._editSollAction:
                # selektierten Satz in die Edit-Fields übernehmen und ändern lassen
                self._view.provideEditFields( self._sollInProcess )
            elif action == self._newSollAction:
                # der selektierte Satz muss in onSubmitChanges() beendet werden, nach dem Ende-Datum fragen
                self._terminationDate = self._askForTerminationDate()
                if not self._terminationDate: # Aktion abgebrochen
                    self._resetAction()
                else:
                    # Ende-Datum und zu beendenden Satz merken
                    self._sollToTerminate =  self._tm.getXSollzahlung( row )
                    #  Edit-Fields mit passenden Werten für neuen Satz vorbelegen
                    pass
                    self._view.setSaveButtonEnabled( True )
                    self._nChanges += 1

    def _askForTerminationDate( self ) -> str:
        isodate = ""
        def onOk( date:QDate ):
            isodate = getIsoStringFromQDate( date )
        dlg = CalendarDialog( self._view )
        dlg.setTitle( "Beendigungsdatum des ausgewählten Intervalls" )
        dlg.setCallback( onOk )
        dlg.show()
        return isodate

    def _resetAction( self ):
        self._sollToTerminate = None
        self._terminationDate = None
        self._sollInProcess = None
        self._actionInProgress = None
        if self._nChanges > 0: self._nChanges -= 1

def test():
    import sys
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication( sys.argv )
    c = SollzahlungenController( SollType.HAUSGELD_SOLL )
    v = c.createView()
    v.setGeometry( 2000, 100, 1000, 800 )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()