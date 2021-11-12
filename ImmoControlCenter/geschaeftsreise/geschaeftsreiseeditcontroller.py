from typing import List

from business import BusinessLogic
from generictable_stuff.okcanceldialog import OkCancelDialog
from geschaeftsreise.geschaeftsreiseeditview import GeschaeftsreiseEditView
from interfaces import XGeschaeftsreise
from messagebox import ErrorBox


class GeschaeftsreiseEditController:
    def __init__( self, x:XGeschaeftsreise=None ):
        self._xgeschaeftsreise:XGeschaeftsreise = x
        self._view:GeschaeftsreiseEditView = None
        self._dlg = OkCancelDialog()
        self._mobjList:List[str] = None

    def validate( self, x: XGeschaeftsreise ) -> bool:
        msg = ""
        if not x.mobj_id: msg = "Objekt muss angegeben sein."
        if not x.von: msg = "Beginn muss angegeben sein."
        if not x.bis: msg = "Ende muss angegeben sein."
        if x.von > x.bis: msg = "Beginn muss vor dem Ende sein."
        if not x.ziel: msg = "Ziel muss angegeben sein."
        if not x.zweck: msg = "Zweck muss angegeben sein."
        if x.km <= 0: msg = "Kilometerangabe fehlt. Muss angegeben werden."
        if msg:
            box = ErrorBox( "Angaben unvollständig", msg, "" )
            box.exec_()
            return False
        return True

    def _createEditViewAndDialog( self ):
        if not self._mobjList:
            dummy, self._mobjList = BusinessLogic.inst().getAllMietobjekte()
        self._view = GeschaeftsreiseEditView( self._mobjList, self._xgeschaeftsreise )
        self._dlg = OkCancelDialog()
        self._dlg.addWidget( self._view, 1 )
        self._dlg.setValidationFunction( self.validate )
        self._dlg.setCancellationFunction( self.mayCancel )

    def validate( self ) -> bool:
        x = self._view.getDataCopyWithChanges()
        msg = ""
        if not x.mobj_id: msg = "Objekt muss angegeben sein."
        elif not x.von: msg = "Beginn muss angegeben sein."
        elif not x.bis: msg = "Ende muss angegeben sein."
        elif x.von > x.bis: msg = "Beginn muss vor dem Ende sein."
        elif not x.ziel: msg = "Ziel muss angegeben sein."
        elif not x.zweck: msg = "Zweck muss angegeben sein."
        elif x.km <= 0: msg = "Kilometerangabe fehlt. Muss angegeben werden."
        if msg:
            box = ErrorBox( "Angaben unvollständig", msg, "" )
            box.exec_()
            return False
        return True

    def mayCancel( self ) -> bool:
        return False

    def createGeschaeftsreise( self, jahr:int ) -> XGeschaeftsreise or None:
        self._xgeschaeftsreise = XGeschaeftsreise()
        self._xgeschaeftsreise.jahr = jahr
        self._createEditViewAndDialog()
        if self._dlg.exec_():
            self._view.applyChanges()
            return self._xgeschaeftsreise
        else:
            return None

    def editGeschaeftsreise( self ) -> bool:
        self._createEditViewAndDialog()
        if self._dlg.exec_():
            xcopy = self._view.getDataCopyWithChanges()
            if not self._xgeschaeftsreise.equals( xcopy ):
                self._view.applyChanges()
                return True
        return False



