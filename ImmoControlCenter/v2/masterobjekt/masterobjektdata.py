from typing import Dict

from v2.icc.iccdata import IccData, DbAction


class MasterobjektData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getMasterObjektData1( self, master_id:int ) -> Dict:
        sql = "select hauswart, hauswart_telefon, hauswart_mailto, heizung, energieeffz, veraeussert_am, bemerkung " \
              "from masterobjekt " \
              "where master_id = %d " % master_id
        di = self.readOneGetDict( sql )
        return di

    def updateMasterobjekt1( self, master_id:int,
                             hauswart:str, hauswart_telefon:str, hauswart_mailto:str,
                             heizung:str, energieeffz:str,
                             veraeussert_am, bemerkung:str  ) -> int:
        """
        Ändert die Attribute gem. Argumentliste in dem Masterobjekt, das durch master_id identifiziert wird.
        Der Update wird ins WriteLog eingetragen
        :param master_id:
        :param hauswart:
        :param hauswart_telefon:
        :param hauswart_mailto:
        :param heizung:
        :param energieeffz:
        :param veraeussert_am:
        :param bemerkung:
        :return: die Anzahl der betroffenen Rows. Sollte 1 oder, im Falle einer falschen master_id, 0 sein.
        """
        # aktuellen Satz holen wg WriteLog:
        oldD = self.getMasterObjektData1( master_id )
        sql = "update masterobjekt " \
              "set hauswart = '%s', " \
              "hauswart_telefon = '%s', " \
              "hauswart_mailto = '%s', " \
              "heizung = '%s', " \
              "energieeffz = '%s', " \
              "veraeussert_am = '%s', " \
              "bemerkung = '%s' " \
              "where master_id = %d " % ( hauswart, hauswart_telefon, hauswart_mailto,
                                          heizung, energieeffz, veraeussert_am, bemerkung, master_id )
        newD = { "hauswart": hauswart, "hauswart_telefon": hauswart_telefon, "hauswart_mailto": hauswart_mailto,
                 "heizung": heizung, "energieeffz": energieeffz,
                 "veraeussert_am": veraeussert_am, "bemerkung": bemerkung}
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE,
                                         table="masterobjekt", id_name="master_id", id_value=master_id,
                                         newvalues=str( newD ), oldvalues=str( oldD ) )
        return rowsAffected


######################  TEST TEST TEST

def test():
    data = MasterobjektData()
    master_id = 15
    d = data.getMasterObjektData1( master_id )
    print( str(d) )
    rowsAffected = data.updateMasterobjekt1( master_id, "Thomas Müller", "06821/12345", "mueller@gmx.com",
                                            "Gasetagenheizung", "F",
                                            "2023-08-31", "keine Bemerkung" )
    print( "rowsAffected: ", rowsAffected)
    data.commit()