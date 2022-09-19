from PySide2.QtCore import Signal, QObject

import datehelper
from business import BusinessLogic
from geschaeftsreise.geschaeftsreiselogic import GeschaeftsreiseLogic
from qtderivates import IntDisplay

class SumFieldsProvider( QObject ):
    __instance = None
    dbaccess_failed = Signal( str )

    def __init__( self, sumMieten:IntDisplay, sumAusgaben:IntDisplay, sumHGV:IntDisplay, saldo:IntDisplay, errorCallback ):
        QObject.__init__( self )
        if SumFieldsProvider.__instance:
            raise Exception( "You can't instantiate SumFieldsAccess more than once." )
        else:
            SumFieldsProvider.__instance = self

        self._sumMieten = sumMieten
        self._sumAusgaben = sumAusgaben
        self._sumHGV = sumHGV
        self._saldo = saldo
        self._errorCallback = errorCallback

    @staticmethod
    def inst() -> __instance:
        if SumFieldsProvider.__instance is None:
           raise Exception( "SumFieldsAccess not yet constructed." )
        return SumFieldsProvider.__instance

    def setSumFields( self ):
        try:
            y = datehelper.getCurrentYear()
            sumMieten, sumAusgaben, sumHGV = BusinessLogic.inst().getSummen( y )
            reiselogic = GeschaeftsreiseLogic()
            reisekosten = int( round( reiselogic.getSummeGeschaeftsreisekosten( y ) ) )
        except Exception as ex:
            sumMieten = 0
            sumAusgaben = 0
            sumHGV = 0
            reisekosten = 0
            self._errorCallback( str( ex ) )

        self.setSumMieten( sumMieten )
        self.setSumAusgaben( sumAusgaben + reisekosten )
        self.setSumHGV( sumHGV )

    def getSumMieten( self ) -> int:
        return self._sumMieten.getIntValue()

    def getSumAusgaben( self ) -> int:
        return self._sumAusgaben.getIntValue()

    def getSumHGV( self ) -> int:
        return self._sumHGV.getIntValue()

    def getSaldo( self ) -> int:
        return self._saldo.getIntValue()

    def addMiete( self, val:int ):
        sum = self.getSumMieten()
        sum += val
        self.setSumMieten( sum )

    def addAusgabe( self, val:int ):
        sum = self.getSumAusgaben()
        sum += val
        self.setSumAusgaben( sum )

    def addHGV( self, val:int ):
        sum = self.getSumHGV()
        sum += val
        self.setSumHGV( sum )

    def setSumMieten( self, val:int ) -> None:
        self._sumMieten.setIntValue( val )
        self._calculateSaldo()

    def setSumAusgaben( self, val:int ) -> None:
        self._sumAusgaben.setIntValue( val )
        self._calculateSaldo()

    def setSumHGV( self, val:int ) -> None:
        self._sumHGV.setIntValue( val )
        self._calculateSaldo()

    def _calculateSaldo( self ):
        saldo = self.getSumMieten() + self.getSumAusgaben() + self.getSumHGV()
        self._saldo.setIntValue( saldo )