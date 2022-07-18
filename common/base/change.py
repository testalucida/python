from datetime import datetime
from typing import List, Tuple, Any

from base.interfaces import XBase

####################  Change  #######################
class Change:
    def __init__( self, XBase, key, oldval, newval ):
        self.xbase:XBase = XBase
        self.key = key
        self.oldval = oldval
        self.newval = newval
        self.timestamp = datetime.now()

##################  ChangeLog  ###################
class ChangeLog:
    def __init__( self ):
        self._list:List[Change] = list()

    def addChange( self, x:XBase, key, oldval, newval ) -> None:
        """
        Schreibt das Änderungslogbuch
        :param indexrow:  Zeile, in der die Änderung stattgefunden hat
        :param indexcolumn:  Spalte, in der sich der Wert geändert hat
        :param x: von der Änderung betroffenes XBase-Objekt
        :param key: Attributname (Key im XBase.__dict__)
        :param oldval: Wert vor der Änderung
        :param newval: Wert nach der Änderung
        :return: None
        """
        c = Change( x, key, oldval, newval )
        self._list.append( c )

    def hasChanges( self ) -> bool:
        return len( self._list ) > 0

    def getChanges( self ) -> List[Change]:
        return self._list

    def getChangedObjects( self ):
        return [x.xbase for x in self._list]

    def getChangesForObject( self, obj ) -> List[Change]:
        return [change for change in self._list if change.xbase == obj]

    def getChangesForKey( self, object_, key ) -> List[Change]:
        objlist = self.getChangesForObject( object_ )
        keylist = [obj.key for obj in objlist if obj.key == key]
        return keylist

    def getFirstAndLastValueForKey( self, obj, key ) -> Tuple[Any, Any]:
        chnglist = self.getChangesForKey( obj, key )
        len_ = len( chnglist )
        if len_ == 0:
            raise Exception( "ChangeLog.getInitialAndLastValueForObject(): object/key not found" )
        first = chnglist[0].oldval
        last = chnglist[len_-1].newval
        return ( first, last )

    def clear( self ):
        self._list.clear()