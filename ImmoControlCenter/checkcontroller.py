from PySide2.QtWidgets import QMessageBox, QWidget
from abc import ABC, abstractmethod
from typing import List, Dict
from datehelper import *
from mdichildcontroller import MdiChildController
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic
from constants import einausart
from mdisubwindow import MdiSubWindow

class CheckController( MdiChildController, ABC ):
    def __init__(self ):
        MdiChildController.__init__( self )
        curr = getCurrentYearAndMonth()
        self._currentYear:int = curr["year"]
        self._currentCheckMonth:int = curr["month"]

    def getSelectedJahr( self ) -> int:
        return self._currentYear

    def jahrChangedCallback( self, jahr:int ):
        if jahr == self._currentYear: return
        eaart:einausart = self.getEinAusArt()
        if not BusinessLogic.inst().existsEinAusArt( eaart, jahr ):
            BusinessLogic.inst().createMtlEinAusJahresSet( jahr )
        model = self.createModel( jahr, self._currentCheckMonth )
        self._subwin.widget().setModel( model )
        self._currentYear = jahr

    @abstractmethod
    def addJahr( self, jahr:int ):
        pass

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
        model = CheckTableModel( rowlist, monat, jahr )
        model.setChangedCallback( self.onDataChanged )
        return model

    def createView( self ) -> QWidget:
        checkView = CheckView()
        checkView.saveCallback = self.onSaveData
        jahrelist = BusinessLogic.inst().getExistingJahre( einausart.MIETE )
        if len( jahrelist ) == 0:
            BusinessLogic.inst().createMtlEinAusJahresSet( self._currentYear )
            jahrelist.append( self._currentYear )
        checkView.setJahre( jahrelist )
        # neue CheckViews immer mit aktuellem Jahr/Monat
        curr = getCurrentYearAndMonth()
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
        return checkView

    def onDataChanged( self ):
        # wird vom DictListTableModel gerufen
        if self.changedCallback:
            view:CheckView = self._subwin.widget()
            view.setSaveButtonEnabled()
            self.changedCallback()  #MainContrller informieren:
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

    def addJahr( self, jahr:int ):
        self._subwin.widget().addJahr( jahr )

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

    def addJahr( self, jahr: int ):
        self._subwin.widget().addJahr( jahr )