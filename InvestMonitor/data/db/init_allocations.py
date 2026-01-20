from typing import List, Dict

from base.databasecommon2 import DatabaseCommon
from base.interfaces import XBase
from data.db.investmonitordata import InvestMonitorData
from imon.definitions import DATABASE
from interface.interfaces import XAllokation

class XAllocationsAlt( XBase ):
    """
    Klasse wird nur für die Initialisierung der neuen Tabelle allokation benötigt, deshalb wird sie
    hier deklariert und nicht in interfaces.py
    """
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.id:int = 0 # depotposition.id
        self.wkn:str = ""
        self.topfirmen = "" # depotposition.topfirmen - bsp. "REC ORD A 3.05%; PETROBRAS - PETROLEO BRASILEIRO SA VZ. 2.35%"
        self.toplaender = "" # depotposition toplaender - bsp. "Brasilien 24%; Taiwan 17%; China 15%; Indien 10%; "
        self.topsektoren = "" # depotposition topsektoren - bsp. "Finanz 22%; Immobilien 15%; Industrie 15%; Technologie 10%"
        if valuedict:
            self.setFromDict( valuedict )

class XAllocNeu:
    def __init__(self):
        self.name = ""
        self.percent = 0.0

class InitAllocations( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self, DATABASE )
        self._db = InvestMonitorData()

    def _insertAllocList( self, wkn:str, typ:str, allocList:List[XAllocNeu] ):
        for alloc in allocList:
            self._db.insertAllocation(wkn, typ, alloc.name, alloc.percent)

    def work( self ):
        depposlist:List[XAllocationsAlt] = self.getDepposAllocationsAlt()
        for deppos in depposlist:
            if deppos.toplaender and len(deppos.toplaender.strip()) > 0:
                laenderAllocList:List[XAllocNeu] = self.getStructuredAllokationList(deppos.toplaender)
                self._insertAllocList(deppos.wkn, "Land", laenderAllocList)
            if deppos.topsektoren and len(deppos.topsektoren.strip()) > 0:
                sektorenAllocList: List[XAllocNeu] = self.getStructuredAllokationList( deppos.topsektoren )
                self._insertAllocList( deppos.wkn, "Sektor", sektorenAllocList )
            if deppos.topfirmen and len(deppos.topfirmen.strip()) > 0:
                firmenAllocList: List[XAllocNeu] = self.getStructuredAllokationList( deppos.topfirmen )
                self._insertAllocList( deppos.wkn, "Firma", firmenAllocList )
        self.commit()

    @staticmethod
    def getStructuredAllokationList( alloclist_alt:str ) -> List[XAllocNeu]:
        alloc_neu_list = list()
        allocs_u_proz = alloclist_alt.split(";") # ==> ['Brasilien 24%', ' Taiwan 17%', ' China 15%', ' Indien 10%', ' ']
        allocs_u_proz = [alloc for alloc in allocs_u_proz if alloc > " "]
        # remove leading whitespace:
        allocs_u_proz = [aup.lstrip() for aup in allocs_u_proz] # ['Brasilien 24%', 'Taiwan 17%', 'China 15%', 'Indien 10%', '']
        # extract percent values:
        for alloc_alt in allocs_u_proz:
            alloc_neu = XAllocNeu()
            try:
                idx = alloc_alt.index("%")
            except:
                # es gibt keine Prozentangabe in alloc_alt
                alloc_neu.name = alloc_alt
                alloc_neu_list.append( alloc_neu )
                continue

            idx -= 1 # das %-Zeichen selbst wollen wir nicht
            # Manchmal ist ein Leerzeichen zwischen der Prozentzahl und dem Prozentzeichen, das müssen wir ausblenden
            while idx > 0 and alloc_alt[idx] == " ":
                idx -= 1
            perc = ""
            for idx in range(idx, -1, -1): # alte Allokation von hinten nach vorn abarbeiten
                c = alloc_alt[idx]
                if c > " ":
                    if c == ",": c = "." # für die spätere Umwandlung in float brauchen wir . statt ,
                    perc = c + perc
                else:
                    print("alloclist_alt: ", alloclist_alt, ", Prozent: '%s'" %perc)
                    alloc_neu.percent = float(perc)
                    print("Prozent: ", alloc_neu.percent)
                    break

            # auf den letzten Buchstaben des Allokationsnamen setzen
            while idx > 0 and alloc_alt[idx] == " ":
                idx -= 1
            idx += 1
            alloc_neu.name = alloc_alt[:idx]
            alloc_neu_list.append(alloc_neu)

        return alloc_neu_list


    def getDepposAllocationsAlt( self ) -> List[XAllocationsAlt]:
        """
        """
        sql = ("select id, wkn, topfirmen, toplaender, topsektoren "
               "from depotposition "
               "where flag_displ = 1 ")
        xlist = self.readAllGetObjectList( sql, XAllocationsAlt )
        return xlist

if __name__ == "__main__":
    allocs = InitAllocations()
    allocs.work()
