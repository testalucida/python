from abc import ABC, abstractmethod
from PySide2.QtWidgets import QMdiSubWindow
from typing import List, Dict
import datetime
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic
from constants import einausart

# TODO wo werden die CheckViews instanziert?
# TODO hat jeder CheckView seinen eigenen Controller oder gibt es einen MietenController/HGV-Controller für
#      ALLE MietenViews/HGVViews?

class CheckController( ABC ):
    def __init__(self ):
        curr = self.getCurrentYearAndMonth()
        self._currentYear:int = curr["year"]
        self._currentCheckMonth:int = curr["month"]
        self._subwin: QMdiSubWindow = None

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
        self._subwin.widget().getModel().setCheckMonat( monat )

    def createModel( self, jahr:int, monat:int ) -> CheckTableModel:
        rowlist = self.getRowList( jahr, monat )
        if len( rowlist ) == 0:
            raise Exception( "Zum gewählten Jahr sind keine Daten vorhanden.",
                             'Daten sind für das aktuelle Jahr und für max. zwei zurückliegende Jahre vorhanden.' )

        for r in rowlist:
            r["ok"] = ""
            r["nok"] = ""
        model = CheckTableModel( rowlist, monat )
        return model

    def createSubwindow( self ) -> QMdiSubWindow:
        checkView = CheckView()
        checkView.setJahre( BusinessLogic.inst().getExistingJahre( einausart.MIETE ) )
        # neue CheckViews immer mit aktuellem Jahr/Monat
        curr = self.getCurrentYearAndMonth()
        checkView.setJahr( self._currentYear )
        checkView.setCheckMonat( self._currentCheckMonth )
        checkView.setModel( self.createModel( self._currentYear, self._currentCheckMonth ) )
        checkView.setJahrChangedCallback( self.jahrChangedCallback )
        checkView.setCheckMonatChangedCallback( self.monatChangedCallback )

        self._subwin = QMdiSubWindow()
        self._subwin.setWidget( checkView )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )
        return self._subwin

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def getEinAusArt( self ) -> einausart:
        pass

    @abstractmethod
    def getRowList( self, jahr:int, monat:int ) -> List[Dict]:
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
        return BusinessLogic.inst().getMietzahlungen( jahr, monat )

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