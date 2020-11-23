from abc import ABC, abstractmethod
from PySide2.QtWidgets import QMdiSubWindow
from typing import List, Dict
import datetime
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic

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

    def zeitraumChangedCallback( self, jahr:int, monat: int ):
        if jahr == self._currentYear: return

        art = self.getArt()
        if not BusinessLogic.inst().existsEinAusArt( art, jahr ):
            BusinessLogic.inst().createMtlEinAusJahresSet( art, jahr )
        model = self.createModel( jahr, monat )
        self._subwin.widget().setModel( model )

        self._currentYear = jahr
        self._currentCheckMonth = monat
        return

    def createModel( self, jahr:int, monat:int ) -> CheckTableModel:
        rowlist = self.getRowList( jahr )
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
        checkView.setZeitraumChangedCallback( self.zeitraumChangedCallback )

        self._subwin = QMdiSubWindow()
        self._subwin.setWidget( checkView )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )

        # neue CheckViews immer mit aktuellem Jahr/Monat
        curr = self.getCurrentYearAndMonth()
        checkView.setZeitraum( curr["year"], curr["month"] )
        return self._subwin

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def getArt( self ):
        pass

    @abstractmethod
    def getRowList( self, jahr:int ) -> List[Dict]:
        pass

#################### MietenController ###################
class MietenController( CheckController ):
    def __init__( self ):
        CheckController.__init__( self )

    def getViewTitle( self ) -> str:
        return "Mieteingänge " + str( self.getSelectedJahr() )

    def getArt( self ):
        return "miete"

    def getRowList( self, jahr:int ) -> List[Dict]:
        return BusinessLogic.inst().getMietzahlungen( jahr )

#################### HGVController ########################
class HGVController( CheckController ):
    def __init__( self ):
        CheckController.__init__( self )

    def getViewTitle( self ) -> str:
        return "HG-Vorauszahlungen " + str( self.getSelectedJahr() )

    def getArt( self ):
        return "hgv"

    def getRowList( self, jahr:int ) -> List[Dict]:
        return BusinessLogic.inst().getH