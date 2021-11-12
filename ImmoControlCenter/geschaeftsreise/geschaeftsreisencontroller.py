from typing import Any, Tuple, Dict, List

from PySide2.QtWidgets import QWidget, QApplication, QMessageBox, QDialog

from business import BusinessLogic
from geschaeftsreise.geschaeftsreiseeditcontroller import GeschaeftsreiseEditController
from geschaeftsreise.geschaeftsreisentablemodel import GeschaeftsreisenTableModel
from geschaeftsreise.geschaeftsreisenview import GeschaeftsreisenView
from icccontroller import IccController
from interfaces import XGeschaeftsreise
from messagebox import QuestionBox, ErrorBox
from screen import setScreenSize, getScreenWidth


class GeschaeftsreisenController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:GeschaeftsreisenView = None
        self._editCtrl = GeschaeftsreiseEditController()

    def createView( self ) -> QWidget:
        busi = BusinessLogic.inst()
        ### !!! *** TESTTESTTESTTEST  *** !!! ###
        # jahre = busi.getExistingJahre( einausart.MIETE )
        # jahr = jahre[0]
        jahre = [2020, 2021]
        jahr = jahre[1]
        ### !!! *** TESTTESTTESTTEST  *** !!! ###
        tm:GeschaeftsreisenTableModel = busi.getGeschaeftsreisenTableModel( jahr )
        self._view = GeschaeftsreisenView( tm )
        self._view.setJahre( jahre )
        self._view.setJahr( jahr )
        self._view.save.connect( self.onSave )
        self._view.yearChanged.connect( self.onYearChanged )
        self._view.createItem.connect( self.onCreate )
        self._view.editItem.connect( self.onEdit )
        self._view.deleteItem.connect( self.onDelete )

        w = self._view.getPreferredWidth()
        screenwidth = getScreenWidth()
        if w > screenwidth:
            w = screenwidth
        sz = self._view.size()
        self._view.resize( w, sz.height() )
        return self._view

    def onYearChanged( self, newyear:int ):
        if self.isChanged():
            box = QuestionBox( "Änderungen speichern?", "Sollen die Änderungen an Geschäftsreisen gespeichert werden?",
                               "Ja", "Nein", "Abbrechen" )
            rc = box.exec_()
            if rc == QMessageBox.Yes:
                if not self.onSave():
                    #title: str, msg: str, more: str
                    ErrorBox( "Fehler beim Speichern", "Speichern hat nicht funktioniert", "" )
                else:
                    self._setNewModel( newyear )
            elif rc == QMessageBox.No: # Anwender will die Änderungen nicht speichern
                self._setNewModel( newyear )
            else:
                pass # Anwender hat Abbrechen gedrückt
        else:
            self._setNewModel( newyear )

    def _setNewModel( self, jahr:int ):
        tm: GeschaeftsreisenTableModel = BusinessLogic.inst().getGeschaeftsreisenTableModel( jahr )
        self._view.setModel( tm )
        tm.setSortable( True )

    def onSave( self ) -> bool:
        if self.writeChanges( self._view.getModel().getChanges() ):
           model: GeschaeftsreisenTableModel = self._view.getModel()
           model.clearChanges()
           return True
        return False

    def getChanges( self ) -> Any:
        model:GeschaeftsreisenTableModel = self._view.getModel()
        return model.getChanges()

    def writeChanges( self, changes: Any = None ) -> bool:
        changes:Dict[str, List[XGeschaeftsreise]] = self.getChanges()
        for x in changes["INSERT"]:
            try:
                BusinessLogic.inst().insertGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Einfügen der Geschäftsreise", str( ex ) )
                box.exec_()
                return False
        for x in changes["UPDATE"]:
            try:
                BusinessLogic.inst().updateGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Ändern der Geschäftsreise", str( ex ) )
                box.exec_()
                return False
        for x in changes["DELETE"]:
            try:
                BusinessLogic.inst().deleteGeschaeftsreise( x.id )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Löschen der Geschäftsreise", str( ex ) )
                box.exec_()
                return False
        return True

    def clearChanges( self ) -> None:
        model:GeschaeftsreisenTableModel = self._view.getModel()
        model.clearChanges()

    def getViewTitle( self ) -> str:
        return "Geschäftsreisen"

    def isChanged( self ) -> bool:
        model:GeschaeftsreisenTableModel = self._view.getModel()
        return model.isChanged()

    def onCreate( self ):
        editCtrl = GeschaeftsreiseEditController()
        x:XGeschaeftsreise = editCtrl.createGeschaeftsreise( self._view.getJahr() )
        if x:
            model:GeschaeftsreisenTableModel = self._view.getModel()
            model.insert( x )

    def onEdit( self, x: XGeschaeftsreise ):
        editCtrl = GeschaeftsreiseEditController( x )
        if editCtrl.editGeschaeftsreise():
            model: GeschaeftsreisenTableModel = self._view.getModel()
            model.update( x )

    def onDelete( self, x: XGeschaeftsreise ):
        model: GeschaeftsreisenTableModel = self._view.getModel()
        model.delete( x )


##############################  T E S T  ############################
def jahrChanged( arg ):
    print( "Jahr geändert: ", arg )

def save():
    print( "Speichern" )

def test():
    app = QApplication()
    setScreenSize( app )
    c = GeschaeftsreisenController()
    v = c.createView()
    v.yearChanged.connect( jahrChanged )
    v.save.connect( save )
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()