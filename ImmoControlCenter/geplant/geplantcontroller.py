from typing import Any, List

from PySide2.QtWidgets import QApplication, QWidget

from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantservices import GeplantServices
from geplant.geplantviews import GeplantView, GeplantEditDialog
from icc.iccbaseservices import IccBaseServices
from icc.icccontroller import IccController
from interfaces import XGeplant
from mietobjekt.mietobjektservices import MietobjektServices
from returnvalue import ReturnValue


class GeplantController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:GeplantView = None
        self._geplantModel:XBaseTableModel = None
        self._masterList:List[str] = self.getValueOrRaise( MietobjektServices.getMasterobjektNamen() )
        self._firmenList:List[str] = self.getValueOrRaise( IccBaseServices.getHandwerkerNachBranchen() )
        self._planungInProgress:XGeplant = None

    def createView( self ) -> QWidget:
        yearlist:List[int] = GeplantServices.getDistinctYears()
        self._geplantModel = GeplantServices.getPlanungenModel( 2022 )
        self._view = GeplantView( self._geplantModel )
        self._view.addJahre( yearlist )
        self._view.setCurrentJahr( self._geplantModel.getJahr() )
        self._view.save.connect( self.writeChanges )
        self._view.yearChanged.connect( self.onYearChanged )
        self._view.createItem.connect( self.onCreatePlanung )
        self._view.editItem.connect( self.onEditPlanung )
        self._view.deleteItem.connect( self.onDeletePlanung )
        return self._view

    def onCreatePlanung( self ):
        """
        Es wurde im GeplantView auf den Plus-Button gedrückt
        :return:
        """
        self._planungInProgress = XGeplant()
        self._showEditDialog()

    def onEditPlanung( self, x ):
        """
        Eine Planung wurde in der Tabelle der GeplantView markiert und auf den Edit-Button gedrückt.
        :param x:
        :return:
        """
        self._planungInProgress = x
        self._showEditDialog()

    def onDeletePlanung( self, x ):
        """
        Eine Planung wurde in der Tabelle der GeplantView markiert und auf den Delete-Button gedrückt
        :param x:
        :return:
        """
        self._planungInProgress = x
        raise  NotImplementedError("GeplantController.onDeletePlanung")

    def _showEditDialog( self ):
        def onOk():
            dlg.accept()
            self._planungInProgress = None
        def onCancel():
            dlg.reject()
            self._planungInProgress = None
        def onEditDialogMasterobjektChanged( newmaster ):
            mobjlist = self.getValueOrRaise( MietobjektServices.getMietobjektNamen( newmaster ) )
            dlg.clearMietobjekte()
            dlg.setMietobjekte( mobjlist )
        def onCreateHandwerker():
            print( "new Handwerker" )
        dlg = GeplantEditDialog( self._masterList, self._firmenList, self._planungInProgress )
        dlg.masterobjektChanged.connect( onEditDialogMasterobjektChanged )
        dlg.createHandwerker.connect( onCreateHandwerker )
        dlg.ok_pressed.connect( onOk )
        dlg.cancel_pressed.connect( onCancel )
        dlg.exec_()

    def isChanged( self ) -> bool:
        return False
        # todo
        # changedObj = self._view.getMietobjektCopyWithChanges()
        # return False if changedObj == self._mietobjekt else True

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        self._geplantModel.clearChanges()

    def onYearChanged( self, year:int ):
        self._geplantModel = None
        self._geplantModel = GeplantServices.getPlanungenModel( year )
        self._view.setTableModel( self._geplantModel )
        self._geplantModel.layoutChanged.emit()

    def _tryValidateAndSave( self ):
        msg = self._validate()
        if not msg:
            self.writeChanges()
        else:
            self._view.showException( "Validierungsfehler", msg )

    def _validate( self ) -> str:
        """
        Simple Validierung: Sind Pflichtfelder gefüllt?
        :return:
        """
        xgeplant = self._view.applyChanges()
        if not xgeplant.leistung: return "Es muss eine Leistung benannt werden."
        return ""

    def writeChanges( self, changes:Any=None ) -> bool:
        msg = GeplantServices.save( self._planungInProgress )

    def getViewTitle( self ) -> str:
        return "Geplante Arbeiten"


def test():
    app = QApplication()
    c = GeplantController()
    d = c.createDialog( None )
    d.exec_()
