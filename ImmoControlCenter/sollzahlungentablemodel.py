from abc import ABC, abstractmethod
from typing import List, Dict

from PySide2.QtCore import QAbstractTableModel

import constants
from icctablemodel import IccTableModel
from interfaces import XSollzahlung


class SollzahlungenTableModel( IccTableModel, ABC ):
    def __init__( self, sollList:List[XSollzahlung] ):
        QAbstractTableModel.__init__( self )
        self.sollList:List[XSollzahlung] = sollList
        """
        Gewünschte Spaltenfolge: 
        Objekt | Mieter / WEG | von | bis | netto | NKV / RüZuFü | Bemerkung
        """
        self._keylist = ("werterhaltend", "umlegbar", "master_name", "mobj_id", "kreditor", "buchungstext", "rgdatum", "buchungsdatum", "betrag", "rgtext")
        self._headers = ("w", "u", "Haus", "Whg", "Kreditor", "Buchungstext", "Rg.datum", "Buch.datum", "Betrag", "Rg.text")
        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XSollzahlung]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XSollzahlung],
            "UPDATE": List[XSollzahlung],
            "DELETE": List[XSollzahlung]
        }
        """

    @abstractmethod
    def getKeyList( self ) -> List[str]:
        pass

    @abstractmethod
    def getHeaders( self ) -> List[str]:
        pass

################################################################
class SollmietenTableModel( SollzahlungenTableModel ):
    def __init__( self, sollList: List[XSollzahlung] ):
        SollzahlungenTableModel.__init__( sollList )

    def getKeyList( self ) -> List[str]:
        return ( "mobj_id", "mv_id", "von", "bis", "netto", "nkv", "bemerkung" )

    def getHeaders( self ) -> List[str]:
        return ( "Objekt", "Mieter", "von", "bis", "netto", "NKV", "Bemerkung" )

#################################################################
class SollHGVTableModel( SollzahlungenTableModel ):
    def __init__( self, sollList: List[XSollzahlung] ):
        SollzahlungenTableModel.__init__( sollList )
        
    def getKeyList( self ) -> List[str]:
        return ( "mobj_id", "vwg_id", "von", "bis", "netto", "ruezufue", "bemerkung" )

    def getHeaders( self ) -> List[str]:
        return ( "Objekt", "WEG", "von", "bis", "netto", "RüZuFü", "Bemerkung" )