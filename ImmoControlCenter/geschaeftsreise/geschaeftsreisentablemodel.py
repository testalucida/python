from typing import List

from defaulticctablemodel import DefaultIccTableModel
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
            "Anz.\nPers.": "personen",
            "Übernachtung": "uebernachtung",
            "Übernacht.\nkosten": "uebernacht_kosten",
            "Gef. km": "km"
        } )
        self.setNumColumnsIndexes( (6, 7, 8) )
