from PySide2.QtCore import Slot, QPoint
from PySide2.QtWidgets import QMessageBox, QMenu, QAction
from abc import abstractmethod
from typing import List

import datehelper
from datehelper import *
from icc.icccontroller import IccController
from checkview import CheckView, CheckTableView
from checktablemodel import CheckTableModel
from business import BusinessLogic
from constants import einausart
from icc.iccview import IccView
from messagebox import InfoBox
from mietverhaeltnis.mietverhaeltniscontroller import MietverhaeltnisController
from mietverhaeltnis.minikuendigungscontroller import MiniKuendigungsController
from sumfieldsprovider import SumFieldsProvider
from tablecellactionhandler import TableCellActionHandler


class CheckController( IccController ):
    def __init__(self ):
        IccController.__init__( self )
        self._tableContextMenu: TableCellActionHandler = None
        curr = getCurrentYearAndMonth()
        self._currentYear:int = curr["year"]
        self._currentCheckMonth:int = curr["month"]
        self._view:CheckView = None

    def getSelectedJahr( self ) -> int:
        return self._currentYear

    def jahrChangedCallback( self, jahr:int ):
        if jahr == self._currentYear: return
        eaart:einausart = self.getEinAusArt()
        if not BusinessLogic.inst().existsEinAusSet( eaart, jahr ):
            BusinessLogic.inst().createFolgejahrSet( jahr )
        model = self.createModel( jahr, self._currentCheckMonth )
        self._dlg.getView().setModel( model )
        self._currentYear = jahr

    @abstractmethod
    def addJahr( self, jahr:int ):
        pass

    def monatChangedCallback( self, monat:int ):
        self._currentCheckMonth = monat
        model:CheckTableModel = self._dlg.getView().getModel()
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

    def createView( self ) -> IccView:
        checkView = CheckView()
        checkView.saveCallback = self.onSaveData
        jahrelist = BusinessLogic.inst().getExistingJahre( einausart.MIETE )
        if len( jahrelist ) == 0:
            BusinessLogic.inst().createFolgejahrSet( self._currentYear )
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
        tv = checkView.tableView
        self._tableContextMenu = TableCellActionHandler( tv )
        self._tableContextMenu.activateComputeSumAction()
        tv.setColumnHidden( 0, True )
        tv.setColumnHidden( 1, True )
        tv.setColumnHidden( 2, True )
        tv.setColumnHidden( 3, True )
        self._view = checkView
        self.implementSpecificFeatures( tv )
        return checkView

    @abstractmethod
    def implementSpecificFeatures( self, tv:CheckTableView ):
        pass

    def onDataChanged( self ):
        # wird vom DictListTableModel gerufen
        if self.changedCallback:
            view:CheckView = self._dlg.getView()
            view.setSaveButtonEnabled()
            self.changedCallback()  #MainContrller informieren:
            title = self._dlg.windowTitle()
            if title[-1] != "*":
                title += " *"
                self._dlg.setWindowTitle( title )

    def onSaveData( self ): # called by save button of this view
        self.save()
        title = self._dlg.windowTitle()
        title = title.rstrip( " *" )
        self._dlg.setWindowTitle( title )

    def _doDataSavedCallback( self ):
        if self.savedCallback:
            view: CheckView = self._dlg.getView()
            view.setSaveButtonEnabled( False )
            self.savedCallback()

    def save( self ):
        model: CheckTableModel = self._dlg.getView().getModel()
        if model.isChanged():
            try:
                self.writeChanges( model.getChanges() )
            except Exception as ex:
                view: CheckView = self._dlg.getView()
                view.showException( "Speichern der geänderten Daten hat nicht geklappt.", str( ex ) )
                return

            model.resetChanges()
            SumFieldsProvider.inst().setSumFields()
            self._doDataSavedCallback()

    def isChanged( self ) -> bool:
        return self._view.getModel().isChanged()

    def getChanges( self ):
        return self._view.getModel().getChanges()

    def clearChanges( self ) -> None:
        self._view.getModel().clearChanges()

    @abstractmethod
    def writeChanges( self, changes ) -> bool:
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

    def writeChanges( self, changes:Dict[int, Dict] ) -> bool:
        # todo: in try...except einbetten
        BusinessLogic.inst().updateMietzahlungen( changes )
        return True

    def addJahr( self, jahr:int ):
        self._dlg.getView().addJahr( jahr )

    def implementSpecificFeatures( self, tv:CheckTableView ):
        tv.frozenRightClick.connect( self.onFrozenRightClick )

    def onFrozenRightClick( self, point:QPoint ):

        @Slot( str, str )
        def onGekuendigt( mv_id:str, datum:str ):
            #Model aktualisieren
            model.setBis( index.row(), datum )

        tv = self._view.tableView
        #model = tv.getTableModel()
        model = tv.getModel()
        index = tv.indexAt( point )
        if not index.triggerColumn() in (model.nameColumnIdx, model.sollColumnIdx):
            return

        mv_id = model.getId( index.row() )
        menu = QMenu( tv )
        if index.triggerColumn() == model.nameColumnIdx:
            action = QAction( "Dieses Mietverhältnis beenden" )
            action.setData( "K" )
            menu.addAction( action )
            menu.addSeparator()
            action2 = QAction( "Mietverhältnisdaten anzeigen" )
            action2.setData( "A" )
            menu.addAction( action2 )
        else:
            action = QAction( "Nettomiete und NKV anzeigen" )
            menu.addAction( action )
        action = menu.exec_( tv.viewport().mapToGlobal( point ) )
        if action and index.triggerColumn() == model.nameColumnIdx:
            if action.data() == "K":
                c = MiniKuendigungsController( self._view )
                c.mietverhaeltnisGekuendigt.connect( onGekuendigt )
                c.kuendigeMietverhaeltnisUsingMiniDialog( mv_id )
            else:
                self._showMietverhaeltnis( mv_id, point )
        elif action and index.triggerColumn() == model.sollColumnIdx:
            netto, nkv = BusinessLogic.inst().getNettomieteUndNkv( mv_id, self._currentYear, self._currentCheckMonth )
            box = QMessageBox()
            box.setWindowTitle( "Teile der Bruttomiete" )
            box.setIcon( QMessageBox.Information )
            box.setText( "Nettomiete:\t%.2f €\n\n"
                         "Nebenkosten:\t%.2f €" % ( netto, nkv ) )
            box.exec_()

    def _showMietverhaeltnis( self, mv_id:str, point:QPoint ):
        if datehelper.getCurrentYear() == self._currentYear:
            c = MietverhaeltnisController()
            c.showMietverhaeltnis( mv_id, point )
        else:
            box = InfoBox( "Sorry", "Mietverhältnisdaten können nur für das aktuelle Jahr angezeigt werden.", "", "OK" )
            box.exec_()

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

    def writeChanges( self, changes:Dict[int, Dict] ) -> bool:
        # todo: in try...except einbetten
        BusinessLogic.inst().updateHausgeldvorauszahlungen( changes )
        return True

    def addJahr( self, jahr: int ):
        self._dlg.getView().addJahr( jahr )

    def implementSpecificFeatures( self, tv:CheckTableView ):
        pass