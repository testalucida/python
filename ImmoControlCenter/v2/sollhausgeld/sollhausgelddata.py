from typing import List

import datehelper
from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollHausgeld


class SollHausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSollHausgelder( self, jahr: int ) -> List[XSollHausgeld]:
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr, 12, 31)
        sql = "select shg.shg_id, shg.vwg_id, shg.mobj_id, vwg.weg_name, vwg.master_name, shg.von, shg.bis, " \
              "shg.netto, shg.ruezufue, shg.bemerkung " \
              "from sollhausgeld shg " \
              "inner join verwaltung vwg on vwg.vwg_id = shg.vwg_id " \
              "where (shg.bis is NULL or shg.bis = '' or shg.bis >= '%s') " \
              "and not shg.von > '%s' " \
              "order by vwg.weg_name, shg.von desc" % (minbis, maxvon)
        l: List[XSollHausgeld] = self.readAllGetObjectList( sql, XSollHausgeld )
        for x in l:
            x.brutto = x.netto + x.ruezufue
        return l

    def getCurrentSollHausgeld( self, mobj_id: str ) -> XSollHausgeld:
        """
        liefert das momentan gültige Soll-Hausgeld für mobj_id
        :param mobj_id:
        :return: ein XHausgeld-Objekt
        """
        sql = "select s.shg_id, v.vw_id, s.mobj_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
              "(s.netto + s.ruezufue) as brutto, s.mobj_id, " \
              "v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
              "from sollhausgeld s " \
              "inner join verwaltung v on v.vwg_id = s.vwg_id " \
              "where s.mobj_id = '%s' " \
              "and (s.bis is NULL or s.bis = '' or s.bis >= CURRENT_DATE) " \
              "and s.von <= CURRENT_DATE" % mobj_id
        x = self.readOneGetObject( sql, XSollHausgeld )
        return x

    def getSollHausgeldAm( self, weg_name:str, jahr:int, monthNumber:int ) -> XSollHausgeld:
        """
        :param weg_name:
        :param jahr:
        :param monthNumber: 1: Januar ... 12: Dezember
        :return:
        """
        lastday = datehelper.getNumberOfDays( monthNumber )
        minbis = "%d-%02d-%02d" % (jahr, monthNumber, 1)
        maxvon = "%d-%02d-%02d" % (jahr, monthNumber, lastday)
        sql = "select s.shg_id, v.vw_id, s.vwg_id, s.mobj_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
              "(s.netto + s.ruezufue) as brutto, s.mobj_id, " \
              "v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
              "from sollhausgeld s " \
              "inner join verwaltung v on v.vwg_id = s.vwg_id " \
              "where v.weg_name = '%s' " \
              "and not s.von > '%s' " \
              "and (s.bis is NULL or s.bis = '' or s.bis >= '%s' ) "  % ( weg_name, maxvon, minbis )
        x = self.readOneGetObject( sql, XSollHausgeld )
        return x


def test():
    data = SollHausgeldData()
    # x:XSollHausgeld = data.getCurrentSollHausgeld( "charlotte" )
    x: XSollHausgeld = data.getSollHausgeldAm( "WEG Wilhelm-Marx-Str. 15", 2022, 5 )
    x.print()