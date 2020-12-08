from PySide2.QtWidgets import QWidget
from abc import ABC, abstractmethod
import datetime
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from sonstausview import SonstigeAusgabenView
from mdisubwindow import MdiSubWindow
import constants

class SonstAusController( MdiChildController, ABC ):
    """
    Controller für Rechnungen und Beiträge/Abgaben/Vers.prämien
    """
    def __init__( self ):
        MdiChildController.__init__( self )
        self._jahr:int = 0

    def createView( self ) -> QWidget:
        sausview = SonstigeAusgabenView()
        jahre = BusinessLogic.inst().getExistingJahre( constants.einausart.MIETE )
        sausview.setJahre( jahre )
        jahr = datetime.datetime.now().year
        sausview.setBuchungsjahr( jahr )
        sausview.setRechnungsjahr( jahr )
        self._jahr = jahr
        return sausview

    def onCloseSubWindow( self, window: MdiSubWindow ) -> bool:
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
        #model: CheckTableModel = self._subwin.widget().getModel()
        #i model.isChanged():
        #    return self._askWhatToDo( model )
        return True


#################  ServiceController  ###########################
class ServiceController( SonstAusController ):
    """
    Controller für Kosten, die von öffentlichen Serviceprovidern wie KEW, EVS und von den Gemeinden (Grundsteuer,...)
    erhoben werden.
    """
    def __init__( self ):
        MdiChildController.__init__( self )

    def getViewTitle( self ) -> str:
        return "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )

    def save( self ):
        """
        Implementation der abstrakten Methode aus MdiChildController
        :return:
        """
        print( "ServiceController.save()" )