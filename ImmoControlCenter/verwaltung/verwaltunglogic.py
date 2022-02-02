from typing import List

import datehelper
from interfaces import XVerwaltung, XHausgeldZahlungJahr, XSollHausgeld
from verwaltung.verwaltungdata import VerwaltungData


class VerwaltungLogic:
    def __init__(self):
        self._db = VerwaltungData()

    def getAktiveVerwaltungen( self, jahr:int ) -> List[XVerwaltung]:
        return self._db.getAktiveVerwaltungen( jahr )

    def getHausgeldzahlung( self, master_name:str, jahr:int ) -> XHausgeldZahlungJahr:
        """
        Liefert die tatsächlich getätigten Zahlungen in einem XHausgeldZahlungJahr-Objekt:
        Summe der Vorauszahlungen; Summe der Rücklagenzuführungen; Summe der aus Abrechnungen (können mehrere Zahlungen
        sein) errechneten Zahlungen.
        Die Rücklagenzuführungen werden aus der Tabelle <sollhausgeld> ermittelt, da sie aus der Hausgeld-Vorauszahlung
        nicht explizit ersichtlich sind, da immer eine Brutto-Vorauszahlung geleistet wird, die sowohl das Hausgeld
        wie auch die RüZuFü enthält.
        :param master_name:  Masterobjekt, zu dem die Zahlungen ermittelt werden sollen
        :param jahr:  Jahr, für das die Zahlungen ermittelt werden sollen.
        :return:
        """
        # die Summe der Vorauszahlungen aus Tabelle <zahlung> ermitteln:
        hgvSum:float = self._db.getHGVSumme( master_name, jahr )
        # die Abrechnungen-Summe aus Tabelle <zahlung> ermitteln:
        hgaSum:float = self._db.getHGASumme( master_name, jahr )
        # die Liste der Soll-Hausgelder ermitteln (HGV kann sich unterjährig ändern):
        sollHGVList:List[XSollHausgeld] = self._db.getSollHausgeld( master_name, jahr )
        # die RüZuFü fürs ganze Jahr ausrechnen:
        ruezufue = 0
        for soll in sollHGVList:
            anzMon = datehelper.getNumberOfMonths( soll.von, soll.bis, jahr )
            ruezufue += anzMon * soll.ruezufue
        x = XHausgeldZahlungJahr( master_name, jahr )
        x.hgv = hgvSum
        x.hga = hgaSum
        x.rueZuFue = round( ruezufue, 2 )
        return x

def test1():
    logic = VerwaltungLogic()
    x = logic.getHausgeldzahlung( "NK_Volkerstal", 2021 )
    print( x )