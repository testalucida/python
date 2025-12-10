from argparse import ArgumentError
from typing import Iterable, List, Any

from typing_extensions import Sized


class SimpleDataTable:
    def __init__( self, tableName:str = None, columns:List[List]=None, headers:List=None ):
        self.tableName = tableName
        if headers is None:
            headers = list()
        if columns is None:
            columns = list()
        if len( headers ) != len( columns ):
            raise ArgumentError(
                "SimpleDataTable.__init__(): Anzahl der Spalte stimmt nicht mit Anzahl der Header überein." )
        self._columns = columns
        self._headers = headers

    def getColumnCount( self ) -> int:
        return len( self._columns )

    def getRowCount( self ) -> int:
        if self.getColumnCount() == 0:
            return 0
        return len( self._columns[0] )

    def getColumnIndex( self, header:str ) -> int:
        colIdx = self._headers.index( header )
        if colIdx < 0:
            raise ValueError( "SimpleDataTable.getValue(): columnName '%s' existiert nicht." % header )
        return colIdx

    def getColumn( self, header:str ) -> List:
        idx = self.getColumnIndex( header )
        return self._columns[idx]

    def getValue( self, header:str, row:int ) -> Any:
        colIdx = self.getColumnIndex( header )
        return self._columns[colIdx][row]

    def getValue2( self, colIdx:int, rowIdx:int  ) -> Any:
        return self._columns[colIdx][rowIdx]

    def setValue( self, header:str, row:int, value:Any ):
        idx = self.getColumnIndex( header )
        self._columns[idx][row] = value

    def addColumn2( self, header:str ) -> int:
        """
        erzeugt eine Liste in der Länge der Tabelle und fügt sie der Tabelle hinzu.
        Alle Felder werden mit None initialisiert
        """
        c = [None] * self.getRowCount()
        return self.addColumn( c, header )

    def addColumn( self, column:List, header:str="" ) -> int:
        """
        fügt <column> der Tabelle hinzu und liefert den Index dieser Spalte zurück
        """
        if len( column ) != self.getRowCount():
            raise ValueError( "SimpleDataTable.addColumn(): Die Anzahl der Werte in <column> stimmt nicht mit der Anzahl der Zeilen "
                                 "dieser Tabelle überein." )
        self._columns.append( column )
        self._headers.append( header )
        return len( self._columns ) - 1

    def addRow( self, columnValues:List=None ) -> int:
        """
        fügt der Tabelle eine Zeile hinzu ( allen Spalten bekommen ein zusätzliches Element )
        <columnValues> muss, wenn nicht None, soviel Werte enthalten, wie es Spalten in der Tabelle gibt
        """
        if columnValues:
            if len( columnValues ) != len( self._columns ):
                raise ValueError( "SimpleDataTable.addRow(): Anzahl der Spaltenwerte stimmt nicht mit Anzahl der Spalten überein." )
            for colVal, idx in zip( columnValues, range(self.getColumnCount() ) ):
                self._columns[idx].append( colVal )
        else:
            for c in self._columns:
                c.append( None )
        return self.getRowCount()

    def print( self ):
        for c, idx in zip( self._columns, range( self.getColumnCount() ) ):
            for v in c:
                print( "Col ", self._headers[idx], ": Val=", v )

def test():
    dt = SimpleDataTable()
    col1 = ["ABC", "DEF"]
    h1 = "Alphabet"
    col2 = [100, 200]
    h2 = "Zahlen"
    dt.addColumn( col1, h1 )
    dt.addColumn( col2, h2 )
    dt.print()

def test2():
    col1 = ["ABC", "DEF"]
    h1 = "Alphabet"
    col2 = [100, 200]
    h2 = "Zahlen"
    dt = SimpleDataTable( [col1, col2], [h1, h2] )
    dt.addRow( ["GHI", 300] )
    col3 = ["UUU", "UUU"]
    dt.addColumn( col3, "Lauter Uuuus" )
    dt.print()
    val = dt.getValue( "Lauter Uuuus", 1 )
    print( val )
    val = dt.getValue2( 1, 0 )
    print( val )
    dt.addRow()
    dt.print()
    dt.setValue( "Alphabet", 2, "XYZ" )
    dt.print()

if __name__ == "__main__":
    test2()
