from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollHausgeld


class SollHausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getCurrentSollHausgeld( self, mobj_id: str ) -> XSollHausgeld:
        """
        liefert das momentan gültige Soll-Hausgeld für mobj_id
        :param mobj_id:
        :return: ein XHausgeld-Objekt
        """
        sql = "select s.shg_id, v.vw_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
              "(s.netto + s.ruezufue) as brutto, " \
              "v.mobj_id, v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
              "from sollhausgeld s " \
              "inner join verwaltung v on v.vwg_id = s.vwg_id " \
              "where v.mobj_id = '%s' " \
              "and (s.bis is NULL or s.bis = '' or s.bis >= CURRENT_DATE) " \
              "and s.von <= CURRENT_DATE" % mobj_id
        x = self.readOneGetObject( sql, XSollHausgeld )
        return x