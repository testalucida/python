from typing import List

from PySide6.QtCore import QModelIndex, QPoint
from PySide6.QtWidgets import QWidget, QApplication

from base.baseqtderivates import BaseAction, BaseDialogWithButtons, getCloseButtonDefinition
from base.basetablemodel import SumTableModel, BaseTableModel
from base.basetableview import BaseTableView
from base.basetableviewframe import BaseTableViewFrame
from base.printhandler import PrintHandler
from generictable_stuff.okcanceldialog import OkDialog
from v2.extras.cashflow.cashflowlogic import CashflowLogic, CashflowTableModel
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XMasterEinAus, XCashflow


class CashflowController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view = BaseTableView()
        self._printHandler:PrintHandler = None
        self._logic = CashflowLogic()
        self._jahr = 0
        self._dlg = None

    def createGui( self ) -> QWidget:
        """
        Brauchen wir hier nicht
        :return:
        """
        pass

    def showCashflow( self ):
        if not self._dlg:
            v:BaseTableViewFrame = self.createView()
            dlg = OkDialog( "Cashflow-Übersicht" )
            dlg.addWidget( v, 0 )
            dlg.setOkButtonText( "Schließen" )
            dlg.resize( v.getPreferredWidth()+25, 800 )
            self._dlg = dlg
        # Dialog non-modal öffnen
        self._dlg.show()

    def createView( self ) -> BaseTableViewFrame:
        model:CashflowTableModel = self._logic.getCashflowTableModel()
        v = self._view
        v.setModel( model )
        v.setAlternatingRowColors( True )
        #v.setContextMenuCallbacks( self.onProvideContext, self.onSelectedAction )
        frame = BaseTableViewFrame( v )
        frame.setWindowTitle( "Cashflow für alle Objekte" )
        # tb = frame.getToolBar()
        # tb.addExportAction( "Tabelle nach Calc exportieren", lambda: self.onExport(model) )
        # self._printHandler = PrintHandler( v )
        # tb.addPrintAction( "Druckvorschau für diese Tabelle öffnen...", self._printHandler.handlePreview )
        return frame

    def onExport( self, tm:BaseTableModel ):
        from base.exporthandler import ExportHandler
        handler = ExportHandler()
        handler.exportToCsv( tm )

    def onProvideContext( self, index:QModelIndex, point:QPoint, selectedIndexes:List[QModelIndex] ) -> List[BaseAction]:
        tm = self._view.model()
        l = list()
        col = index.column()
        x:XCashflow = tm.getElement( selectedIndexes[0].row() )
        # if col == tm.colIdxAllgKosten:
        #     action = BaseAction( "Details...", ident="allg" )
        #     action.setData( x )
        #     l.append( action )
        # elif col == tm.colIdxRep:
        #     action = BaseAction( "Details...", ident="rep" )
        #     action.setData( x )
        #     l.append( action )
        # elif col == tm.colIdxSonstKosten:
        #     action = BaseAction( "Details...", ident="sonst" )
        #     action.setData( x )
        #     l.append( action )
        return l

    def onSelectedAction( self, action:BaseAction ):

        def onClose():
            dlg.accept()

        x:XCashflow = action.data()
        title = ""
        # detail_tv = BaseTableView()
        # tvframe = BaseTableViewFrame( detail_tv )
        # tb = tvframe.getToolBar()
        # tb.addExportAction(  "Tabelle nach Calc exportieren", lambda: self.onExport(tm) )
        # tm:SumTableModel = None
        # if action.ident == "rep":
        #     tm = self._logic.getReparaturenEinzeln( x.master_name, self._jahr )
        #     title = "Reparaturen '%s' " % x.master_name + "im Detail"
        # elif action.ident == "allg":
        #     tm = self._logic.getAllgemeineKostenEinzeln( x.master_name, self._jahr )
        #     title = "Allgemeine Kosten '%s' " % x.master_name + "im Detail"
        # elif action.ident == "sonst":
        #     tm = self._logic.getSonstigeKostenEinzeln( x.master_name, self._jahr )
        #     title = "Sonstige Kosten '%s' " % x.master_name + "im Detail"
        # detail_tv.setModel( tm )
        dlg = BaseDialogWithButtons( title, getCloseButtonDefinition( onClose ) )
        # dlg.setMainWidget( tvframe )
        # dlg.resize( detail_tv.getPreferredWidth()+25, detail_tv.getPreferredHeight() + 50 )
        # dlg.exec()


def test():
    app = QApplication()
    c = CashflowController()
    v = c.createView()
    v.show()
    app.exec()

if __name__ == "__main__":
    test()