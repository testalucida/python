from PySide2.QtGui import QStandardItem
from PySide2.QtWidgets import QWidget
from abc import ABC, abstractmethod
from typing import List
import datetime
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from sonstausview import SonstigeAusgabenView
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus, XServiceLeistung
from servicetreemodel import ServiceTreeModel
import constants

class SonstAusController( MdiChildController ):
    """
    Controller für Rechnungen und Beiträge/Abgaben/Vers.prämien
    """
    def __init__( self ):
        MdiChildController.__init__( self )
        self._jahr:int = 0
        self._view:SonstigeAusgabenView = None

    def createView( self ) -> QWidget:
        sausview = SonstigeAusgabenView()
        jahre = BusinessLogic.inst().getExistingJahre( constants.einausart.MIETE )
        sausview.setJahre( jahre )
        jahr = datetime.datetime.now().year
        sausview.setBuchungsjahr( jahr )
        #sausview.setRechnungsjahr( jahr )
        self._jahr = jahr

        servicelList:List[XServiceLeistung] = BusinessLogic.inst().getServiceLeistungen()
        treemodel = ServiceTreeModel()
        kreditor = ""
        for x in servicelList:
            if x.kreditor != kreditor:
                kreditoritem = QStandardItem( x.kreditor )
                treemodel.appendRow( kreditoritem )
                kreditor = x.kreditor
            objekt = x.name  # masterobjekt.name
            if len( objekt ) > 0 and len( x.mobj_id ) > 0: objekt += "/"
            objekt += x.mobj_id
            buchungstextitem = QStandardItem( x.buchungstext + " (" + objekt + ")" )
            kreditoritem.appendRow( [buchungstextitem,] )

        sausview.setServiceTreeModel( treemodel )
        self._view = sausview
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

    def getViewTitle( self ) -> str:
        return "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )

    def save( self ):
        """
        Implementation der abstrakten Methode aus MdiChildController
        :return:
        """
        print( "ServiceController.save()" )

#################  ServiceController  ###########################
# class ServiceController( SonstAusController ):
#     """
#     Controller für Kosten, die von öffentlichen Serviceprovidern wie KEW, EVS und von den Gemeinden (Grundsteuer,...)
#     erhoben werden.
#     """
#     def __init__( self ):
#         SonstAusController.__init__( self )
#
#     def getViewTitle( self ) -> str:
#         return "Rechnungen, Abgaben, Gebühren,... " + str( self._jahr )
#
#     def save( self ):
#         """
#         Implementation der abstrakten Methode aus MdiChildController
#         :return:
#         """
#         print( "ServiceController.save()" )