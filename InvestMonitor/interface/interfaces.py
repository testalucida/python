import datetime
from typing import Dict, List, Any

import pandas
from pandas import DataFrame, Series
from yfinance.scrapers.quote import FastInfo

import datehelper
from base.basetablemodel import SumTableModel
from base.interfaces import XBase
from imon.enums import Period, Interval

class XMatch(XBase):
    def __init__(self, wkn, isin, ticker, name ):
        XBase.__init__(self)
        self.wkn = wkn
        self.isin = isin
        self.ticker = ticker
        self.name = name

class XDateValueItem( XBase ):
    def __init__( self, dateIso:str, value:Any ):
        XBase.__init__( self, valuedict=None )
        self.dateIso = dateIso
        self.value:Any = value

    def getDatetime( self ) -> datetime.date:
        return datehelper.getDateFromIsoString(self.dateIso)

class XWpGattung(XBase):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.gattung = "" # Fond, ETF, Anleihe etc.
        self.summe = 0 # Summe in Euro für diese Gattung
        self.prozent = 0.0 # Anteil dieser Gattung am (beobachteten) Depot
        if valuedict:
            self.setFromDict( valuedict )

class XAllocation(XBase):
    def __init__( self, valuedict: Dict = None ):
        XBase.__init__( self )
        self.id = 0
        self.wkn = ""
        self.typ = "" # Land, Sektor, Firma
        self.name = "" # z.B. "Japan", "Technology", "Sony"
        self.prozent = 0.0  # Anteil dieser Allokation an wkn
        if valuedict:
            self.setFromDict( valuedict )

class XAllocationAmount(XBase):
    """
    Daten für den Überblick nach Depot-Allokationen nach Ländern, Sektoren, Firmen.
    Es gibt also z.B. genau 1 XAllocationAmount-Objekt für das Land UK,
    dessen .wert entspricht der Summe aller prozentualen Werte derjenigen
    Depot-Positionen, die in UK investiert sind.
    Beispiel: Wenn der Wert einer solchen deppos 10000 Euro ist und die UK-Allokation mit
    10% ausgewiesen ist, dann geht der Wert dieser deppos mit
    1000 Euro in das UK-XAllocationAmount-Objekt ein.
    """
    def __init__( self ):
        XBase.__init__( self )
        self.name = "" # z.B. "Japan", "Technology", "Sony"
        self.wert = 0 # mit welchem Betrag in EUR das Depot in dieses Land/Sektor/Firma investiert ist
        self.prozent = 0.0 # Prozentsatz, der sich errechnet zu Wert dieser Allokation / Gesamt-Depotwert

class XAllocationViewModel( XBase ):
    """
    Ein Model, das die statistischen Daten für die AllocationView-Anzeige enthält.
    """
    def __init__( self ):
        XBase.__init__( self )
        self.depot_gesamtwert = 0
        self.stmLaender:SumTableModel = None
        self.stmSektoren:SumTableModel = None
        self.stmFirmen:SumTableModel = None

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
        self.ter = 0.0  # annual total expense ratio
        self.waehrung = "" # EUR, USD, etc. => immer die Original-Währung, außer: GBp wird GBP
        self.flag_acc = False
        self.beschreibung = ""
        # self.toplaender = "" # deprecated
        # self.topfirmen = ""  # deprecated
        # self.topsektoren = "" # deprecated
        self.allokationen:List[XAllocation] = None # neu: Liste der Allokationen (Länder, Sektoren, Firmen)
        self.anteil_usa = 0  # Anteil von US-Firmen
        self.letzte_aktualisierung = "" # Datum, wann die letzte Detail-Aktualisierung erfolgt ist.
        self.period = Period.unknown
        self.interval = Interval.unknown
        self.tradingDaysPeriod:pandas.DatetimeIndex = None # trading days in der eingestellten period, sortiert ASC
        self.startIdxPeriod:int = -1 # der für die gewünschte period zu wählende start-index in der
                                     # Liste tradingDays
        self.closePrices:List[float] = None # alle Kurse über 5 Jahre, börsentäglich
        self.closePricesEUR: List[float] = None  # dto
        self.closePricesPeriod:List[float] = None
        self.closePricesEURPeriod:List[float] = None
        self.dividends:List[float] = None   # bezahlte Dividenden in Orig.währung pro Stück über 5 Jahre, börsentäglich
        self.dividendsEUR:List[float] = None # dto, aber in EUR
        #self.dividendsEURPeriod:List[float] = None # bezahlte Dividenden in EUR pro Stück in der gewählten Periode
                                                    # sollte in der Summe self.dividend_period ergeben
        self.dividend_period = 0.0 # Summe der Dividenden PRO STÜCK, die während period ausgeschüttet wurde
        self.dividend_yield = 0.0 # Dividendenrendite:
                                  # Summe der Dividenden in der gewählten Periode / Kurs am ersten Tag der Periode
        self.dividend_paid_period = 0  # Die Summe der Dividenden, die für diese Depotposition in der eingestellten
                                       # Periode ausbezahlt wurde
        self.dividend_days:List[datetime.date] = None # die Tage, an denen in period die Ausschüttungen erfolgten
        self.stueck = 0 # Restbestand (Käufe und Verkäufe saldiert)
        self.einstandswert_restbestand = 0 # Einstandswert des (Rest-)Bestandes, ermittelt nach der Formel:
                                      # Stückzahl * durchschnittlicher Stück-Kaufpreis
        self.preisprostueck = 0.0 # durchschnittl. Preis pro Stück nach der Formel: Gesamtkaufpreis / Stück
        self.maxKaufpreis = 0.0 # Max. Kaufpreis / Stück
        self.minKaufpreis = 0.0 # Min. Kaufpreis / Stück
        self.erster_kauf = "" # DAtum des ersten Kaufs
        self.letzter_kauf = "" # Datum des letzten Kaufs
        self.kaufKurse:List[float] = None # enthält die Kurse ALLER Käufe (in EUR) dieses Wertpapiers
                                # Die Reihenfolge entspricht der in tradingDays, d.h., die Liste hat genauso viele
                                # Einträge wie tradingDays. Eine 0 Steht für kein Kauf, ein Wert > 0 steht für den
                                # Kurs, zu dem gekauft wurde
        self.kauf_dtix:List[datetime.datetime] = None # enthält die datetimes ALLER Käufe dieses Wertpapiers
        self.verkaufKurse:List[float] = None  # enthält die Kurse ALLER Verkäufe (in EUR) dieses Wertpapiers,
                                       # Form wie kaeufe
        self.verkauf_dtix:List[datetime.datetime] = None # enthält die datetimes ALLER Verkäufe dieses Wertpapiers
        self.gesamtwert_aktuell = 0 # Stück * kurs_aktuell
        self.anteil_an_summe_gesamtwerte = 0  # wie hoch der Anteil dieser Depotposition an der Gesamtsumme der
                                              # im IMON befindlichen Positionen ist (in Prozent)
        self.kurs_aktuell = 0.0
        self.delta_proz = 0.0 #prozentualer Unterschied zwischen preisprostueck und kurs_aktuell
        self.fastInfo:FastInfo = None # fast_info aus yfinance.Ticker
        self.delta_kurs_percent = 0.0 # Kursentwicklung seit letztem Close in Prozent - nicht abhängig von der
                                      # eingestellten period
        # self.avg_kurs_50 = 0.0 # average Kurs letzte 50 Tage
        # self.avg_kurs_200 = 0.0  # average Kurs letzte 200 Tage
        self.depot_id = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""
        if valuedict:
            self.setFromDict( valuedict )

class XDelta( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.id = 0
        self.name = ""
        self.wkn = ""
        self.isin = ""
        self.ticker = ""
        self.delta_stck = 0
        self.delta_datum = ""
        self.preis_stck = 0.0
        self.order_summe = 0.0 # delta_stck * preis_stck (Kurs, zu dem gekauft wurde)
        self.verkauft_stck = 0 # wieviel Stück von einem früheren, bereits existenten Kauf-Satz verkauft wurden
        self.verkaufskosten = 0.0 # Kosten, die bei einem Verkauf anfallen. Werden steuerlich berücksichtigt bei der
                                  # Ermittlung des Veräußerungsgewinnes
        self.bemerkung = ""
        if valuedict:
            self.setFromDict( valuedict )

class XDividend( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.name = ""
        self.wkn = ""
        # self.isin = ""
        self.ticker = ""
        self.pay_day = "" # Datum der Dividendenzahlung
        self.div_pro_stck = 0.0 # Div.Zahlunge pro Stück
        self.div_summe = 0.0 # Div.Zahlung pro Stück * Stück unter Berücksichtigung des am Zahltag vorhandenen Bestands.
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
        self.letzte_aktualisierung = ""
        self.bank = ""
        self.depot_nr = ""
        self.depot_vrrkto = ""

class XExchangeRate(XBase):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.date:str = ""
        self.base:str = ""
        self.target:str = ""
        self.rate:float = 0.0
        if valuedict:
            self.setFromDict( valuedict )

class XAllokation(XBase):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.id:int = 0 # DB-ID
        self.wkn:str = ""
        self.typ:str = "" # "Land", "Sektor", "Firma"
        self.name:str = ""
        self.prozent:float = 0.0
        if valuedict:
            self.setFromDict( valuedict )
