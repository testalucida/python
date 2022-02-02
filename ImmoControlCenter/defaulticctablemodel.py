from functools import cmp_to_key
from typing import Any, List, Dict

from PySide2.QtCore import QModelIndex, Qt, Signal
from PySide2.QtGui import QBrush, QFont
from PySide2.QtWidgets import QTableView

import constants
from icc.icctablemodel import IccTableModel
from interfaces import XBase


class DefaultIccTableModel( IccTableModel ):
    """
    TableModel, das eine Liste von XBase-Objekten in Empfang nimmt.
    Alle Methoden, die die QTableView zum Anzeigen benötigt, sind implementiert (rowcount, columncount, data, ...)
    Per Default werden Strings linksbündig, numerische Werte rechtsbündig angezeigt.
    Negative Zahlen werden in Rot dargestellt. (Dies kann derzeit nicht geändert werden.)
    Geänderte, aber noch nicht gespeicherte Zeilen werden in Gelb dargestellt.
    Methoden zum Sortieren und Ändern sind enthalten.
    Die Sortierbarkeit muss vor dem Sortieren auf True geschaltet werden setSortable( True ).
    (Außerdem muss in der QTableView setSortingEnabled( True ) aufgerufen werden.)
    """
    sortingFinished = Signal()
    def __init__( self, xbaselist:List[XBase] ):
        IccTableModel.__init__( self )
        self._xbaseList = xbaselist
        self._keyHeaderMapper = dict()
        self._headers = list()
        self._changes: Dict[str, List[XBase]] = { }
        self._numColumns:List[int] = list()
        self._sortable = False
        self._sort_col = 0
        self._sort_reverse = False
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._prepareChangeDictionary()
        self._createDefaultKeyHeaderMappings()

    def _prepareChangeDictionary( self ):
        for s in constants.actionList:
            self._changes[s] = list()

    def _createDefaultKeyHeaderMappings( self ):
        """
        Damit wir vernünftige Werte in self._keyHeaderMapper und in self._headers haben,
        wenn self.setKeyHeaderMappings *nicht* aufgerufen wird
        :return:
        """
        if len( self._xbaseList ) == 0: return
        x = self._xbaseList[0]
        for key in x.__dict__.keys():
            self._keyHeaderMapper[key] = key
            self._headers.append( key )

    def setKeyHeaderMappings( self, keyheaderdict:Dict[str, str] ):
        """
        Setzt die Zuordnung von Keys zu Header-Namen, in der Form "Nachname": "name"
        In der TableView, der dieses Model übergeben wird, werden so viele Spalten
        angezeigt, wie keyheaderdict Einträge (keys) hat.
        Wird diese Zuordnung nicht gesetzt, werden in der TableView so viele Spalten
        angezeigt, wie in der Liste, die bei Instanzierung übergeben wurde, Elemente enthalten sind.
        :return:
        """
        self._keyHeaderMapper.clear()
        self._headers.clear()
        self._keyHeaderMapper = keyheaderdict
        self._headers = list( self._keyHeaderMapper.keys() )

    def setNumColumnsIndexes( self, intlist:List[int] ):
        self._numColumns = intlist

    ###############  Methoden, die Informationen zur Liste liefern  ################
    def isNumColumn( self, idx:int ) -> bool:
        return idx in self._numColumns

    def rowCount( self, parent: QModelIndex = None ) -> int:
        return len( self._xbaseList )

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    ##################  DISPLAY - FUNKTIONALITÄT  ##############
    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            return self.getAlignment( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForeground( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        elif role == Qt.BackgroundRole:
            return self.getBackground( index.row(), index.column() )
        return None

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.getHeaders()[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

    def getHeaders( self ) -> List[str]:
        return self._headers

    def getAlignment( self, indexrow: int, indexcolumn: int ) -> int:
        """
        Gibt für str-Werte Links / vertical centered zurück und für
        numerische Werte Rechts / vertical centered
        Die Align-Werte werden als Integer zurückgegeben.
        :param indexrow:
        :param indexcolumn:
        :return:
        """
        if self.isNumColumn( indexcolumn ):
            return int( Qt.AlignRight | Qt.AlignVCenter )
        return int( Qt.AlignLeft | Qt.AlignVCenter )

    def getForeground( self, indexrow: int, indexcolumn: int ) -> Any:
        return None

    def getFont( self, indexrow: int, indexcolumn: int ) -> Any:
        return None

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._xbaseList[indexrow]
        header = self._headers[indexcolumn]
        key = self._keyHeaderMapper.get( header )
        val = x.__dict__[key]
        return val

    def getBackground( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self.getXBaseObject( indexrow )
        if self.isXBaseInsertedOrUpdatedOrDeleted( x ):
            return self._yellowBrush
        return None

    def getXBaseObject( self, row:int ) -> XBase:
        return self._xbaseList[row]

    def getRow( self, x:XBase ):
        return self._xbaseList.index( x )

    #################  ÄNDERUNGEN AN DER XBASE-LISTE  #############
    def insert( self, x: XBase ):
        self._xbaseList.append( x )
        self._writeChangeLog( constants.tableAction.INSERT, x )
        self.layoutChanged.emit()

    def update( self, x: XBase ):
        l = self._xbaseList
        cols = len( self.getHeaders() )
        row = self.getRow( x )
        idxfrom = self.index( row, 0 )
        idxbis = self.index( row, cols - 1 )
        if not self._isInChangeLog( x, constants.tableAction.INSERT ):
            self._writeChangeLog( constants.tableAction.UPDATE, x )
        self.dataChanged.emit( idxfrom, idxbis )

    def delete( self, x: XBase ) -> None:
        self._xbaseList.remove( x )
        self._writeChangeLog( constants.tableAction.DELETE, x )
        self.layoutChanged.emit()

    ############ Methoden, die das Change-Log betreffen  ###################
    def isXBaseInsertedOrUpdatedOrDeleted( self, x: XBase ) -> bool:
        dictChanges = self.getChanges()
        if x in dictChanges["INSERT"]: return True
        if x in dictChanges["UPDATE"]: return True
        if x in dictChanges["DELETE"]: return True
        return False

    def _isInChangeLog( self, x: XBase, actionId: constants.tableAction ) -> bool:
        actionstring = constants.actionList[actionId]
        xlist: List[XBase] = self._changes[actionstring]
        return (x in xlist)

    def _writeChangeLog( self, actionId: constants.tableAction, x: XBase ):
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist: List[XBase] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def isChanged( self ) -> bool:
        for k, v in self._changes.items():
            if len( v ) > 0: return True
        return False

    def getChanges( self ) -> Dict[str, List[XBase]]:
        return self._changes

    def _removeFromChangeLog( self, x: XBase, actionId: constants.tableAction ) -> bool:
        actionstring = constants.actionList[actionId]
        xlist: List[XBase] = self._changes[actionstring]
        xlist.remove( x )

    def clearChanges( self ):
        self._changes.clear()
        self._prepareChangeDictionary()
        self.layoutChanged.emit()

    ################   SORT - FUNKTIONALITÄT  ##################
    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

    def isSortable( self ) -> bool:
        return self._sortable

    def sort( self, col: int, order: Qt.SortOrder ) -> None:
        if not self._sortable: return
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self._sort_col = col
        self._sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        self._xbaseList = sorted( self._xbaseList, key=cmp_to_key( self.compare ) )
        self.layoutChanged.emit()
        self.sortingFinished.emit() # muss gesendet werden NACHDEM layoutChanged gesendet wurde!

    def compare( self, x1: XBase, x2: XBase ) -> int:
        v1 = self._getValue( x1, self._sort_col )
        v2 = self._getValue( x2, self._sort_col )
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return 1 if self._sort_reverse else -1
        if v1 > v2: return -1 if self._sort_reverse else 1
        if v1 == v2: return 0

    def _getValue( self, x:XBase, col:int ) -> str:
        keys = list( self._keyHeaderMapper.values() )
        key = keys[col]
        return x.__dict__[key]

    ########### grober Unfug  ###############
    def getListToSort( self ) -> List:
        pass

    def receiveSortedList( self, li: List ) -> None:
        pass

def test():
    class XTest( XBase ):
        def __init__( self ):
            XBase.__init__( self )
            self.name = ""
            self.vorname = ""
            self.alter = 0
            self.haarfarbe = ""
            self.schuhgroesse = 0
            self.bemerkung = ""

    x1 = XTest()
    x1.name = "Kendel"
    x1.vorname = "Martin"
    x1.alter = 66
    x1.haarfarbe = "grau"
    x1.schuhgroesse = 44
    x1.bemerkung = "Das ist alles \nein riesengroßer Irrtum"

    x2 = XTest()
    x2.name = "Haaretz"
    x2.vorname = "Yosh"
    x2.alter = 56
    x2.haarfarbe = "schwarz"
    x2.schuhgroesse = 42

    tm = DefaultIccTableModel( (x1, x2 ) )
    tm.setSortable( True )
    tm.setKeyHeaderMappings( { "Nachname": "name", "Vorname": "vorname", "Alter": "alter", "Bemerkung": "bemerkung" } )
    tm.setNumColumnsIndexes( (2,) )

    from PySide2.QtWidgets import QApplication
    app = QApplication()

    tv = QTableView( )
    tv.setModel( tm )
    tv.setAlternatingRowColors( True )
    tv.setSortingEnabled( True )
    tv.resizeColumnsToContents()
    tv.resizeRowsToContents()
    tm.layoutChanged.connect( tv.resizeRowsToContents ) ## <======== WICHTIG bei mehrzeiligem Text in einer Zelle!
    tv.show()

    app.exec_()

if __name__ == "__main__":
    test()