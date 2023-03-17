from PySide2.QtWidgets import QMenu

from base.baseqtderivates import BaseAction
from v2.extras.ertrag.ertragcontroller import ErtragController
from v2.icc.icccontroller import IccController


class ExtrasController( IccController ):
    def __init__( self ):
        IccController.__init__( self )

    def getMenu( self ) -> QMenu or None:
        """
        Jeder Controller liefert dem MainController ein Menu, das im MainWindow in der Menubar angezeigt wird
        :return:
        """
        menu = QMenu( "Extras" )
        action = BaseAction( "Ertragsübersicht...", parent=menu )
        action.triggered.connect( self.onErtragsuebersicht )
        menu.addAction( action )
        return menu

    def onErtragsuebersicht( self ):
        ertrCtrl = ErtragController()
        v = ertrCtrl.showErtraege()