from abc import abstractmethod
from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog

import datehelper
from base.messagebox import ErrorBox
from v2.einaus.einausview import EinAusTableView
from v2.icc.constants import iccMonthShortNames
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccTableViewFrame, IccCheckTableViewFrame
from v2.mtleinaus.mtleinauslogic import MieteLogic, MtlEinAusTableModel, MtlEinAusLogic
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, ValueDialog, MtlZahlungEditDialog


#############  MtlEinAusController  #####################
class MtlEinAusController( IccController ):
    def __init__( self, logic:MtlEinAusLogic ):
        IccController.__init__( self )
        self._logic:MtlEinAusLogic = logic

    @abstractmethod
    def createGui( self ) -> IccCheckTableViewFrame:
        pass

    @abstractmethod
    def getTableViewFrame( self ) -> IccTableViewFrame:
        pass

    @abstractmethod
    def getModel( self ) -> MtlEinAusTableModel:
        pass

    @abstractmethod
    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        pass

    @abstractmethod
    def onSelected( self, action: QAction ):
        pass

    @abstractmethod
    def onYearChanged( self, newYear: int ):
        pass

    @abstractmethod
    def onMonthChanged( self, newMonthIdx: int, newMonthLongName: str ):
        pass

    # def getCurrentYearAndMonth( self ):
    #     return self._year, self._month

    def onBetragOk( self, index:QModelIndex ):
        model:MtlEinAusTableModel = self.getModel()
        row = index.row()
        sollVal = model.getSollValue( row )
        self._addZahlung( row, sollVal )

    def onBetragEdit( self, index: QModelIndex ):
        def editing_done( val:float, bemerkung:str ):
            self._addZahlung( index.row(), val, bemerkung )

        def onNewItem():
            print( "onNewItem" )

        def onEditItem( row:int ):
            print( "onEditItem" )

        def onDeleteItems( rowlist:List[int] ):
            print( "onDelete" )

        model = self.getModel()
        monthIdx = model.getSelectedMonthIdx()
        tm = self._logic.getZahlungenModelObjektMonat( model.getMietobjekt( index.row() ), self._year, monthIdx )
        if tm.rowCount() > 1:
            # mehrere Zahlungen führen zum angezeigten Wert.
            # Deshalb den MtlZahlungEditDialog zeigen, damit der User die Zahlung auswählen kann, die er ändern oder
            # löschen will. Er kann auch eine neue Zahlung anlegen.
            tv = EinAusTableView()
            tv.setModel( tm )
            dlg = MtlZahlungEditDialog( tv )
            tvframe = dlg.getTableViewFrame()
            tvframe.newItem.connect( onNewItem )
            tvframe.editItem.connect( onEditItem )
            tvframe.deleteItems.connect( onDeleteItems )
            dlg.exec_()
        else:
            # dem angezeigten Monatswert liegt keine oder genau eine Zahlung zugrunde,
            # deshalb können wir den "kleinen" Dialog zeigen
            dlg = ValueDialog()
            crsr = QCursor.pos()
            dlg.setCallback( editing_done )
            dlg.move( crsr.x(), crsr.y() )
            dlg.exec_()

    def _addZahlung( self, row:int, value:float, bemerkung="" ):
        model: MtlEinAusTableModel = self.getModel()
        selectedMonthIdx = model.getSelectedMonthIdx()
        selectedYear = model.getJahr()
        try:
            self._logic.addMonatsZahlung( model.getMietobjekt( row ), model.getDebiKredi( row ),
                                          selectedYear, selectedMonthIdx, value, bemerkung )
        except Exception as ex:
            box = ErrorBox( "Fehler beim Aufruf von MieteLogic.addZahlung(...) ",
                            "Exception in MtlEinAusController._addZahlung():\n" +
                            str( ex ), "" )
            box.exec_()
            return


        editColIdx = model.getEditableColumnIdx()
        model.setValue( row, editColIdx, value )


##############  MieteController  ####################
class MieteController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self, MieteLogic.inst() )
        self._tv: MieteTableView = MieteTableView()
        self._tvframe: MieteTableViewFrame = MieteTableViewFrame( self._tv )

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr, monat = self.getYearAndMonthToStartWith()
        tm = self._logic.getMietzahlungenModel( jahr, monat )
        tv = self._tv
        tv.setModel( tm )
        tb = self._tvframe.getToolBar()
        jahre = self.getJahre()
        if len(jahre) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre , self.onYearChanged )
        tb.setYear( jahr )
        tb.addMonthCombo( self.onMonthChanged )
        tb.setMonthIdx( monat )

        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        tv.okClicked.connect( self.onBetragOk )
        tv.nokClicked.connect( self.onBetragEdit )
        return self._tvframe

    def getTableViewFrame( self ) -> IccTableViewFrame:
        return self._tvframe

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        print( "context menu for column ", index.column(), ", row ", index.row() )
        l = list()
        l.append( QAction( "Action 1" ) )
        l.append( QAction( "Action 2" ) )
        sep = QAction()
        sep.setSeparator( True )
        l.append( sep )
        l.append( QAction( "Action 3" ) )
        return l

    def onSelected( self, action: QAction ):
        print( "selected action: ", str( action ) )

    def onYearChanged( self, newYear:int ):
        tm = self._logic.getMietzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
        model: MtlEinAusTableModel = self.getModel()
        model.setEditableMonth( newMonthIdx )

