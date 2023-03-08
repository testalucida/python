from typing import List, Any

from defaulticctablemodel import DefaultIccTableModel
from interfaces import XGeschaeftsreise


class GeschaeftsreiseTableModel( DefaultIccTableModel ):
    def __init__( self, reiseList:List[XGeschaeftsreise] ):
        DefaultIccTableModel.__init__( self, reiseList )
        self.setKeyHeaderMappings( {
            "Haus": "master_name",
            "Beginn": "von",
            "Ende": "bis",
            "Zweck": "zweck",
            "Anz.\nPers.": "personen",
            "Übernachtung": "uebernachtung",
            "Übernacht.\nkosten": "uebernacht_kosten",
            "Gef. km": "km"
        } )
        self.setNumColumnsIndexes( (4, 6, 7) )

    def getBackground( self, indexrow: int, indexcolumn: int ) -> Any:
        return None
