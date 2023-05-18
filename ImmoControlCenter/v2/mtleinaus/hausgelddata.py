from typing import List, Dict

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XMtlHausgeld


class HausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getMtlHausgeldListe( self, aktiv=True ) -> List[XMtlHausgeld]:
        """
        Liefert die Mietobjekte, für die Hausgeld entrichtet wird (=die von einem Verwalter verwaltet werden)
        als Liste von XMtlHausgeld.
        D.h., ILL_Eich, NK_Kleist und SB_Kaiser werden nicht berücksichtigt.
        :param aktiv: Wenn False, werden ALLE (verwalteten) Mietobjekte geliefert, sonst nur die, bei denen dieses
                      Kennzeichen auf 1 steht (Tabelle mietobjekt)
                      Auch nach einem Verkauf ist ein Objekt noch solange "aktiv", bis die
                      z.B. die HG-Abrechnung mit dem Verwalter oder dem Käufer erfolgt ist.
                      Das kann ggf. mehrere Monate dauern.
        :return:
        """
        aktiv = 1 if aktiv == True else False
        sql = "select distinct mo.master_name, mo.mobj_id, vwg.weg_name " \
              "from mietobjekt mo " \
              "inner join verwaltung vwg on vwg.master_name = mo.master_name " \
              "where mo.aktiv = %d " % aktiv
        return self.readAllGetObjectList( sql, XMtlHausgeld )


##################################################################################

def test():
    data = HausgeldData()
    l = data.getMtlHausgeldListe()
    print( l )
    # l = data.getSollHausgelder( 2022 )
    #print( l )