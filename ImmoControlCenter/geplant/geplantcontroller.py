from typing import Any

from PySide2.QtWidgets import QApplication, QWidget

from business import BusinessLogic
from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantservices import GeplantServices
from geplant.geplantview import GeplantView
from icccontroller import IccController
from interfaces import XMietverhaeltnis, XMietobjektExt
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietobjekt.mietobjektview import MietobjektView
from mietverhaeltnis.mieterwechselgui import MieterwechselView


class GeplantController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:GeplantView = None
        self._geplantModel:XBaseTableModel = None


    def createView( self ) -> QWidget:
        self._geplantModel = GeplantServices.getPlanungenModel()
        self._view = GeplantView( self._geplantModel )
        #todo: self._view.save.connect( self.writeChanges )
        return self._view

    def isChanged( self ) -> bool:
        return False
        # todo
        # changedObj = self._view.getMietobjektCopyWithChanges()
        # return False if changedObj == self._mietobjekt else True

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        self._view.clear()

    def writeChanges( self, changes:Any=None ) -> bool:
        #wird von _askWhatToDo gerufen
        # if self._validateMieterwechsel():
        #     self._view.applyChanges()
        #     try:
        #         BusinessLogic.inst().processMieterwechsel( self._mietverhaeltnisVorher.mv_id,
        #                                                    self._view.getAltesMietverhaeltnisMietEnde(),
        #                                                    self._mietverhaeltnisNachher )
        #         return True
        #     except Exception as ex:
        #         self.showErrorMessage( "Mieterwechsel: Speichern fehlgeschlagen", str( ex ) )
        #         return False
        # return False
        return True

    def getViewTitle( self ) -> str:
        return "Geplante Arbeiten"


def test():
    app = QApplication()
    c = GeplantController()
    d = c.createDialog( None )
    d.exec_()
