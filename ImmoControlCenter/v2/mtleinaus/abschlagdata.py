from typing import List, Dict

from v2.icc.iccdata import IccData, DbAction
from v2.icc.interfaces import XSollMiete, XSollAbschlag


class AbschlagData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSollabschlaege__( self, jahr: int ) -> List[XSollAbschlag]:
        sql = "select sab_id, kreditor, vnr, leistung, ea_art, master_name, coalesce(mobj_id, '') as mobj_id, " \
              "von, coalesce(bis, '') as bis, " \
              "betrag, umlegbar, coalesce(bemerkung, '') as bemerkung " \
              "from sollabschlag " \
              "order by kreditor, mobj_id "
        l:List[XSollAbschlag] = self.readAllGetObjectList( sql, XSollAbschlag )
        return l

    def getSollabschlaege__Feb_2025( self, jahr: int ) -> List[XSollAbschlag]:
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr, 12, 31)
        sql = "select sab_id, kreditor, vnr, leistung, ea_art, master_name, coalesce(mobj_id, '') as mobj_id, " \
              "von, coalesce(bis, '') as bis, " \
              "betrag, umlegbar, coalesce(bemerkung, '') as bemerkung " \
              "from sollabschlag " \
              "where (bis is NULL or bis = '' or bis >= '%s') " \
              "and not von > '%s' " \
              "order by kreditor, mobj_id, von desc" % (minbis, maxvon)
        l:List[XSollAbschlag] = self.readAllGetObjectList( sql, XSollAbschlag )
        return l

    def getSollabschlaege( self ) -> List[XSollAbschlag]:
        sql = "select sab_id, kreditor, vnr, leistung, ea_art, master_name, coalesce(mobj_id, '') as mobj_id, " \
              "betrag, umlegbar, coalesce(bemerkung, '') as bemerkung " \
              "from sollabschlag " \
              "order by kreditor, mobj_id "
        l: List[XSollAbschlag] = self.readAllGetObjectList( sql, XSollAbschlag )
        return l

    def getSollAbschlag__Feb_2025( self, sab_id:int ) -> XSollAbschlag:
        sql = "select sab_id, kreditor, vnr, leistung, ea_art, master_name, mobj_id, von, coalesce(bis, '') as bis, " \
              "betrag, umlegbar, bemerkung " \
              "from sollabschlag " \
              "where sab_id = %d " % sab_id
        return self.readOneGetObject( sql, XSollAbschlag )

    def getSollAbschlag( self, sab_id:int ) -> XSollAbschlag:
        sql = "select sab_id, kreditor, vnr, leistung, ea_art, master_name, mobj_id, " \
              "betrag, umlegbar, bemerkung " \
              "from sollabschlag " \
              "where sab_id = %d " % sab_id
        return self.readOneGetObject( sql, XSollAbschlag )


    def getVnrUndEaArtUndUmlegbar( self, sab_id:int ) -> Dict:
        sql = "select vnr, ea_art, umlegbar from sollabschlag where sab_id = " + str( sab_id )
        dic = self.readOneGetDict( sql )
        return dic

    def insertSollAbschlag( self, xsa: XSollAbschlag ) -> int:
        mobj_id = "NULL" if not xsa.mobj_id else ("'%s'" % xsa.mobj_id)
        vnr = "NULL" if not xsa.vnr else ("'%s'" % xsa.vnr)
        leistung = "NULL" if not xsa.leistung else ("'%s'" % xsa.leistung)
        bemerkung = "NULL" if not xsa.bemerkung else ("'%s'" % xsa.bemerkung)
        sql = "insert into sollabschlag " \
              "(master_name, mobj_id, kreditor, leistung, vnr, ea_art, betrag, umlegbar, bemerkung) " \
              "values " \
              "('%s',         %s,      '%s',     %s,      %s,    '%s',  %.2f,   '%s',      %s)" % \
              (xsa.master_name, mobj_id, xsa.kreditor, leistung, vnr, xsa.ea_art, xsa.betrag, xsa.umlegbar, bemerkung)
        inserted_id = self.writeAndLog( sql, DbAction.INSERT, "sollabschlag", "sab_id", 0,
                                        newvalues=xsa.toString( printWithClassname=True ), oldvalues=None )
        xsa.sab_id = inserted_id
        return inserted_id

    def updateSollAbschlag( self, xsa:XSollAbschlag ) -> int:
        oldX = self.getSollAbschlag( xsa.sab_id )
        mobj_id = "NULL" if not xsa.mobj_id else ("'%s'" % xsa.mobj_id)
        vnr = "NULL" if not xsa.vnr else ("'%s'" % xsa.vnr)
        leistung = "NULL" if not xsa.leistung else ("'%s'" % xsa.leistung)
        bemerkung = "NULL" if not xsa.bemerkung else ("'%s'" % xsa.bemerkung)
        sql = "update sollabschlag " \
              "set " \
              "kreditor = '%s', " \
              "vnr = %s, " \
              "leistung = %s, " \
              "ea_art = '%s', " \
              "master_name = '%s', " \
              "mobj_id = %s, " \
              "betrag = %.2f," \
              "umlegbar = '%s', " \
              "bemerkung = %s " \
              "where sab_id = %d " % (xsa.kreditor, vnr, leistung, xsa.ea_art, xsa.master_name, mobj_id, xsa.betrag,
                                     xsa.umlegbar, bemerkung, xsa.sab_id )
        rowsAffected = self.writeAndLog( sql, DbAction.UPDATE, "sollabschlag", "sab_id", xsa.sab_id,
                                         newvalues=xsa.toString( True ), oldvalues=oldX.toString( True ) )
        return rowsAffected

    def deleteSollAbschlag( self, sab_id:int ):
        oldX = self.getSollAbschlag( sab_id )
        sql = "delete from sollabschlag " \
              "where sab_id = " + str(sab_id)
        self.writeAndLog( sql, DbAction.DELETE, "sollabschlag", "sab_id", sab_id,
                          newvalues=None, oldvalues=oldX.toString( printWithClassname=True ) )




##################################################################################

def test():
    data = AbschlagData()
    l = data.getSollabschlaege( 2022 )
    print( l )
    u = data.getVnrUndUmlegbar( 2 )
    print( u )