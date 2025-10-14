from typing import List, Iterable, Any

from base.basetablemodel import SumTableModel, BaseTableModel
from base.interfaces import XBase
from v2.extras.cashflow.cashflowdata import CashflowData

#############      ########################
from v2.icc.constants import EinAusArt
from v2.icc.interfaces import XCashflow, XMasterobjekt, XMasterobjektKurz


###################   CashflowTableModel   ####################
# class CashflowTableModel( SumTableModel ):
#     def __init__( self, cashflowlist:List[XCashflow], colsToSum:List[str] ):
#         SumTableModel.__init__( self, cashflowlist, 0, colsToSum )
#
#     def internalGetValue( self, indexrow:int, indexcolumn:int ) -> Any:
#         """
#         For internal use only.
#         May be overridden by inherited classes
#         :param indexrow:
#         :param indexcolumn:
#         :return:
#         """
#         e: XCashflow = self.getElement( indexrow )
#         val = e.getValue( self.keys[indexcolumn] )
#         return val

class CashflowTableModel( SumTableModel ):
    def __init__( self, cashflowlist:List[XCashflow], colsToSum:List[str] ):
        SumTableModel.__init__( self, cashflowlist, 0, colsToSum )

###################   ErtragLogic   #######################
class CashflowLogic:
    def __init__( self ):
        self._cashflowData = CashflowData()

    def getCashflowTableModel__( self ) -> CashflowTableModel:
        xlist = list()
        x1 = XCashflow()
        x1.master_id = 1
        x1.master_name = "BUEB"
        x1.__dict__["2025\nEinzahlg."] = 5000
        x1.__dict__["2025\nAuszahlg."] = -4000
        x1.__dict__["2025\nSaldo"] = 1000
        xlist.append( x1 )
        x2 = XCashflow()
        x2.master_id = 1
        x2.master_name = "CAESAR"
        x2.__dict__["2025\nEinzahlg."] = 3000
        x2.__dict__["2025\nAuszahlg."] = -2500
        x2.__dict__["2025\nSaldo"] = 500
        xlist.append( x2 )

        tm = CashflowTableModel( xlist, ("2025\nEinzahlg.", "2025\nAuszahlg.", "2025\nSaldo") )
        tm.setHeaders( ("id", "Objekt", "2025\nEinzahlg.", "2025\nAuszahlg.", "2025\nSaldo") )
        return tm

    def getCashflowTableModel( self ) -> CashflowTableModel:
        """
        Das CashflowTableModel hat folgenden Aufbau:
        In Spalte 0 stehen die Master-IDs, in Spalte 1 die Masterobjekte.
        In den folgenden Spalten stehen die Cashflow-Zahlen der Jahre wie folgt:
        Spalte 0    Spalte 1    Spalte 2        Spalte 3        Spalte 4        Spalte 4 ...
           id        Master       2025 Einz.    2025 Ausz.      2025 Soll       2024 Einz.   ...
           12        SB-Kaiser     60000        -40000           20000           58000  ...
        """
        masters: List[XMasterobjektKurz] = self._cashflowData.getMasterobjekteKurz()
        l = list()
        years = self._cashflowData.getJahre()
        einzahlg = "Einzahlg."
        auszahlg = "Auszahlg."
        saldo = "Saldo"
        for master in masters:
            x = XCashflow()
            for year in years:
                sYear = str(year) + "\n"
                x.master_id = master.master_id
                x.master_name = master.master_name
                # Spaltenname:
                colname_ein = sYear + einzahlg
                x.__dict__[colname_ein] = self._cashflowData.getSummeEinzahlungen( master.master_name, year )
                colname_aus = sYear + auszahlg
                x.__dict__[colname_aus] = self._cashflowData.getSummeAuszahlungen( master.master_name, year )
                colname_saldo = sYear + saldo
                x.__dict__[colname_saldo] = x.__dict__[colname_ein] + x.__dict__[colname_aus]  # Auszahlungen sind negativ, deshalb '+'
            l.append( x )

        # l = sorted( l, key=lambda x: x.ertrag, reverse=True ) # größter Ertrag oben
        # Die Spalten-Header bauen:
        headers = ["id", "Objekt"]
        sYears = [str( y ) for y in years]
        for sYear in sYears:
            headers.append( sYear + "\n" + einzahlg )
            headers.append( sYear + "\n" + auszahlg )
            headers.append( sYear + "\n" + saldo )
        # TableModel instanzieren, alle Spalten außer der ersten sind summierbar
        tm = CashflowTableModel( l, headers[2:] )
        tm.setHeaders( headers )
        return tm

    # def getCashflowTableModel( self ) -> CashflowTableModel:
    #     """
    #     Das CashflowTableModel hat folgenden Aufbau:
    #     In Spalte 0 stehen die Masterobjekte.
    #     In den folgenden Spalten stehen die Cashflow-Zahlen der Jahre wie folgt:
    #     Spalte 0    Spalte 1    Spalte 2    Spalte 3    Spalte 4 ...
    #     Master       E 2025      A 2025      S 2025       E 2024   ...
    #     SB-Kaiser     60000      -40000       20000        58000  ...
    #     """
    #     masters:List[XMasterobjektKurz] = self._cashflowData.getMasterobjekteKurz()
    #     l = list()
    #     years = self._cashflowData.getJahre()
    #     for master in masters:
    #         for year in years:
    #             x = XCashflow()
    #             x.master_id = master.master_id
    #             x.master_name = master.master_name
    #             x.jahr = year
    #             x.einzahlungen = self._cashflowData.getSummeEinzahlungen( master.master_name, year )
    #             x.auszahlungen = self._cashflowData.getSummeAuszahlungen( master.master_name, year )
    #             x.saldo = x.einzahlungen + x.auszahlungen # Auszahlungen sind negativ, deshalb '+'
    #             l.append( x )
    #
    #     # l = sorted( l, key=lambda x: x.ertrag, reverse=True ) # größter Ertrag oben
    #     # Die Spalten-Header bauen:
    #     sYears = [str( y ) for y in years]
    #     headers = ["Objekt",]
    #     for sYear in sYears:
    #         header = "Einzahlg." + "\n" + sYear
    #         headers.append( header )
    #         header = sYear + "\n" + "Auszahlg."
    #         headers.append( header )
    #         header = sYear + "\n" + "Saldo"
    #         headers.append( header )
    #     # TableModel instanzieren, alle Spalten außer der ersten sind summierbar
    #     tm = CashflowTableModel( l, headers[1:] )
    #     tm.setHeaders( headers )
    #     return tm

def test():
    logic = CashflowLogic()
    tm = logic.getCashflowTableModel()

    print( tm )

if __name__ == "__main__":
    test()