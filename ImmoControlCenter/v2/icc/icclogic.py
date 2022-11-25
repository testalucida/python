from typing import List, Iterable, Dict

from base.basetablemodel import BaseTableModel, SumTableModel
from base.interfaces import XBase
from v2.icc.iccdata import IccData

######################   IccTableModel   ########################
from v2.icc.interfaces import XMasterobjekt, XMietobjekt, XKreditorLeistung, XLeistung


class IccTableModel( BaseTableModel ):
    def __init__( self, rowList:List[XBase]=None, jahr:int=None ):
        BaseTableModel.__init__( self, rowList, jahr )

######################   IccSumTableModel   #####################
class IccSumTableModel( SumTableModel ):
    def __init__( self, objectList:List[XBase], jahr:int, colsToSum:Iterable[str] ):
        SumTableModel.__init__( self, objectList, jahr, colsToSum )

########################   IccLogic   ###########################
class IccLogic:
    def __init__(self):
        self._iccdata = IccData()
        self._masterobjekte:List[XMasterobjekt] = None

    def getJahre( self ) -> List[int]:
        """
        Liefert eine Liste der Jahre, für die Daten in der Datenbank vorhanden sind.
        :return:
        """
        return self._iccdata.getJahre()

    def getMasterobjekte( self ) -> List[XMasterobjekt]:
        if not self._masterobjekte:
            self._masterobjekte = self._iccdata.getMasterobjekte()
        return self._masterobjekte

    def getMasterNamen( self ) -> List[str]:
        li = self.getMasterobjekte()
        names = [o.master_name for o in li]
        return names

    def getMietobjekte( self, master_name:str ) -> List[XMietobjekt]:
        return self._iccdata.getMietobjekte( master_name )

    def getMietobjektNamen( self, master_name:str ) -> List[str]:
        li = self.getMietobjekte( master_name )
        names = [o.mobj_id for o in li]
        return names

    def getKreditorLeistungen( self, master_name:str, mobj_id:str=None ) -> List[XKreditorLeistung]:
        li:List[XKreditorLeistung] = self._iccdata.getKreditorLeistungen( master_name )
        if mobj_id:
            li = [k for k in li if k.mobj_id == mobj_id]
        return li

    def getKreditoren( self, master_name:str ) -> List[str]:
        kredleistlist = self.getKreditorLeistungen( master_name )
        kredlist = [k.kreditor for k in kredleistlist]
        kredlist.insert( 0, "" )
        return kredlist

    def getLeistungen( self, master_name, kreditor:str ) -> List[str]:
        kredleistlist:List[XLeistung] = self._iccdata.getLeistungen( master_name, kreditor )
        leistungen = [l.leistung for l in kredleistlist]
        leistungen.insert( 0, "" )
        return leistungen

    def getLeistungskennzeichen( self, master_name, kreditor, leistung ) -> XLeistung or None:
        leistungslist: List[XLeistung] = self._iccdata.getLeistungen( master_name, kreditor )
        if len( leistungslist ) > 0:
            leistungslist = [l for l in leistungslist if l.leistung == leistung]
            if len( leistungslist ) > 0:
                return leistungslist[0]
        else: return None

