from PySide2.QtCore import QModelIndex, QPoint, Qt
from PySide2.QtWidgets import QWidget, QAbstractItemView, QAction, QMenu, QApplication
from typing import List, Dict
import datetime
import sys

from abrechnungentablemodel import AbrechnungenTableModel
from abrechnungenview import AbrechnungenView
from business import BusinessLogic
from mdichildcontroller import MdiChildController
from mdisubwindow import MdiSubWindow
from interfaces import XSonstAus, XSonstAusSummen
import constants
from datehelper import *
from tablecellactionhandler import TableCellActionHandler

class AbrechnungenController( MdiChildController ):
    def __init__( self ):
        MdiChildController.__init__( self )
        self._tableCellActionHandler: TableCellActionHandler = None
        curr = getCurrentYearAndMonth()
        self._jahr: int = curr["year"]
        self._title = self.getViewTitle() + str( self._jahr )
        self._view: AbrechnungenView = None

    def createView( self ) -> QWidget:
        abrview = AbrechnungenView()
        jahre = self._getExistingAbrechnungsjahre()
        if not self._jahr - 1 in jahre:
            jahre.insert( 0, self._jahr - 1 )
        model = self._createModel( jahre[0] )
        abrview.setAbrechnungenTableModel( model )

        return abrview

    def _createModel( self, jahr:int ) -> AbrechnungenTableModel:
        pass

    def _getExistingAbrechnungsjahre( self ) -> List[int]:
        pass

    def save( self ):
        model: AbrechnungenTableModel = self._subwin.widget().getModel()

class NkAbrechnungenController( AbrechnungenController ):
    def __init__( self ):
        AbrechnungenController.__init__( self )

    def getViewTitle( self ) -> str:
        return "Nebenkostenabrechnungen"

    def _createModel( self, jahr: int ) -> AbrechnungenTableModel:
        return BusinessLogic.inst().getNkAbrechnungenTableModel( jahr )

    def _getExistingAbrechnungsjahre( self ) -> List[int]:
        return BusinessLogic.inst().getExistingNkAbrechnungsjahre()


def test():
    app = QApplication()

    c = NkAbrechnungenController()
    v = c.createView()
    v.show()

    app.exec_()

if __name__ == "__main__":
    test()