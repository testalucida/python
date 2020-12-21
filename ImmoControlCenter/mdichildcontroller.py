from abc import ABC, abstractmethod
from PySide2.QtWidgets import QWidget, QMessageBox
from typing import Any

from icctablemodel import IccTableModel
from mdisubwindow import MdiSubWindow

class MdiChildController( ABC ):
    def __init__( self ):
        self._subwin:MdiSubWindow = None
        self.changedCallback = None
        self.savedCallback = None

    @abstractmethod
    def save( self ):
        pass

    def createSubwindow( self ) -> MdiSubWindow:
        view = self.createView()
        self._subwin = MdiSubWindow()
        self._subwin.addQuitCallback( self.onCloseSubWindow )
        self._subwin.setWidget( view )
        title = self.getViewTitle()
        self._subwin.setWindowTitle( title )
        return self._subwin

    @abstractmethod
    def createView( self ) -> QWidget:
        pass

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    # @abstractmethod
    # def onCloseSubWindow( self, window: MdiSubWindow ) -> bool:
    #     pass

    def onCloseSubWindow( self,  window:MdiSubWindow ) -> bool:
        """
        wird als Callback-Funktion vom zu schließenden MdiSubWindow aufgerufen.
        Prüft, ob es am Model der View, die zu diesem Controller gehört, nicht gespeicherte
        Änderungen gibt. Wenn ja, wird der Anwender gefragt, ob er speichern möchte.
        :param window:
        :return: True, wenn keine Änderungen offen sind.
                 True, wenn zwar Änderungen offen sind, der Anwender sich aber für Speichern entschlossen hat und
                 erfolgreicht gespeichert wurde.
                 True, wenn der Anwender offene Änderungen verwirft
                 False, wenn der Anwender offene Änderungen nicht verwerfen aber auch nicht speichern will.

        """
        model: IccTableModel = self._subwin.widget().getModel()
        if model.isChanged():
            return self._askWhatToDo( model )
        return True

    def _askWhatToDo( self, model: IccTableModel ) -> bool:
        # create a modal message box that offers some choices (Yes|No|Cancel)
        box = QMessageBox()
        box.setWindowTitle( 'Nicht gespeicherte Änderung(en)' )
        box.setText( "Daten dieser Tabelle wurden geändert." )
        box.setInformativeText( "Sollen die Änderungen gespeichert werden?" )
        box.setStandardButtons( QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel )
        box.setDefaultButton( QMessageBox.Save )
        result = box.exec_()

        if result == QMessageBox.Save:
            self.writeChanges( model.getChanges() )
            return True
        elif result == QMessageBox.Discard:
            return True
        elif result == QMessageBox.Cancel:
            return False

    def writeChanges( self, changes:Any ) -> None:
        return