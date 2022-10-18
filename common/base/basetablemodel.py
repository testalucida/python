import decimal
import numbers
import sys
from functools import cmp_to_key
from PySide2.QtCore import QAbstractTableModel, SIGNAL, Qt, QModelIndex, QSize, Signal
from typing import Any, List, Dict, Tuple, Iterator, Iterable, Type
from PySide2.QtGui import QColor, QBrush, QFont, QPixmap

from base.interfaces import XBase, Action

##################  KeyHeaderMapping  ################
class KeyHeaderMapping:
    def __init__( self, key=None, header=None ):
        self.key = key
        self.header = header

##################  BaseTableModel  ##################
class BaseTableModel( QAbstractTableModel ):
    sorting_finished = Signal()
    def __init__( self, rowList:List[XBase]=None, jahr:int=None ):
        QAbstractTableModel.__init__( self )
        self.rowList:List[XBase] = rowList
        self._jahr:int = jahr # das Jahr ist bei manchen Models interessant, bei manchen nicht - kann also auf None stehen.
        self.headers:List = list()
        self.keys:List = list()
        self.headerColor = QColor( "#FDBC6A" )
        self.headerBrush = QBrush( self.headerColor )
        self.negNumberBrush = QBrush( Qt.red )
        self.greyBrush = QBrush( Qt.lightGray )
        self.inactiveBrush = QBrush( Qt.black )
        self.inactiveBrush.setStyle( Qt.BDiagPattern )
        self.boldFont = QFont( "Arial", 11, QFont.Bold )
        self.yellow = QColor( "yellow" )
        self.yellowBrush = QBrush( self.yellow )
        self.sortable = False
        self.sort_col = 0
        self.sort_ascending = False
        if rowList:
            self.setRowList( rowList )
        #self._changelog:ChangeLog = ChangeLog.inst()

    def _setDefaultKeyHeaderMapping( self ):
        """
        Per default verwenden wir die Keys eines der übergebenen Dictionaries als Keys und Headers
        :return:
        """
        x:XBase = self.rowList[0]
        for k in x.getKeys():
            self.keys.append( k )
            self.headers.append( k )

    def setRowList( self, rowList:List[XBase] ):
        self.rowList = rowList
        if len( rowList ) > 0:
            self._setDefaultKeyHeaderMapping()

    # def receiveSortedList( self, li:List[XBase] ) -> None:
    #     self.rowList = li

    def setKeyHeaderMappings( self, mappings:List[KeyHeaderMapping] ):
        self.headers = [x.header for x in mappings]
        self.keys = [x.key for x in mappings]

    def setKeyHeaderMappings2( self, keys:Iterable[str], headers:Iterable[str] ):
        self.keys = keys
        self.headers = headers

    def setHeaders( self, headerlist:Iterable[str] ):
        """
        Definiert die Spalten-Überschriften.
        Die Reihenfolge muss der Reihenfolge der Keys (Attribute) des XBase-Objekts entsprechen.
        :param headerlist:
        :return:
        """
        self.headers = headerlist

    def getColumnIndex( self, header ) -> int:
        return self.headers.index( header )

    def getColumnIndexByKey( self, key:str ) -> int:
        return self.keys.index( key )

    def getHeaders( self ) -> List[str]:
        return self.headers

    def getHeader( self, col:int ) -> Any:
        return self.headerData( col, orientation=Qt.Horizontal, role=Qt.DisplayRole )

    def getKeyByHeader( self, header:Any ) -> Any:
        headerIndex = self.headers.index( header )
        return self.keys[headerIndex]

    def getRowList( self ) -> List[XBase]:
        """
        :return: die rohe Liste der XBase-Elemente
        """
        return self.rowList

    def getJahr( self ) -> int:
        return self._jahr

    def getRow( self, x:XBase ) -> int:
        """
        Liefert die Zeile, in der das spezifizierte XBase-Objekt dargestellt wird
        :param x:
        :return:
        """
        return self.rowList.index( x )

    def getElement( self, indexrow: int ) -> XBase:
        return self.rowList[indexrow]

    def getElements( self, indexrows:List[int] ) -> List[XBase]:
        retlist = list()
        for r in indexrows:
            retlist.append( self.rowList[r] )
        return retlist

    def getKey( self, indexcolumn:int ):
        return self.keys[indexcolumn]

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        e:XBase = self.getElement( indexrow )
        return e.getValue( self.keys[indexcolumn] )

    def getText( self, indexrow: int, indexcolumn: int ) -> str:
        item = self.getValue( indexrow, indexcolumn )
        return item if isinstance( item, str ) else str(item)

    def getValueByName( self, indexrow:int, attrName:str ) -> Any:
        e:XBase = self.getElement( indexrow )
        return e.getValue( attrName )

    def getValueByColumnName( self, indexrow:int, colname:str ) -> Any:
        colidx = self.headers.index( colname )
        return self.getValue( indexrow, colidx )

    # def setValue( self, indexrow:int, indexcolumn:int, value:Any, writeLog=True ) -> None:
    #     """
    #     Ändert einen Wert in dem durch indexrow spezifiz. XBase-Element.
    #     Löst ein dataChanged-Signal aus. (Damit die View sich updaten kann.)
    #     Schreibt ein XChange-Objekt ins ChangeLog, wenn writeLog==True.
    #     *** ACHTUNG ***
    #     Leider kann nicht verhindert werden, dass XBase-Objekte, die Bestandteil dieses Models sind,
    #     außerhalb des Models verändert werden.
    #     Da das Model von einer solchen Änderung keine Kenntnis erhält, wird auch kein ChangeLog geschrieben!
    #     Wenn es notwendig ist, Objekte außerhalb des Models zu ändern, die View aber trotzdem aktualisiert
    #     werden soll, muss nach der externen Änderung die Methode objectUpdatedExternally(...) aufgerufen werden.
    #     Mit dem Parameter writeLog kann dabei gesteuert werden, ob das ChangeLog geschrieben werden soll
    #     - allerdings nicht auf Attributebene, weil hier nicht bekannt ist,
    #     welche Attribute geändert wurden - aber wenigstens auf Objekt-Ebene.
    #     ***************
    #     :param indexrow: Spezifiziert die Zeile der zu ändernden Zelle
    #     :param indexcolumn: Spezifiziert die Spalte der zu ändernden Zelle
    #     :param value: der neue Wert, der an dieser Stelle zu setzen ist.
    #     :param writeLog: wenn True, wird das ChangeLog geschrieben.
    #     :return:
    #     """
    #     oldval = self.getValue( indexrow, indexcolumn )
    #     if oldval == value: return
    #     e:XBase = self.getElement( indexrow )
    #     key = self.keys[indexcolumn]
    #     e.setValue( key, value )
    #     index = self.createIndex( indexrow, indexcolumn )
    #     self.dataChanged.emit( index, index, [Qt.DisplayRole] )
    #     if writeLog:
    #         method = sys._getframe().f_code.co_name
    #         self._changelog.addChange( classtype=self.__class__, method=method, action=Action.UPDATE, x=e,
    #                                    key=key, oldval=oldval, newval=value )

    # def objectUpdatedExternally( self, x:XBase, writeLog:bool=True, classtype:Type=None, method="",
    #                              action=Action.UPDATE,
    #                              key="", oldval=None, newval=None ) -> None:
    #     """
    #     Diese Methode behandelt ein XBase-Objekt, das außerhalb dieses Models geändert wurde.
    #     Sie löst ein dataChanged-Signal aus und schreibt das ChangeLog, wenn <writeLog> == True.
    #     Das ChangeLog wird allerdings nur auf Objekt- nicht auf Attributebene geschrieben.
    #     Ist das Korn "Attributebene" gewünscht, muss die Methode setValue(...) - gegebenenfalls mehrfach -
    #     aufgerufen werden.
    #     :param x: das geänderte XBase-Objekt
    #     :param writeLog: wenn True, wird das ChangeLog geschrieben
    #     :param classtype: Typ der externen Klasse, in der das Objekt geändert wurde
    #     :param method: Name der Methode der externen Klasse, in der das OBjekt gäendert wurde
    #     :param action: INSERT, UPDATE, DELETE
    #     :param key: Name des Attributs, das geändert wurde (nur bei UPDATE)
    #     :param oldval: Alter Wert des Attributs
    #     :param newval: Neuer Wert des Attributs
    #     :return: None
    #     """
    #     row = self.getRow( x )
    #     indexA = self.createIndex( row, 0 )
    #     indexZ = self.createIndex( row, self.columnCount() - 1 )
    #     self.dataChanged.emit( indexA, indexZ, [Qt.DisplayRole] )
    #     if writeLog:
    #         if not oldval: oldval = str( None )
    #         if not newval: newval = str( None )
    #         self._changelog.addChange( classtype, method, action, x, key, oldval, newval )

    def setValue( self, indexrow: int, indexcolumn: int, value: Any ) -> None:
        """
        Ändert einen Wert in dem durch indexrow spezifiz. XBase-Element.
        (Durch indexcolumn wird ein Attribut in diesem XBase-Element spezifiziert.)
        Löst ein dataChanged-Signal aus. (Damit die View sich updaten kann.)
        *** ACHTUNG ***
        Leider kann nicht verhindert werden, dass XBase-Objekte, die Bestandteil dieses Models sind,
        außerhalb des Models verändert werden.
        Da das Model von einer solchen Änderung keine Kenntnis erhält, wird auch kein dataChanged-Signal ausgelöst!
        Wenn es notwendig ist, Objekte außerhalb des Models zu ändern, die View aber trotzdem aktualisiert
        werden soll, muss nach der externen Änderung die Methode objectUpdatedExternally(...) aufgerufen werden.
        ***************
        :param indexrow: Spezifiziert die Zeile der zu ändernden Zelle
        :param indexcolumn: Spezifiziert die Spalte der zu ändernden Zelle
        :param value: der neue Wert, der an dieser Stelle zu setzen ist.
        :return:
        """
        oldval = self.getValue( indexrow, indexcolumn )
        if oldval == value: return
        e: XBase = self.getElement( indexrow )
        key = self.keys[indexcolumn]
        e.setValue( key, value )
        index = self.createIndex( indexrow, indexcolumn )
        self.dataChanged.emit( index, index, [Qt.DisplayRole] )

    def objectUpdatedExternally( self, x:XBase ):
        """
        Diese Methode behandelt ein XBase-Objekt, das außerhalb dieses Models geändert wurde.
        Sie löst ein dataChanged-Signal aus, damit die Anzeige aktualisiert wird.
        """
        row = self.getRow( x )
        indexA = self.createIndex( row, 0 )
        indexZ = self.createIndex( row, self.columnCount() - 1 )
        self.dataChanged.emit( indexA, indexZ, [Qt.DisplayRole] )

    def addObject( self, x:XBase ):
        """
        Wird aufgerufen, um ein neues Objekt (eine neue Tabellenzeile) hinzuzufügen.
        Löst ein dataChanged- und ein layoutChanged-Signal aus.
        :param x: das neue Objekt
        :return:
        """
        self.rowList.append( x )
        row = self.rowCount() - 1
        indexA = self.createIndex( row, 0 )
        indexZ = self.createIndex( row, self.columnCount()-1 )
        self.dataChanged.emit( indexA, indexZ, [Qt.DisplayRole] )
        # method = sys._getframe().f_code.co_name
        # self._changelog.addChange( self.__class__, method, Action.INSERT, x )
        self.layoutChanged.emit() # muss hier aufgerufen werden, damit in der View eine neue Row angezeigt wird.

    def removeObject( self, x:XBase ):
        """
        Wird aufgerufen, um ein Objekt (eine Tabellenzeile) aus der Tabelle zu löschen.
        Löst ein dataChanged- und ein layoutChanged-Signal aus.
        :param x: das zu löschende Objekt
        :return:
        """
        row = self.getRow( x )
        self.rowList.remove( x )
        indexA = self.createIndex( row, 0 )
        indexZ = self.createIndex( row, self.columnCount()-1 )
        self.dataChanged.emit( indexA, indexZ, [Qt.DisplayRole] )
        # method = sys._getframe().f_code.co_name
        # self._changelog.addChange( self.__class__, method, Action.DELETE, x )
        self.layoutChanged.emit() # muss hier aufgerufen werden, damit in der View eine Zeile weniger angezeigt wird.

    def removeObjects( self, xlist:List[XBase] ):
        for x in xlist:
            self.removeObject( x )

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self.rowList )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self.headers )

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            v = self.getValue( index.row(), index.column() )
            if isinstance( v, numbers.Number ): return int( Qt.AlignRight | Qt.AlignVCenter )
        elif role == Qt.BackgroundRole:
            return self.getBackgroundBrush( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForegroundBrush( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        elif role == Qt.DecorationRole:
            return self.getDecoration( index.row(), index.column() )
        elif role == Qt.SizeHintRole:
            return self.getSizeHint( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.headers[col]
            if role == Qt.BackgroundRole:
                if self.headerBrush:
                    return self.headerBrush
        return None

    def getBackgroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        return None

    def getForegroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        if self.negNumberBrush:
            val = self.getValue( indexrow, indexcolumn )
            if isinstance( val, numbers.Number ) and val < 0:
                return QBrush( Qt.red )

    def getFont( self, indexrow: int, indexcolumn: int ) -> QFont or None:
        return None

    def getDecoration( self, indexrow: int, indexcolumn: int ) -> QPixmap or None:
        return None

    def getSizeHint( self, indexrow:int, indexcolumn:int ) -> QSize or None :
        return None

    def setHeaderColor( self, color:QColor ):
        self.headerColor = color

    def displayNegNumbersRed( self, on:bool=False ):
        if on:
            self.negNumberBrush = QBrush( Qt.red )
        else:
            self.negNumberBrush = None

    # def find( self, value, caseSensitive:bool=False, exactMatch:bool=False ):
    #     """
    #     Sucht nach Vorkommen von <value> in allen Spalten und Zeilen und liefert
    #     die Position eines jeden Treffers als row/column-Tuple zurück.
    #     Die Suche erfolgt sowohl auf String-Basis wie auch auf numerischer Basis, wenn der
    #     Suchbegriff in eine Zahl (int oder float) umgewandelt werden kann.
    #     Als Treffer gilt auch, wenn <exactMatch> == False und der Suchbegriff <value> nur ein Teilstring
    #     eines Wertes aus dem TableModel ist.
    #     :param value: Suchbegriff, numerisch oder alpha
    #     :param caseSensitive: ob Groß-/Kleinschreibung beachtet werden soll
    #     :param exactMatch: ob der Vergleich zwischen den kompletten Strings erfolgen soll oder ob als Match auch
    #                     gelten soll, wenn <value> ein Teilstring des TableModel-Wertes ist.
    #     :return: yields jeden Treffer bestehend aus einem Tuple(row-Index, column-Index)
    #     """
    #     def makeComparable( val ):
    #         valNum = None
    #         if type( val ) in (int, float):
    #             valNum = val
    #             val = str( val )
    #         else: # string (hopefully)
    #             try:
    #                 valNum = int(val)
    #             except ValueError:
    #                 try:
    #                     valNum = float(val)
    #                 except ValueError:
    #                     pass
    #         if not caseSensitive:
    #             val = val.lower()
    #         return val, valNum
    #
    #     value, valueNum = makeComparable( value )
    #     l: List[Tuple] = list()
    #     for r in range( 0, self.rowCount() ):
    #         for c in range( 0, self.columnCount() ):
    #             tmval = self.getValue( r, c )
    #             tmval, tmvalNum = makeComparable( tmval )
    #             match = False
    #             if (exactMatch and value == tmval) or (not exactMatch and value in tmval ):
    #                 match = True
    #             if match or (tmvalNum is not None and valueNum is not None and tmvalNum == valueNum):
    #                 #l.append( (r, c) )
    #                 yield r, c
    #     #return l

    def isChanged( self ) -> bool:
        return self._changes.hasChanges()

    # def getChanges( self ) -> ChangeLog:
    #     return self._changes

    def clearChanges( self ):
        self._changes.clear()

    def setSortable( self, sortable:bool=True ):
        self.sortable = sortable

    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        if not self.sortable: return
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.sort_col = col
        self.sort_ascending = True if order == Qt.SortOrder.AscendingOrder else False
        self.rowList = sorted( self.rowList, key=cmp_to_key( self.compare ) )
        self.sorting_finished.emit()
        self.layoutChanged.emit()

    def compare( self, x1:XBase, x2:XBase ) -> int:
        key = self.getKey( self.sort_col )
        v1 = x1.getValue( key )
        v2 = x2.getValue( key )
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return 1 if self.sort_ascending else -1
        if v1 > v2: return -1 if self.sort_ascending else 1
        if v1 == v2: return 0

##################  SumTableModel  #########################
class SumTableModel( BaseTableModel ):
    """
    A BaseTableModel displaying a sum row below all other rows
    """
    def __init__( self, objectList:List[XBase], jahr:int, colsToSum:Iterable[str] ):
        BaseTableModel.__init__( self, objectList, jahr )
        self._colsToSum = colsToSum # Liste mit den keys (Attributnamen des XBase-Objekts) der Spalten,
                                    # die summiert werden sollen
        self._summen:List[Dict] = list() # enthält die Summen,
                                         # die unter den in _colsToSum spezifierten Spalten anzuzeigen sind
        self._rowCount = len( objectList ) + 1  # wegen Summenzeile
        self._fontSumme = QFont( "Arial", 12, weight=QFont.Bold )
        for col in self._colsToSum:
            summe = sum([e.getValue( col ) for e in objectList])
            dic = {"key": col, "sum" : summe}
            self._summen.append( dic )

    def rowCount( self, parent: QModelIndex = None ) -> int:
        return self._rowCount

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexrow == self._rowCount - 1:
            if indexcolumn == 0:
                return "SUMME"
            else:
                key = self.keys[indexcolumn]
                if key in self._colsToSum: # die Summe der Spalte, die die Werte von key enthält, soll angezeigt werden
                    dic = [d for d in self._summen if d["key"] == key][0]
                    return dic["sum"]
                else:
                    return ""
        return self.internalGetValue( indexrow, indexcolumn )

    def internalGetValue( self, indexrow:int, indexcolumn:int ) -> Any:
        """
        For internal use only.
        May be overridden by inherited classes
        :param indexrow:
        :param indexcolumn:
        :return:
        """
        e: XBase = self.getElement( indexrow )
        return e.getValue( self.keys[indexcolumn] )

    def getFont( self, indexrow: int, indexcolumn: int ) -> QFont or None:
        if indexrow == self._rowCount - 1:
            key = self.keys[indexcolumn]
            if key in self._colsToSum:
                return self._fontSumme
            else:
                return None

################################################################
def test():
    class X(XBase):
        def __init__(self, v1, v2 ):
            XBase.__init__( self )
            self.var1 = v1
            self.var2 = v2

    def onNewItem():
        xn = X( "Gustav", 99 )
        tm.addObject( xn )

    def onDeleteItem( rowlist ):
        if len( rowlist ) > 0:
            obj = tm.getElement( rowlist[0] )
            tm.removeObject( obj )

    def onEditItem( row ):
        obj = tm.getElement( row )
        ## so nicht:
        #obj.var1 = "Meister Karl"  # Mist!! Es wird kein ChangeLog geschrieben und
                                   # die Änderung wird nicht in der Tabelle angezeigt bis zum nächsten
                                   # layoutChanged-Signal
        ## entweder so:
        ##col = tm.getColumnIndexByKey( "var1" )
        ##tm.setValue( row, col, "Master Karl" )
        ## oder so:
        obj.var1 = "Meister Karl"
        tm.objectUpdatedExternally( obj )

    x1 = X( "Otto", 34 )
    x2 = X( "Paul", 57 )
    l = [x1, x2]
    tm = BaseTableModel( l )

    from PySide2.QtWidgets import QApplication
    from base.basetableview import BaseTableView
    from base.basetableviewframe import BaseTableViewFrame
    app = QApplication()
    v = BaseTableView()
    v.setModel( tm )
    frame = BaseTableViewFrame( v, True )
    frame.newItem.connect( onNewItem )
    frame.editItem.connect( onEditItem )
    frame.deleteItems.connect( onDeleteItem )
    frame.show()
    app.exec_()