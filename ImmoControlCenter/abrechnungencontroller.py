from PySide2.QtCore import QModelIndex, QPoint, Qt
from PySide2.QtWidgets import QWidget, QAbstractItemView, QAction, QMenu
from typing import List, Dict
import datetime
import sys

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
        self._title = "Abrechnungen" + str( self._jahr )
        self._view: AbrechnungenView = None

    def createView( self ) -> QWidget:
        abrview = AbrechnungenView()
        jahre = BusinessLogic.ins().getExistingAbrechnungsjahre( constants.abrechnung.NK )