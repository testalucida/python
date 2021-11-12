from typing import Any, List, Dict
from functools import cmp_to_key
from PySide2.QtCore import SIGNAL, Qt, QModelIndex

import constants
from defaulticctablemodel import DefaultIccTableModel
from icctablemodel import IccTableModel
from interfaces import XGeschaeftsreise


class GeschaeftsreisenTableModel( DefaultIccTableModel ):
    def __init__( self, reiseList:List[XGeschaeftsreise] ):
        DefaultIccTableModel.__init__( self, reiseList )
        self.setKeyHeaderMappings( {
            "Mietobjekt": "mobj_id",
            "Beginn": "von",
            "Ende": "bis",
            "Ziel": "ziel",
            "Zweck": "zweck",
            "Übernachtung": "uebernachtung",
            "Übernacht.\nkosten": "uebernacht_kosten",
            "Gef. km": "km",
            "Vpfl.\npausch.": "verpfleg_pauschale"
        } )
        self.setNumColumnsIndexes( (6, 7, 8) )
