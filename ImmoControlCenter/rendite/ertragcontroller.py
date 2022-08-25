from typing import Any, List

from PySide2.QtCore import QModelIndex, QPoint
from PySide2.QtWidgets import QWidget, QApplication

from base.baseqtderivates import BaseAction, BaseDialogWithButtons, getCloseButtonDefinition
from base.basetablemodel import SumTableModel
from base.basetableview import BaseTableView
from base.basetableviewframe import BaseTableViewFrame
from base.printhandler import PrintHandler
from business import BusinessLogic
from constants import einausart
from icc.icccontroller import IccController
from rendite.ertraguebersicht import ErtragTableModel, XMasterEinAus, ErtragLogic


class ErtragController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view = BaseTableView()
        self._printHandler:PrintHandler = None
        self._logic = ErtragLogic()
        self._jahr = 0

    def createView( self ) -> QWidget:
        busi: BusinessLogic = BusinessLogic.inst()
        jahre = busi.getExistingJahre( einausart.MIETE ) # das neueste (größte) Jahr hat Index 0
        jahr = 0
        if len( jahre ) > 0:
            if len( jahre ) > 1:
                jahr = jahre[1]  # das aktuelle minus 1 - für das liegen die Daten komplett vor
            else:
                jahr = jahre[0]
        self._jahr = jahr
        model = self._logic.getDaten( jahr )
        v = self._view
        v.setModel( model )
        v.setAlternatingRowColors( True )
        v.setContextMenuCallbacks( self.onProvideContext, self.onSelectedAction )
        frame = BaseTableViewFrame( v )
        frame.setWindowTitle( self.getViewTitle() )
        tb = frame.getToolBar()
        tb.addYearCombo( jahre, self.onChangeYear )
        tb.setYear( self._jahr )
        tb.addExportAction( "Tabelle nach Calc exportieren", self.onExport )
        self._printHandler = PrintHandler( v )
        tb.addPrintAction( "Druckvorschau für diese Tabelle öffnen...", self._printHandler.handlePreview )
        return frame

    def onChangeYear( self, newYear:int ):
        tm = self._logic.getDaten( newYear )
        self._view.setModel( tm )
        self._jahr = newYear

    def onExport( self ):
        print( "onExport")

    def onProvideContext( self, index:QModelIndex, point:QPoint, selectedIndexes:List[QModelIndex] ) -> List[BaseAction]:
        tm = self._view.model()
        l = list()
        col = index.column()
        x:XMasterEinAus = tm.getElement( selectedIndexes[0].row() )
        if col == tm.colIdxAllgKosten:
            action = BaseAction( "Details...", ident="allg" )
            action.setData( x )
            l.append( action )
        elif col == tm.colIdxRep:
            action = BaseAction( "Details...", ident="rep" )
            action.setData( x )
            l.append( action )
        elif col == tm.colIdxSonstKosten:
            action = BaseAction( "Details...", ident="sonst" )
            action.setData( x )
            l.append( action )
        return l

    def onSelectedAction( self, action:BaseAction ):
        def onClose():
            dlg.accept()

        x:XMasterEinAus = action.data()
        title = ""
        detail_tv = BaseTableView()
        tm:SumTableModel = None
        if action.ident == "rep":
            tm = self._logic.getReparaturenEinzeln( x.master_name, self._jahr )
            title = "Reparaturen '%s' " % x.master_name + "im Detail"
        elif action.ident == "allg":
            tm = self._logic.getAllgemeineKostenEinzeln( x.master_name, self._jahr )
            title = "Allgemeine Kosten '%s' " % x.master_name + "im Detail"
        elif action.ident == "sonst":
            tm = self._logic.getSonstigeKostenEinzeln( x.master_name, self._jahr )
            title = "Sonstige Kosten '%s' " % x.master_name + "im Detail"
        detail_tv.setModel( tm )
        dlg = BaseDialogWithButtons( title, getCloseButtonDefinition( onClose ) )
        dlg.setMainWidget( detail_tv )
        dlg.exec_()

    def getViewTitle( self ) -> str:
        return "Erträge der Objekte"

    def isChanged( self ) -> bool:
        return False

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        return None

    def writeChanges( self, changes:Any=None ) -> bool:
        return True

def test():
    app = QApplication()
    c = ErtragController()
    v = c.createView()
    v.show()
    app.exec_()
