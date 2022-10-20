from typing import List, Iterable

from PySide2.QtWidgets import QMenu, QAction

from base.baseqtderivates import BaseAction
from base.messagebox import InfoBox, ErrorBox
from v2.icc.icccontroller import IccController
from v2.icc.iccmainwindow import IccMainWindow
from v2.icc.iccwidgets import IccCheckTableViewFrame
from v2.icc.mainlogic import MainLogic
from v2.mtleinaus.mtleinauscontroller import MieteController, HausgeldController


class MainController( IccController ):
    def __init__( self, environment:str ):
        IccController.__init__( self )
        self._win:IccMainWindow = None
        self._env = environment
        self._logic:MainLogic = MainLogic()
        self._mieteCtrl = MieteController()
        self._hausgeldCtrl = HausgeldController()

    def createGui( self ) -> IccMainWindow:
        self._win = IccMainWindow( self._env )
        self._win.addMenu( self.getMenu() )
        menu = self._mieteCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )
        menu = self._hausgeldCtrl.getMenu()
        if menu:
            self._win.addMenu( menu )

        tvf:IccCheckTableViewFrame = self._mieteCtrl.createGui()
        self._win.addMieteTableViewFrame( tvf )
        tvf: IccCheckTableViewFrame = self._hausgeldCtrl.createGui()
        self._win.addHausgeldTableViewFrame( tvf )

        return self._win

    def getMenu( self ) -> QMenu:
        menu = QMenu( "ImmoCenter" )
        # Menü "Datenbank zum Server exportieren"
        action = BaseAction( "Datenbank zum Server exportieren", parent=menu )
        action.triggered.connect( self.onExportDatabase )
        menu.addAction( action )

        # Menü "Datenbank vom Server importieren"
        action = BaseAction( "Datenbank vom Server importieren", parent=menu )
        action.triggered.connect( self.onImportDatabase )
        menu.addAction( action )

        menu.addSeparator()

        # # Menüpunkt "Ende"
        action = BaseAction( "Ende", parent=menu )
        action.triggered.connect( self.onExit )
        action.setShortcut( "Alt+F4")
        menu.addAction( action )
        return menu

    def onExportDatabase( self ):
        try:
            self._logic.exportDatabaseToServer()
            box = InfoBox( "Datenbank-Export", "Export der Datenbank abgeschlossen.", "", "OK" )
            box.exec_()
        except Exception as ex:
            box = ErrorBox( "Datenbank-Export", "Export der Datenbank fehlgeschlagen.", str(ex) )
            box.exec_()

    def onImportDatabase( self ):
        try:
            self._logic.importDatabaseFromServer()
            # todo: nach Dateinamen fragen etc.
            box = InfoBox( "Datenbank-Import", "Import der Datenbank abgeschlossen.", "", "OK" )
            box.exec_()
        except Exception as ex:
            box = ErrorBox( "Datenbank-Import", "Import der Datenbank fehlgeschlagen.", str(ex) )
            box.exec_()

    def onExit( self ):
        print( "onExit" )

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = MainController( "DEVELOP" )
    win = c.createGui()
    win.show()
    app.exec_()