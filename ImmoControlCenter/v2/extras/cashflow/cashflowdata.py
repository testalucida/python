from typing import List, Iterable

import datehelper
from v2.icc.constants import EinAusArt
from v2.icc.iccdata import IccData
from v2.icc.interfaces import XEinAus


class CashflowData( IccData ):
    def __init__( self ):
        IccData.__init__( self )

    def getSummeEinzahlungen( self, master_name:str, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from einaus " \
              "where master_name = '%s' " \
              "and jahr = %d " \
              "and betrag > 0 " \
              % (master_name, jahr)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0

    def getSummeAuszahlungen( self, master_name:str, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from einaus " \
              "where master_name = '%s' " \
              "and jahr = %d " \
              "and betrag < 0 " \
              % (master_name, jahr)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0

    def getSumme( self, master_name:str, jahr:int, ea_art_db:str ) -> int:
        sql = "select sum(betrag) " \
              "from einaus " \
              "where master_name = '%s' " \
              "and jahr = %d " \
              "and ea_art = '%s' " % (master_name, jahr, ea_art_db )
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0

def test():
    d = CashflowData()
    master = "NK_Volkerstal"
    year = 2024
    suE = d.getSummeEinzahlungen( master, year )
    print( "Summe Einz.: ", suE )
    suA = d.getSummeAuszahlungen( master, year )
    print( "Summe Ausz.: ", suA )
    print( "Saldo: ", suE + suA )

if __name__ == "__main__":
    test()