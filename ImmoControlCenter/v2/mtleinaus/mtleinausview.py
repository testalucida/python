
##################  MieteTableView  ##############
from abc import abstractmethod
from typing import List, Callable

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, QModelIndex, Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog, QGridLayout, QPushButton, QApplication, QWidget, QHBoxLayout

from base.baseqtderivates import BaseEdit, BaseDialog, BaseDialogWithButtons, getOkCancelButtonDefinitions, \
    getCloseButtonDefinition
from v2.einaus.einausview import EinAusTableView, EinAusTableViewFrame, TeilzahlungDialog
from v2.icc.iccwidgets import IccTableView, IccCheckTableViewFrame
from v2.mtleinaus.mtleinauslogic import MieteTableModel, MtlEinAusTableModel


##############   MtlEinAusTableView   #################
class MtlEinAusTableView( IccTableView ):
    okClicked = Signal( QModelIndex )
    nokClicked = Signal( QModelIndex )
    def __init__( self ):
        IccTableView.__init__( self )
        self.setAlternatingRowColors( True )
        self.btvLeftClicked.connect( self.onLeftClicked )
        self._columnsWidth: List[int] = list()

    def setModel( self, model: MtlEinAusTableModel ):
        super().setModel( model, selectRows=False, singleSelection=False )
        if len( self._columnsWidth ) == 0:
            oknoksize = 30
            self.horizontalHeader().setMinimumSectionSize( oknoksize )
            self.setColumnWidth( model.getOkColumnIdx(), oknoksize )
            self.setColumnWidth( model.getNokColumnIdx(), oknoksize )
            for c in range( 0, model.columnCount() ):
                self._columnsWidth.append( self.columnWidth( c ) )
        else:
            for c in range( 0, model.columnCount() ):
                self.setColumnWidth( c, self._columnsWidth[c] )

    def onLeftClicked( self, index: QModelIndex ):
        isOkColumn, isNokColumn = False, False
        if index.column() == self.model().getOkColumnIdx():
            isOkColumn = True
            self.okClicked.emit( index )
        elif index.column() == self.model().getNokColumnIdx():
            isNokColumn = True
            self.nokClicked.emit( index )
        if True in (isOkColumn, isNokColumn):
            self.clearSelection()

##############   MieteTableView   #################
class MieteTableView( MtlEinAusTableView ):
    def __init__( self ):
        MtlEinAusTableView.__init__( self )

###############  MieteTableViewFrame  #############
class MieteTableViewFrame( IccCheckTableViewFrame ):
    def __init__( self, tableView:MieteTableView ):
        IccCheckTableViewFrame.__init__( self, tableView )

##############   HausgeldTableView   #################
class HausgeldTableView( MtlEinAusTableView ):
    def __init__( self ):
        MtlEinAusTableView.__init__( self )

###############  HausgeldTableViewFrame  #############
class HausgeldTableViewFrame( IccCheckTableViewFrame ):
    def __init__( self, tableView:MieteTableView ):
        IccCheckTableViewFrame.__init__( self, tableView )

##############   AbschlagTableView   #################
class AbschlagTableView( MtlEinAusTableView ):
    def __init__( self ):
        MtlEinAusTableView.__init__( self )

###############  AbschlagTableViewFrame  #############
class AbschlagTableViewFrame( IccCheckTableViewFrame ):
    def __init__( self, tableView:AbschlagTableView ):
        IccCheckTableViewFrame.__init__( self, tableView, withEditButtons=True )

    def _onEditItem( self ):
        """
        Der BaseTableViewFrame sendet sein edit-Signal nur, wenn die ganze Zeile selektiert ist.
        Im AbschlagTableViewFrame sind allerdings einzelne Zellen auswählbar, und der Abschlag soll bearbeitet werden
        können, egal ob die ganze Zeile oder nur eine einzelne Zelle selektiert ist.
        Deshalb müssen wir _onEditItem überschreiben.
        :return:
        """
        sel_indexes = self._tv.getSelectedIndexes()
        if len( sel_indexes ) > 0:
            row = sel_indexes[0].row()
            self.editItem.emit( row )

    def _onDeleteItems( self ):
        """
        Der BaseTableViewFrame sendet sein deleteItems-Signal nur, wenn die ganze Zeile selektiert ist.
        Im AbschlagTableViewFrame sind allerdings einzelne Zellen auswählbar, und Abschläge sollen gelöscht werden
        können, egal ob die ganze Zeile oder nur eine einzelne Zelle selektiert ist.
        Deshalb müssen wir _onDeleteItems überschreiben.
        :return:
        """
        sel_indexes = self._tv.getSelectedIndexes()
        sel_rows = list()
        for sel_idx in sel_indexes:
            row = sel_idx.row()
            sel_rows.append( row )
        if len( sel_rows ) > 0:
            self.deleteItems.emit( sel_rows )

###################  TEST   TEST   TEST   #################

def test2():
    # def validation() -> bool:
    #     #return True
    #     return False

    app = QApplication()
    dlg = TeilzahlungDialog( EinAusTableView() )
    if dlg.exec_() == QDialog.Accepted:
        print( "storing modifications")
