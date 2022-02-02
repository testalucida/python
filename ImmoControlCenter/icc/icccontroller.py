from abc import ABC, abstractmethod

from PySide2.QtCore import QAbstractItemModel, QObject
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QWidget, QMessageBox
from typing import Any

from business import BusinessLogic
from icc.iccdialog import IccDialog
from returnvalue import ReturnValue


class IccControllerMeta( type(QObject), type(ABC) ):
    pass

class IccController( QObject, ABC, metaclass=IccControllerMeta ):
    def __init__( self ):
        QObject.__init__( self )
        self._dlg:IccDialog = None
        self.changedCallback = None
        self.savedCallback = None

    def createDialog( self, parent ) -> IccDialog:
        view = self.createView() # createView() wird von allen abgeleiteten Controllern implementiert
        if not view: return None
        self._dlg = IccDialog( parent )
        self._dlg.mayClose = self.mayDialogClose
        self._dlg.dialogClosing.connect( self.onDialogClosing )
        self._dlg.setView( view )
        title = self.getViewTitle()
        self._dlg.setWindowTitle( title )
        return self._dlg

    def mayDialogClose( self ) -> bool:
        """
        Umleitung von IccDialog.mayClose().
        Prüft, ob es am Model der View, die zu diesem Controller gehört, nicht gespeicherte
        Änderungen gibt. Wenn ja, wird der Anwender gefragt, ob er speichern möchte.
        :param window:
        :return: True, wenn keine Änderungen offen sind.
                 True, wenn zwar Änderungen offen sind, der Anwender sich aber für Speichern entschlossen hat und
                 erfolgreicht gespeichert wurde.
                 True, wenn der Anwender offene Änderungen verwirft
                 False, wenn der Anwender offene Änderungen nicht verwerfen aber auch nicht speichern will.
                 Bei der Rückgabe von True wird der Dialog geschlossen, bei False nicht.
        """
        if not self._dlg: # Dialog schon geschlossen, unnötige Anfrage vom MainController
            return True
        v = self._dlg.getView()
        if v.isChanged():
            return self._askWhatToDo()
        # if self.isChanged():
        #     return self._askWhatToDo()
        return True

    def onDialogClosing( self ):
        # der Dialog wird geschlossen, jetzt hält ihn nichts mehr auf.
        # Wir wissen hier nicht, ob der Anwender "Speichern" oder "Schließen ohne Speichern" gewählt hat.
        # Deshalb löchen wir vorsichtshalber die changes.
        #model: IccTableModel = self._dlg.getView().getModel()
        self.clearChanges()
        self._dlg = None

    def _askWhatToDo( self ) -> bool:
        # create a modal message box that offers some choices (Yes|No|Cancel)
        title = self._dlg.windowTitle()
        if title.endswith( "*" ):
            title = title[:-1]
            title = title.rstrip()
        box = QMessageBox( self._dlg )
        box.setWindowTitle( "Nicht gespeicherte Änderung(en)" )
        box.setText( "Daten im Dialog '%s' wurden geändert." % title )
        box.setInformativeText( "Sollen die Änderungen gespeichert werden?" )
        box.setStandardButtons( QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel )
        box.setDefaultButton( QMessageBox.Save )
        # crsr = QCursor.pos()
        # box.move( crsr.x(), crsr.y() )
        result = box.exec_()

        if result == QMessageBox.Save:
            return self.writeChanges( self.getChanges() )
        elif result == QMessageBox.Discard:
            return True
        elif result == QMessageBox.Cancel:
            return False

    def showErrorMessage( self, title:str, msg:str ):
        box = QMessageBox( QMessageBox.Critical, title, msg )
        crsr = QCursor.pos()
        box.move( crsr.x(), crsr.y() )
        box.exec_()

    def showWarningMessage( self, title:str, msg:str ):
        box = QMessageBox( QMessageBox.Warning, title, msg )
        box.exec_()

    def getValueOrRaise( self, rv:ReturnValue ) -> Any or None:
        """
        Wertet das übergebene ReturnValue-Objekt aus.
        Wenn es eine Exception wrappt, wird eine Exception geworfen und None zurückgegeben.
        Ist ein regulärer Wert enthalten, wird dieser zurückgegeben.
        :param rv:
        :return:
        """
        if rv.missionAccomplished(): # alles okay
            return rv.returnvalue
        else:
            self.showErrorMessage( rv.exceptiontype, rv.errormessage )
            return None

    @abstractmethod
    def createView( self ) -> QWidget:
        pass

    @abstractmethod
    def getChanges( self ) -> Any:
        pass

    @abstractmethod
    def writeChanges( self, changes:Any=None ) -> bool:
        #wird von _askWhatToDo gerufen
        # bei Rückgabe von True wird der Dialog geschlossen
        pass

    @abstractmethod
    def clearChanges( self ) -> None:
        pass

    @abstractmethod
    def getViewTitle( self ) -> str:
        pass

    @abstractmethod
    def isChanged( self ) -> bool:
        pass


