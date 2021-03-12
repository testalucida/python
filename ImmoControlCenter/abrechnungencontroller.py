from PySide2.QtCore import QModelIndex, QPoint, Qt
from PySide2.QtWidgets import QWidget, QAbstractItemView, QAction, QMenu, QApplication, QSizePolicy
from typing import List, Dict
import datetime
import sys

from abrechnungentablemodel import AbrechnungenTableModel
from abrechnungenview import AbrechnungenView
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus, XSonstAusSummen, XAbrechnung
import constants
from datehelper import *
from tablecellactionhandler import TableCellActionHandler

class AbrechnungenController( MdiChildController ):
    def __init__( self ):
        MdiChildController.__init__( self )
        self._tableCellActionHandler: TableCellActionHandler = None
        curr = getCurrentYearAndMonth()
        self._jahr: int = curr["year"]
        self._title = self.getViewTitle() + str( self._jahr )
        self._view: AbrechnungenView = None
        self._tableCellActionHandler:TableCellActionHandler = None
        self._computeSumAction: QAction = QAction( "Berechne Summe" )
        self._deleteAction: QAction = QAction( "Lösche diese Abrechnung" )

    def createView( self ) -> QWidget:
        self._view = abrview = AbrechnungenView()
        abrview.setWindowTitle( self.getViewTitle() )
        jahre = self._getExistingAbrechnungsjahre()
        if not self._jahr - 1 in jahre:
            jahre.insert( 0, self._jahr - 1 )
        if not self._jahr - 2 in jahre:
            jahre.append( self._jahr - 2 )
        model = self._createModel( jahre[0] )
        abrview.setAbrechnungsjahre( jahre )
        abrview.setAbrechnungenTableModel( model )
        tv = abrview.getAbrechnungenTableView()
        tv.clicked.connect( self.onAbrechnungenLeftClick )
        tcm = TableCellActionHandler( tv )
        tcm.addAction( self._computeSumAction, self._onComputeSum )
        tcm.addAction( self._deleteAction, self._onDeleteAbrechnung )
        self._tableCellActionHandler = tcm
        abrview.setAbrechnungsjahrChangedCallback( self.onJahrChanged )
        abrview.setSubmitChangesCallback( self.onSubmitChanges )
        abrview.setSaveActionCallback( self.save )
        abrview.resize( 1050, 1000 )
        return abrview

    def getViewSize( self ) -> (int, int):
        return 1050, 1000

    def _createModel( self, jahr:int ) -> AbrechnungenTableModel:
        pass

    def _getExistingAbrechnungsjahre( self ) -> List[int]:
        pass

    def _onComputeSum( self ):
        tv = self._view.getAbrechnungenTableView()
        model: AbrechnungenTableModel = tv.model()
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

    def _onDeleteAbrechnung( self ):
        tv = self._view.getAbrechnungenTableView()
        model: AbrechnungenTableModel = tv.model()
        indexes = tv.selectedIndexes()
        rows = self._getSelectedRows( indexes )
        x:XAbrechnung = model.getXAbrechnung( rows[0] )
        model.delete( x )
        self._view.clearEditFields()
        self._view.setSaveButtonEnabled( True )
        self._setChangedFlag( True )

    def _getSelectedRows( self, indexes:List ) -> List[int]:
        rows = list()
        for idx in indexes:
            if idx.row() not in rows:
                rows.append( idx.row() )
        return rows

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
        model: AbrechnungenTableModel = self._view.getModel()
        changes: Dict[str, List[XAbrechnung]] = model.getChanges()
        self.writeChanges( changes[constants.actionList[constants.tableAction.UPDATE]] )
        #SumFieldsProvider.inst().setSumFields()
        model.resetChanges()

    def writeChanges( self, changes:List[XAbrechnung] ) -> None:
        for x in changes:
            if x.deleteFlag == True:
                try:
                    self._deleteAbrechnung( x )
                except Exception as e:
                    self._view.showException( "AbrechnungenController.writeChanges()", "deleteAbrechnung", str( e ) )
            elif x.getId() == 0:
                # insert new abrechnung
                try:
                    self._insertAbrechnung( x )
                except Exception as e:
                    self._view.showException( "AbrechnungenController.writeChanges()", "insertAbrechnung", str( e ) )
            else:
                # update existing abrechnung
                try:
                    self._updateAbrechnung( x )
                except Exception as e:
                    self._view.showException( "AbrechnungenController.writeChanges()", "updateAbrechnung", str( e ) )

        self._view.setSaveButtonEnabled( False )
        self._setChangedFlag( False )

    def _insertAbrechnung(self, x:XAbrechnung ):
        pass

    def _updateAbrechnung(self, x:XAbrechnung ):
        pass

    def _deleteAbrechnung( self, x:XAbrechnung ):
        pass

    ########################## callbacks ############################
    def onJahrChanged( self, jahr: int ):
        model = self._createModel( jahr )
        self._view.setAbrechnungenTableModel( model )

    def onAbrechnungenLeftClick( self, index: QModelIndex ):
        """
        Die Daten der ersten markierten Zeile werden zur Bearbeitung in die
        Edit-Felder übernommen.
        :param index:
        :return:
        """
        tv = self._view.getAbrechnungenTableView()
        model = tv.model()
        #val = model.data( index, Qt.DisplayRole )
        x:XAbrechnung = model.getXAbrechnung( index.row() )
        self._view.provideEditFields( x )

    def onSubmitChanges( self, x: XAbrechnung ):
        """
        wird gerufen, wenn der Anwender OK im Edit-Feld-Bereich drückt.
        Die Änderungen werden dann geprüft und in die Abrechnungen-Tabelle übernommen.
        :param x:
        :return:
        """
        msg = self._validateEditFields( x )
        if len( msg ) == 0:
            # all okay
            self._view.getAbrechnungenTableView().model().update( x )
            self._view.clearEditFields()
            self._view.setSaveButtonEnabled( True )
            self._setChangedFlag( True )
            return True
        else:
            self._view.showException( "Validation Fehler",
                                      "Falsche oder fehlende Daten bei der Erfassung der Abrechnung", msg )
            return False

    def _validateEditFields( self, x:XAbrechnung ) -> str:
        """
        Prüft die Edit-Felder.
        :param x: zu prüfendes XSonstAus-OBjekt
        :return: FEhlermeldung, wenn die Validierung nicht i.O. ist, sonst ""
        """
        if not x.buchungsdatum and not x.ab_datum:
            return "Entweder Buchungs- oder Abrechnungsdatum muss angegeben sein."
        return ""


######################################################################
class NkAbrechnungenController( AbrechnungenController ):
    def __init__( self ):
        AbrechnungenController.__init__( self )

    def getViewTitle( self ) -> str:
        return "Nebenkostenabrechnungen"

    def _createModel( self, jahr: int ) -> AbrechnungenTableModel:
        return BusinessLogic.inst().getNkAbrechnungenTableModel( jahr )

    def _getExistingAbrechnungsjahre( self ) -> List[int]:
        return BusinessLogic.inst().getExistingNkAbrechnungsjahre()

    def _insertAbrechnung(self, x:XAbrechnung ):
        BusinessLogic.inst().insertNkAbrechnung( x )

    def _updateAbrechnung(self, x:XAbrechnung ):
        BusinessLogic.inst().updateNkAbrechnung( x )

    def _deleteAbrechnung( self, x:XAbrechnung ):
        BusinessLogic.inst().deleteNkAbrechnung( x )

def test():
    app = QApplication()

    c = NkAbrechnungenController()
    v = c.createView()
    v.show()

    app.exec_()

if __name__ == "__main__":
    test()