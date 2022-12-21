from numbers import Number
from typing import List

from PySide2.QtGui import QGuiApplication

from base.baseqtderivates import SumDialog
from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView


class BaseTableFunctions:
    def __init__(self):
        pass

    def computeSumme( self, tv:BaseTableView, columnVon:int=None, columnBis:int=None ):
        """
        Addiert die in der TableView <tv> markierten Werte.
        Sind columnVon und column-Bis angegeben, werden nur Werte zwischen diesen beiden Columns (jeweils inklusive)
        berücksichtigt.
        :param tv: BaseTableView, in dem sich die selektierten Zellen befinden
        :param columnVon: Column-Index, ab dem addiert werden soll
        :param columnBis: Column-Index, bis zu dem addiert werden soll. Ist columnBis nicht angegeben, wird bis zur
        letzten Spalte addiert.
        :return:
        """
        if not columnVon and not columnBis:
            columnVon = 0
            columnBis = 999
        if columnVon and not columnBis:
            columnBis = 999
        if columnBis and columnVon is None: return
        if columnVon > columnBis: return
        model: BaseTableModel = tv.model()
        summe = 0
        idxlist = tv.selectedIndexes()
        for idx in idxlist:
            if columnVon <= idx.column() <= columnBis:
                val = model.getValue( idx.row(), idx.column() )
                if type( val ) in (int, float):
                    summe += val
        dlg = SumDialog()
        dlg.setSum( summe )
        dlg.exec_()

    def copySelectionToClipboard( self, tv:BaseTableView ):
        values: str = ""
        indexes = tv.selectedIndexes()
        model:BaseTableModel = tv.model()
        row = -1
        for idx in indexes:
            if row == -1: row = idx.row()
            if row != idx.row():
                values += "\n"
                row = idx.row()
            elif len( values ) > 0:
                values += "\t"
            val = model.getValue( idx.row(), idx.column() )
            val = " nil " if not val else val
            if isinstance( val, Number ):
                values += str( val )
            else:
                values += val
        clipboard = QGuiApplication.clipboard()
        clipboard.setText( values )