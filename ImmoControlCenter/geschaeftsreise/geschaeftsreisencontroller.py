from typing import Any, Dict, List

from PySide2.QtWidgets import QWidget, QApplication, QMessageBox

from business import BusinessLogic
from geschaeftsreise.geschaeftsreiseeditcontroller import GeschaeftsreiseEditController
from geschaeftsreise.geschaeftsreiselogic import GeschaeftsreiseUcc
from geschaeftsreise.geschaeftsreisentablemodel import GeschaeftsreisenTableModel
from geschaeftsreise.geschaeftsreisenview import GeschaeftsreisenView
from icc.icccontroller import IccController
from interfaces import XGeschaeftsreise
from messagebox import QuestionBox, ErrorBox
from screen import setScreenSize, getScreenWidth


class GeschaeftsreisenController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._ucc = GeschaeftsreiseUcc.inst()
        self._view:GeschaeftsreisenView = None
        self._editCtrl = GeschaeftsreiseEditController()

    def createView( self ) -> QWidget:
        try:
            jahre = GeschaeftsreiseUcc.inst().getDistinctJahre()
            jahr = jahre[0] # die Liste der Jahre muss mindestens ein Jahr (das laufende) enthalten
            tm:GeschaeftsreisenTableModel = self._ucc.getGeschaeftsreisenTableModel( jahr )
        except Exception as ex:
            box = ErrorBox( "Fehler beim Erzeugen des GeschaeftsreiseView", str( ex ), "" )
            box.exec_()
            return None

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
                    box = ErrorBox( "Fehler beim Speichern", "Speichern hat nicht funktioniert", "" )
                    box.exec_()
                else:
                    self._setNewModel( newyear )
            elif rc == QMessageBox.No: # Anwender will die Änderungen nicht speichern
                self._setNewModel( newyear )
            else:
                pass # Anwender hat Abbrechen gedrückt
        else:
            self._setNewModel( newyear )

    def _setNewModel( self, jahr:int ):
        tm: GeschaeftsreisenTableModel = self._ucc.getGeschaeftsreisenTableModel( jahr )
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
                self._ucc.insertGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Einfügen der Geschäftsreise", str( ex ) )
                box.exec_()
                return False
        for x in changes["UPDATE"]:
            try:
                self._ucc.updateGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Ändern der Geschäftsreise", str( ex ) )
                box.exec_()
                return False
        for x in changes["DELETE"]:
            try:
                self._ucc.deleteGeschaeftsreise( x.id )
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