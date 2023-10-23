from typing import Dict

from pandas import DataFrame

from base.interfaces import XBase


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
        self.history:DataFrame = None
        self.stueck = 0
        self.gesamtkaufpreis = 0 #Kaufpreis des gesamten Bestands
        self.preisprostueck = 0.0 # Gesamtkaufpreis / Stück
        self.gesamtwert_aktuell = 0.0 # Stück * kurs_aktuell
        self.kurs_aktuell = 0.0
        self.delta_proz = 0.0 #prozentualer Unterschied zwischen preisprostueck und kurs_aktuell
        self.depot_id = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""
        if valuedict:
            self.setFromDict( valuedict )