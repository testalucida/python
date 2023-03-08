from typing import Any, Dict, List

from PySide2.QtWidgets import QWidget, QApplication, QMessageBox, QMenu

from base.baseqtderivates import BaseAction
from base.messagebox import ErrorBox, QuestionBox
from screen import setScreenSize, getScreenWidth
from v2.geschaeftsreise.geschaeftsreiseeditcontroller import GeschaeftsreiseEditController
#from v2.geschaeftsreise.geschaeftsreiselogic import GeschaeftsreiseUcc
from v2.geschaeftsreise.geschaeftsreiselogic import GeschaeftsreiseLogic
from v2.geschaeftsreise.geschaeftsreisetablemodel import GeschaeftsreiseTableModel
from v2.geschaeftsreise.geschaeftsreisenview import GeschaeftsreisenView
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XGeschaeftsreise


class GeschaeftsreiseController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = GeschaeftsreiseLogic()
        self._view:GeschaeftsreisenView = None
        self._editCtrl = GeschaeftsreiseEditController()

    def getMenu( self ) -> QMenu or None:
        """
        Jeder Controller liefert ein Menu, das im MainWindow in der Menubar angezeigt wird
        :return:
        """
        menu = QMenu( "Geschäftsreisen" )
        action = BaseAction( "Geschäftsreisen anzeigen und bearbeiten...", parent=menu )
        action.triggered.connect( self.createGui )
        menu.addAction( action )
        return menu

    def createGui( self ) -> QWidget:
        try:
            jahre = self.getJahre()
            jahr = self.getYearToStartWith()
            tm:GeschaeftsreiseTableModel = self._logic.getGeschaeftsreisenTableModel( jahr )
        except Exception as ex:
            box = ErrorBox( "Fehler beim Erzeugen des GeschaeftsreiseView", str( ex ), "" )
            box.exec_()
            return None
        self._view = GeschaeftsreisenView( tm )
        self._view.setJahre( jahre )
        self._view.setJahr( jahr )
        #self._view.save.connect( self.onSave )
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
        tm: GeschaeftsreiseTableModel = self._logic.getGeschaeftsreisenTableModel( jahr )
        self._view.setModel( tm )
        tm.setSortable( True )

    def onSave( self ) -> bool:
        if self.writeChanges( self._view.getModel().getChanges() ):
           model: GeschaeftsreiseTableModel = self._view.getModel()
           model.clearChanges()
           return True
        return False

    def getChanges( self ) -> Any:
        model:GeschaeftsreiseTableModel = self._view.getModel()
        return model.getChanges()

    def writeChanges( self, changes: Any = None ) -> bool:
        changes:Dict[str, List[XGeschaeftsreise]] = self.getChanges()
        for x in changes["INSERT"]:
            try:
                self._logic.insertGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Einfügen der Geschäftsreise", str( ex ), "" )
                box.exec_()
                return False
        for x in changes["UPDATE"]:
            try:
                self._logic.updateGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Ändern der Geschäftsreise", str( ex ), "" )
                box.exec_()
                return False
        for x in changes["DELETE"]:
            try:
                self._logic.deleteGeschaeftsreise( x.reise_id )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Löschen der Geschäftsreise", str( ex ), "" )
                box.exec_()
                return False
        return True

    def clearChanges( self ) -> None:
        model:GeschaeftsreiseTableModel = self._view.getModel()
        model.clearChanges()

    @staticmethod
    def getViewTitle() -> str:
        return "Geschäftsreisen"

    def isChanged( self ) -> bool:
        model:GeschaeftsreiseTableModel = self._view.getModel()
        return model.isChanged()

    def onCreate( self ):
        editCtrl = GeschaeftsreiseEditController()
        x:XGeschaeftsreise = editCtrl.createGeschaeftsreise( self._view.getJahr() )
        if x:
            try:
                self._logic.insertGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Speichern fehlgeschlagen", str( ex ),
                                "\nAufgefangen in GeschaeftsreiseController.onCreate()")
                box.exec_()
                return
            model:GeschaeftsreiseTableModel = self._view.getModel()
            model.insert( x )

    def onEdit( self, x: XGeschaeftsreise ):
        editCtrl = GeschaeftsreiseEditController( x )
        if editCtrl.editGeschaeftsreise():
            try:
                self._logic.updateGeschaeftsreise( x )
            except Exception as ex:
                box = ErrorBox( "Speichern fehlgeschlagen", str( ex ),
                                "\nAufgefangen in GeschaeftsreiseController.onEdit()")
                box.exec_()
                return
            model: GeschaeftsreiseTableModel = self._view.getModel()
            model.update( x )

    def onDelete( self, x: XGeschaeftsreise ):
        try:
            self._logic.deleteGeschaeftsreise( x.reise_id )
        except Exception as ex:
            box = ErrorBox( "Löschen fehlgeschlagen", str( ex ),
                            "\nAufgefangen in GeschaeftsreiseController.onDelete()" )
            box.exec_()
            return
        model: GeschaeftsreiseTableModel = self._view.getModel()
        model.delete( x )


##############################  T E S T  ############################
def jahrChanged( arg ):
    print( "Jahr geändert: ", arg )

def save():
    print( "Speichern" )

def test():
    app = QApplication()
    setScreenSize( app )
    c = GeschaeftsreiseController()
    v = c.createGui()
    v.yearChanged.connect( jahrChanged )
    #v.save.connect( save )
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()