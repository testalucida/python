from typing import Dict

from pandas import DataFrame, Series

from base.interfaces import XBase
from imon.enums import Period, Interval


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
        self.history:Series = None
        self.history_period = Period.unknown
        self.history_interval = Interval.unknown
        self.low_price = 0.0 # todo: der niedrigste Preis in der Periode
        self.high_price = 0.0 # todo: der höchste Preis in der Periode
        self.stueck = 0
        self.gesamtkaufpreis = 0 #Kaufpreis des gesamten Bestands
        self.preisprostueck = 0.0 # Gesamtkaufpreis / Stück
        self.maxKaufpreis = 0.0 # Max. Kaufpreis / Stück
        self.minKaufpreis = 0.0 # Min. Kaufpreis / Stück
        self.gesamtwert_aktuell = 0 # Stück * kurs_aktuell
        self.kurs_aktuell = 0.0
        self.delta_proz = 0.0 #prozentualer Unterschied zwischen preisprostueck und kurs_aktuell
        self.depot_id = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""
        if valuedict:
            self.setFromDict( valuedict )

class XDelta( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.wkn = ""
        self.delta_stck = 0
        self.delta_datum = ""
        self.preis_stck = ""
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )