from PySide2.QtWidgets import QMessageBox
from abc import ABC, abstractmethod
from typing import List, Dict
import datetime
from mdichildctrl import MdiChildController
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic
from constants import einausart
from mdisubwindow import MdiSubWindow

# class MdiChildController( ABC ):
#     def __init__( self ):
#         pass
#
#     @abstractmethod
#     def save( self ):
#         pass

class CheckController( MdiChildController, ABC ):
    def __init__(self ):
        MdiChildController.__init__( self )
        curr = self.getCurrentYearAndMonth()
        self._currentYear:int = curr["year"]
        self._currentCheckMonth:int = curr["month"]
        self._subwin: MdiSubWindow = None
        self.changedCallback = None
        self.savedCallback = None

    def getCurrentYearAndMonth( self ) -> Dict:
        d = {}
        d["month"] = datetime.datetime.now().month
        d["year"] = datetime.datetime.now().year
        return d

    def getSelectedJahr( self ) -> int:
        return self._currentYear

    def jahrChangedCallback( self, jahr:int ):
        if jahr == self._currentYear: return
        eaart:einausart = self.getEinAusArt()
        if not BusinessLogic.inst().existsEinAusArt( eaart, jahr ):
            BusinessLogic.inst().createMtlEinAusJahresSet( eaart, jahr )
        model = self.createModel( jahr, self._currentCheckMonth )
        self._subwin.widget().setModel( model )
        self._currentYear = jahr

    def monatChangedCallback( self, monat:int ):
        self._currentCheckMonth = monat
        model:CheckTableModel = self._subwin.widget().getModel()
        self.updateSollwerte( model.rowlist, self._currentYear, monat )
        model.setCheckmonat( monat )
        model.emitSollValuesChanged()

    def createModel( self, jahr:int, monat:int ) -> CheckTableModel:
        rowlist = self.getRowList( jahr, monat )
        if len( rowlist ) == 0:
            raise Exception( "Zum gewählten Jahr sind keine Daten vorhanden.",
                             'Daten sind für das aktuelle Jahr und für max. zwei zurückliegende Jahre vorhanden.' )
        model = CheckTableModel( rowlist, monat )
        model.setChangedCallback( self.onDataChanged )
        return model

    def createSubwindow( self ) -> MdiSubWindow:
        checkView = CheckView()
        checkView.saveCallback = self.onSaveData
        checkView.setJahre( BusinessLogic.inst().getExistingJahre( einausart.MIETE ) )
        # neue CheckViews immer mit aktuellem Jahr/Monat
        curr = self.getCurrentYearAndMonth()
        checkView.setJahr( self._currentYear )
        checkView.setCheckMonat( self._currentCheckMonth )
        model:CheckTableModel = self.createModel( self._currentYear, self._currentCheckMonth )
        checkView.setModel( model )
        model.setSortable( True )
        checkView.setJahrChangedCallback( self.jahrChangedCallback )
        checkView.setCheckMonatChangedCallback( self.monatChangedCallback )
        checkView.tableView.setColumnHidden( 0, True )
        checkView.tableView.setColumnHidden( 1, True )
        checkView.tableView.setColumnHidden( 2, True )
        checkView.tableView.setColumnHidden( 3, True )

        self._subwin = MdiSubWindow()
        self._subwin.addQuitCallback( self.onCloseSubWindow )
        self._subwin.setWidget( checkView )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )
        return self._subwin

    def onCloseSubWindow( self,  window:MdiSubWindow ) -> bool:
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
        model: CheckTableModel = self._subwin.widget().getModel()
        if model.isChanged():
            return self._askWhatToDo( model )
        return True

    def _askWhatToDo( self, model:CheckTableModel ) -> bool:
        # create a modal message box that offers some choices (Yes|No|Cancel)
        box = QMessageBox()
        box.setWindowTitle( 'Nicht gespeicherte Änderung(en)' )
        box.setText( "Daten dieser Tabelle wurden geändert." )
        box.setInformativeText( "Sollen die Änderungen gespeichert werden?" )
        box.setStandardButtons( QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel )
        box.setDefaultButton( QMessageBox.Save )
        result = box.exec_()

        if result == QMessageBox.Save:
            self.writeChanges( model.getChanges() )
            return True
        elif result == QMessageBox.Discard:
            return True
        elif result == QMessageBox.Cancel:
            return False

    def onDataChanged( self ):
        if self.changedCallback:
            view:CheckView = self._subwin.widget()
            view.setSaveButtonEnabled()
            self.changedCallback()
            title = self._subwin.windowTitle()
            if title[-1] != "*":
                title += " *"
                self._subwin.setWindowTitle( title )

    def onSaveData( self ): # called by save button of this view
        self.save()
        title = self._subwin.windowTitle()
        title = title.rstrip( " *" )
        self._subwin.setWindowTitle( title )

    def _doDataSavedCallback( self ):
        if self.savedCallback:
            view: CheckView = self._subwin.widget()
            view.setSaveButtonEnabled( False )
            self.savedCallback()

    def save( self ):
        model: CheckTableModel = self._subwin.widget().getModel()
        if model.isChanged():
            self.writeChanges( model.getChanges() )
            model.resetChanges()
            self._doDataSavedCallback()

    @abstractmethod
    def writeChanges( self, changes:Dict[int, Dict] ):
        pass

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def getEinAusArt( self ) -> einausart:
        pass

    @abstractmethod
    def getRowList( self, jahr:int, monat:int ) -> List[Dict]:
        pass

    @abstractmethod
    def updateSollwerte( self, rowlist:List[Dict], jahr:int, monat:int ) -> None:
        pass

#################### MietenController ###################
class MietenController( CheckController ):
    def __init__( self ):
        CheckController.__init__( self )

    def getViewTitle( self ) -> str:
        return "Mieteingänge " + str( self.getSelectedJahr() )

    def getEinAusArt( self ) -> einausart:
        return einausart.MIETE

    def getRowList( self, jahr:int, monat:int ) -> List[Dict]:
        return BusinessLogic.inst().getMietzahlungenMitSollUndSummen( jahr, monat )

    def updateSollwerte( self,  rowlist:List[Dict], jahr:int, monat:int ) -> None:
        return BusinessLogic.inst().provideSollmieten( rowlist, jahr, monat )

    def writeChanges( self, changes:Dict[int, Dict] ):
        BusinessLogic.inst().updateMietzahlungen( changes )


#################### HGVController ########################
class HGVController( CheckController ):
    def __init__( self ):
        CheckController.__init__( self )

    def getViewTitle( self ) -> str:
        return "HG-Vorauszahlungen " + str( self.getSelectedJahr() )

    def getEinAusArt( self ) -> einausart:
        return einausart.HGV

    def getRowList( self, jahr:int, monat:int ) -> List[Dict]:
        return BusinessLogic.inst().getHausgeldVorauszahlungenMitSollUndSummen( jahr, monat )

    def updateSollwerte( self,  rowlist:List[Dict], jahr:int, monat:int ) -> None:
        return BusinessLogic.inst().provideSollHGV( rowlist, jahr, monat )

    def writeChanges( self, changes:Dict[int, Dict] ):
        BusinessLogic.inst().updateHausgeldvorauszahlungen( changes )