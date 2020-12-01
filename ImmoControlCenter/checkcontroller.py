from abc import ABC, abstractmethod
from PySide2.QtWidgets import QMdiSubWindow
from typing import List, Dict
import datetime
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic
from constants import einausart

class MdiChildController( ABC ):
    def __init__( self ):
        pass

    @abstractmethod
    def save( self ):
        pass

class CheckController( MdiChildController, ABC ):
    def __init__(self ):
        MdiChildController.__init__( self )
        curr = self.getCurrentYearAndMonth()
        self._currentYear:int = curr["year"]
        self._currentCheckMonth:int = curr["month"]
        self._subwin: QMdiSubWindow = None
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

    def createSubwindow( self ) -> QMdiSubWindow:
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

        self._subwin = QMdiSubWindow()
        self._subwin.setWidget( checkView )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )
        return self._subwin

    def onDataChanged( self ):
        if self.changedCallback:
            view:CheckView = self._subwin.widget()
            view.setSaveButtonEnabled()
            self.changedCallback()
            title = self._subwin.windowTitle()
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
    def writeChanges( self ):
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
    def updateSollwerte( self, model:CheckTableModel, jahr:int, monat:int ) -> None:
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

    def updateSollwerte( self, model:CheckTableModel, jahr:int, monat:int ) -> None:
        return BusinessLogic.inst().provideSollmieten( model, jahr, monat )

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
        return BusinessLogic.inst().getHausgeldVorauszahlungen( jahr, monat )

    def updateSollwerte( self, model:CheckTableModel, jahr:int, monat:int ) -> None:
        pass

    def writeChanges( self, changes:Dict[int, Dict] ):
        print( "HGVController.save()")