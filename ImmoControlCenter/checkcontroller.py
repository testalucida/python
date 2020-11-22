from abc import ABC, abstractmethod
from typing import List, Dict
from checkview import CheckView
from checktablemodel import CheckTableModel
from business import BusinessLogic

class CheckController( ABC ):
    def __init__(self, view:CheckView ):
        self._currentYear:int = 0
        self._view = view

    def getView( self ) -> CheckView:
        return self._view

    def zeitraumChangedCallback( self, jahr:int, monat: int ):
        if self._currentYear == 0: self._currentYear = jahr
        else:
            if jahr == self._currentYear: return

        art = self.getArt()
        if not BusinessLogic.inst().existsEinAusArt( art, jahr ):
            BusinessLogic.inst().createMtlEinAusJahresSet( art, jahr )
        rowlist = self.getRowList( jahr )
        if len(rowlist) == 0:
            raise Exception( "Zum gewählten Jahr sind keine Daten vorhanden.",
                              'Daten sind für das aktuelle Jahr und für max. zwei zurückliegende Jahre vorhanden.' )

        for r in rowlist:
            r["ok"] = ""
            r["nok"] = ""
        model = CheckTableModel( rowlist, monat )
        self._view.setModel( model )

        self._currentYear = jahr
        return

    @abstractmethod
    def getArt( self ):
        pass

    @abstractmethod
    def getRowList( self, jahr:int ) -> List[Dict]:
        pass

#################### MietenController ###################
class MietenController( CheckController ):
    def __init__( self, view: CheckView ):
        CheckController.__init__( self, view )

    def getArt( self ):
        return "miete"

    def getRowList( self, jahr:int ) -> List[Dict]:
        return BusinessLogic.inst().getMietzahlungen( jahr )

#################### HGVController ########################
class HGVController( CheckController ):
    def __init__( self, view: CheckView ):
        CheckController.__init__( self, view )

    def getArt( self ):
        return "hgv"

    def getRowList( self, jahr:int ) -> List[Dict]:
        return BusinessLogic.inst().getH