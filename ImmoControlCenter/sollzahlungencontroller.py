import copy
from abc import abstractmethod, ABC
from enum import IntEnum
from typing import Dict, List

from PySide2.QtCore import QPoint, QModelIndex, QDate
from PySide2.QtWidgets import QAction, QWidget, QMenu, QMessageBox, QInputDialog

import constants
from business import BusinessLogic
from constants import SollType
from datehelper import getIsoStringFromQDate, addDaysToIsoString
from mdichildcontroller import MdiChildController
from qtderivates import CalendarDialog
from sollzahlungenview import SollzahlungenView, SollmietenView, SollHgvView
from sollzahlungentablemodel import SollzahlungenTableModel, SollmietenTableModel, SollHgvTableModel
from interfaces import XSollzahlung, XSollHausgeld, XSollMiete
from tablecellactionhandler import TableCellActionHandler


class SollzahlungenController( MdiChildController, ABC ):
    """
    Controller für Soll-Mieten und Soll-HG-Vorauszahlungen
    """
    def __init__( self ):
        MdiChildController.__init__( self )
        self._view:SollzahlungenView = None
        self._nextSollAction = QAction( "Folge-Soll erfassen" )
        self._tm:SollzahlungenTableModel = None
        self._newSollAction: QAction = QAction( "Dieses Soll-Intervall beenden und ein neues anlegen" )
        #self._editSollAction: QAction = QAction( "Dieses Soll-Intervall bearbeiten (Daten dieses Intervalls werden überschrieben)" )
        self._nChanges = 0
        self._editingFlag = 0
        self._sollInProcess: XSollzahlung = None
        #self._actionInProgress: QAction = None
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
            self._insertSollZahlung( xlist )
        elif idx == constants.tableAction.UPDATE:
            self._updateSollZahlung( xlist )
        else:
            raise Exception(
                "SollzahlungenController._dispatchSaveAction(): known but unhandled action '%s'" % (actionstring) )

    @abstractmethod
    def _insertSollZahlung( self, sollList:List[XSollzahlung] ):
        pass

    @abstractmethod
    def _updateSollZahlung( self, sollList: List[XSollzahlung] ):
        pass

    def createView( self ) -> QWidget:
        view = self._view = self._createView()
        view.setSubmitChangesCallback( self.onSubmitChanges )
        view.setSaveActionCallback( self.onSave )
        view.setSaveButtonEnabled( False )
        tv = view.getTableView()
        tv.clicked.connect( self.onSollTableViewLeftClick )
        tcm = TableCellActionHandler( tv )
        #tcm.addAction( self._editSollAction, self.onEditIntervalAction )
        tcm.addAction( self._newSollAction, self.onNewIntervalAction )
        #tv.customContextMenuRequested.connect( self.onSollTableViewRightClick )
        self._tm = self._createTableModel()
        view.setSollzahlungenTableModel( self._tm )
        return view

    def onEditIntervalAction( self ):
        pass

    def onNewIntervalAction( self ):
        tv = self._view.getTableView()
        idx = tv.selectedIndexes()[0]
        tm:SollzahlungenTableModel = tv.model()
        x:XSollzahlung = tm.getXSollzahlung( idx.row() )
        xnew = tm.duplicate( x )
        # todo: xnew.von mit dem Monatsende des aktuellen Monats versorgen
        xnew.von = "2021-04-01"
        self._view.clearEditFields()
        self._view.provideEditFields( xnew, editOnlyBemerkung=False )

    @abstractmethod
    def _createTableModel( self ) -> SollzahlungenTableModel:
        pass

    @abstractmethod
    def _createView( self ) -> SollzahlungenView:
        pass

    def onSave( self ):
        self.save()

    def onSollTableViewLeftClick( self, index: QModelIndex ):
        """
        Die Daten der Edit-Felder löschen
        :param index:
        :return:
        """
        self._view.clearEditFields()
        x:XSollzahlung = self._tm.getXSollzahlung( index.row() )
        self._view.provideEditFields( x, editOnlyBemerkung=True )

    def onSubmitChanges( self, soll:XSollzahlung ):
        """
        Callback function, die gerufen wird, wenn im View der Button "Submit Changes" gedrückt wird
        :param soll: das editierte Intervall
        :return:
        """
        msg = self._validateEditFields( soll )
        if not msg:
            self._tm.updateOrInsert( soll )
            self._view.clearEditFields()
            self._view.setSaveButtonEnabled( True )
            # todo: wenn soll.getId() == 0, dann liegt ein neues Intervall vor.
            #       Wir müssen das Vorgängerintervall suchen, beenden und ins ChangeLog stellen.

    @abstractmethod
    def _processEditedSollzahlung( self, x:XSollzahlung ):
        pass

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def _validateEditFields( self, soll:XSollzahlung ) -> str:
        pass

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
                    newbegin:str = addDaysToIsoString( self._terminationDate, 1 )
                    #  Edit-Fields mit passenden Werten für neuen Satz vorbelegen
                    newx = copy.copy( self._sollToTerminate )
                    newx.von = newbegin
                    newx.bis = ""
                    self._view.provideEditFields( newx )
                    self._view.setSaveButtonEnabled( True )
                    self._nChanges += 1

    # def _askForTerminationDate( self ) -> str:
    #     isodate = ""
    #     def onOk( date:QDate ):
    #         isodate = getIsoStringFromQDate( date )
    #     dlg = CalendarDialog( self._view )
    #     dlg.setTitle( "Beendigungsdatum des ausgewählten Intervalls" )
    #     dlg.setCallback( onOk )
    #     dlg.setModal( True )
    #     dlg.show()
    #     return isodate

    def _askForTerminationDate( self ) -> str:
        d = QInputDialog()
        d.show()
        return ""

    def _resetAction( self ):
        self._sollToTerminate = None
        self._terminationDate = None
        self._sollInProcess = None
        self._actionInProgress = None
        if self._nChanges > 0: self._nChanges -= 1


###################### derived Soll Controllers #################################

class SollmietenController( SollzahlungenController ):
    def __init__( self ):
        SollzahlungenController.__init__( self )

    def _createView( self ) -> SollzahlungenView:
        return SollmietenView()

    def _createTableModel( self ) -> SollzahlungenTableModel:
        # todo: alle Sollmieten holen
        tm = SollmietenTableModel()
        return tm

    def _validateEditFields( self, soll: XSollzahlung ) -> str:
        return ""

    def getViewTitle( self ) -> str:
        return "Soll-Mieten"

    def _processEditedSollzahlung( self, x:XSollzahlung ):
        pass

    def _insertSollZahlung( self, xlist:List[XSollzahlung] ):
        BusinessLogic.inst().insertSollmieten( xlist )

    def _updateSollZahlung( self, xlist: List[XSollzahlung] ):
        BusinessLogic.inst().updateSollmieten( xlist )

##############################################################

class SollHgvController( SollzahlungenController ):
    def __init__( self ):
        SollzahlungenController.__init__( self )

    def _createView( self ) -> SollzahlungenView:
        return SollHgvView()

    def _createTableModel( self ) -> SollzahlungenTableModel:
        sollHG = BusinessLogic.inst().getAlleSollHausgelder()
        tm = SollHgvTableModel( sollHG )
        return tm

    def getViewTitle( self ) -> str:
        return "Soll-Hausgelder"

    def _validateEditFields( self, soll: XSollzahlung ) -> str:
        return ""

    def _processEditedSollzahlung( self, x:XSollzahlung ):
        pass

    def _insertSollZahlung( self, xlist:List[XSollzahlung] ):
        BusinessLogic.inst().insertSollHausgelder( xlist )

    def _updateSollZahlung( self, xlist: List[XSollzahlung] ):
        BusinessLogic.inst().updateSollHausgelder( xlist )


def test():
    import sys
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication( sys.argv )
    c = SollHgvController()
    v = c.createView()
    v.setGeometry( 2000, 100, 1000, 800 )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()