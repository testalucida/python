from typing import Dict

from pandas import DataFrame, Series

from base.interfaces import XBase
from imon.enums import Period, Interval

class XDividendPayment( XBase ):
    def __init__( self, day:str="", value:float=0.0 ):
        XBase.__init__( self )
        self.day = day # Datum der Dividendenzahlung
        self.value = value # Betrag der Dividendenzahlung

class XDepotPosition( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.id = 0 # Primärschlüssel in Tabelle depotposition
        self.isin = ""
        self.ticker = ""
        self.wkn = ""
        self.basic_index = ""
        self.name = ""
        self.gattung = ""
        self.waehrung = ""
        self.flag_acc = False
        self.beschreibung = ""
        self.toplaender = ""
        self.topfirmen = ""
        self.topsektoren = ""
        self.history:Series = None
        self.history_period = Period.unknown
        self.history_interval = Interval.unknown
        self.dividends:Series = None # Dividenden, die im Lauf von history_period ausgeschüttet wurden.
        self.dividend_period = 0.0 # Summe der Dividenden PRO STÜCK, die während history_period ausgeschüttet wurden
        self.dividend_yield = 0.0 # Dividenden-Rendite
        self.low_price = 0.0 # todo: der niedrigste Preis in der Periode
        self.high_price = 0.0 # todo: der höchste Preis in der Periode
        self.stueck = 0 # Restbestand (Käufe und Verkäufe saldiert)
        self.gesamtkaufpreis = 0 #Kaufpreis des gesamten Bestands -- eigentlich irrelevant: wenn von 995 Stück 900 verkauft werden,
                                 # was soll dann der Gesamtkaufpreis aussagen?
        self.einstandswert_restbestand = 0 # Einstandswert des (Rest-)Bestandes, ermittelt nach der Formel:
                                      # Stückzahl * durchschnittlicher Stück-Kaufpreis
        self.preisprostueck = 0.0 # durchschnittl. Preis pro Stück nach der Formel: Gesamtkaufpreis / Stück
        self.maxKaufpreis = 0.0 # Max. Kaufpreis / Stück
        self.minKaufpreis = 0.0 # Min. Kaufpreis / Stück
        self.gesamtwert_aktuell = 0 # Stück * kurs_aktuell
        self.kurs_aktuell = 0.0
        self.delta_proz = 0.0 #prozentualer Unterschied zwischen preisprostueck und kurs_aktuell
        self.delta_kurs_1 = 0.0 # Kursentwicklung seit letztem Close in Prozent
        self.avg_kurs_50 = 0.0 # average Kurs letzte 50 Tage
        self.avg_kurs_200 = 0.0  # average Kurs letzte 200 Tage
        self.depot_id = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""
        if valuedict:
            self.setFromDict( valuedict )

class XDelta( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.name = ""
        self.wkn = ""
        self.isin = ""
        self.ticker = ""
        self.delta_stck = 0
        self.delta_datum = ""
        self.preis_stck = 0.0
        self.order_summe = 0.0 # delta_stck * preis_stck
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

class XDetail(XBase):
    """
    Wird für die Detail-Anzeige im InfoPanel benötigt (nach Drücken des Detail-Buttons).
    Enthält den Ausschnitt der Daten von XDepotPosition, die nicht im InfoPanel angezeigt werden.
    """
    def __init__(self):
        XBase.__init__( self )
        self.basic_index = ""
        self.beschreibung = ""
        self.toplaender = ""
        self.topfirmen = ""
        self.topsektoren = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""
