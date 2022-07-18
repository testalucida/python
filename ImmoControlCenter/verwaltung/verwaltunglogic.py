from typing import List

import datehelper
from anlage_v.anlagev_interfaces import XErhaltungsaufwand
from interfaces import XVerwaltung, XHausgeldZahlungJahr, XSollHausgeld
from verwaltung.verwaltungdata import VerwaltungData


class VerwaltungLogic:
    def __init__(self):
        self._db = VerwaltungData()

    def getAktiveVerwaltungen( self, jahr:int ) -> List[XVerwaltung]:
        return self._db.getAktiveVerwaltungen( jahr )

    def getRuecklagenEntnahme( self, master_name:str, jahr:int ) -> float:
        return self._db.getRuecklagenEntnahme( master_name, jahr )

    def getRuecklagenEntnahmeNachzuegler( self, master_name:str, jahr:int ) -> [float,List[XErhaltungsaufwand]]:
        """
        Ein Nachzügler ist eine HG-Abrechnung für das Jahr X, die im Jahr X+1 zugestellt wurde,
        nachdem die Steuererklärung für das Jahr X bereits abgegeben wurde.
        Ein solcher Nachzügler ist nur interessant, wenn er eine Entnahme aus der Rücklage ausweist:
        Diese hätte eigentlich in der schon abgegebenen Steuererklärung für Jahr X enthalten sein müssen.
        Um sie nicht unberücksichtigt zu lassen, wird sie (unerlaubterweise) im Jahr X+2 berücksichtigt.
        Als Referenzdatum dient der Abgabetermin für die StE X im Jahr X+1, der in der Tabelle <est_abgabe>
        gespeichert wird. (Siehe auch "Vorgehen")

        ***BEACHTE***:
        Nachzügler, die mehr als 1 Jahr zu spät zugestellt werden (Hausverwaltung Hehn),
        können aus programmiertechnischen Gründen nicht berücksichtigt werden. Man müsste sonst für jede Abrechnung
        speichern, in welchem Jahr sie in der StE berücksichtigt wurde.
        *************

        Vorgehen:
        1.) Lies est_abgabe.abgegeben_am für est_abgabe.vj = <jahr>-1
        2.) Lies alle Abrechnungen,
            wo hg_abrechnung.ab_jahr = <jahr> - 1
            UND hg_abrechnung.ab_datum > est_abgabe.abgegeben_am
            UND hg_abrechnung.entnahme_rue != 0
        :param master_name:
        :param jahr: das aktuell zu veranlagende Jahr, d.h.: wenn <jahr> =2021 übergeben wird, wird hier nach
                    Nachzüglern aus dem Jahr 2020 gesucht.
        :return: die Summe der Entnahmen und eine Liste mit XErhaltungsaufwand-Objekten, je eines für jede Entnahme
        """
        letztesVj = jahr-1
        abgabeLetztesVj = self._db.getAbgabetermin( letztesVj )
        diclist = self._db.getRuecklagenEntnahmeNachzuegler( master_name, abgabeLetztesVj, letztesVj )
        li:List[XErhaltungsaufwand] = list()
        entn_sum = 0
        for dic in diclist:
            x = XErhaltungsaufwand()
            x.master_name = dic["master_name"]
            x.kreditor = "Hausverwaltung"
            x.buchungstext = "Entnahme Rücklage"

            x.betrag = dic["entnahme_rue"]
            # x. = dic[""]
            # x. = dic[""]
            # x. = dic[""]
            # x. = dic[""]
            entn_sum += x.betrag
            li.append( x )

        return [entn_sum, li] #todo: das Ergebnis brauchen wir beim Erhaltungsaufwand (Z. 40 und in der Detail-Tabelle zum
                    # Erhaltungsaufwand

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