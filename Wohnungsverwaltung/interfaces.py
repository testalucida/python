from typing import Dict, List, Text
from enum import Enum, IntEnum
from xinterface import XInterface, XInterfaceList

Vergleichswert = IntEnum('Vergleichswert',
                         'nettomiete nk_voraus hg_voraus rechng '
                         'nk_abrechng hg_abrechng '
                         'ergebnis '
                         'sonderumlage '
                         'nettomiete_qm nk_qm '
                         'hg_netto_qm rueck_qm hg_ges_qm')

class XEinAusJahr():
    def __init__(self):
        self.netto_miete = 0
        self.nk_abschlag = 0
        self.hg_abschlag = 0

class XSonstigeJahressummen():
    def __init__(self):
        self.nk_abrechnung = 0
        self.hg_abrechnung = 0
        self.sonst_kosten = 0
        self.sonderumlagen = 0
        self.abloese = 0

class XJahresdaten():
    def __init__(self):
        self.jahr = 0
        self.whg_id = 0
        self.netto_miete = 0
        self.nk_abschlag = 0
        self.hg_abschlag = 0
        self.rechng = 0
        self.nk_abrechng = 0
        self.hg_abrechng = 0
        self.sonst_kosten = 0
        self.ergebnis = 0
        self.sonderumlagen = 0
        self.netto_miete_qm = 0
        self.nk_qm = 0
        self.hg_netto_qm = 0
        self.ruecklage_qm = 0
        self.hg_ges_qm = 0

class XMtlEinAusJahr(XInterface):
    def __init__(self, dic:Dict[str, str] = None):
        self.jahr = 0
        self.whg_id = 0
        self.gueltig_ab = ''
        self.gueltig_bis = ''
        self.netto_miete = 0.0
        self.nk_abschlag = 0.0
        self.hg_netto_abschlag = 0.0
        self.ruecklage_zufuehr = 0.0
        self.hg_brutto = 0.0
        XInterface.__init__(self, dic)

class XMtlEinAusJahrList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XMtlEinAusJahr, li)

class XRechnungKurz(XInterface):
    def __init__(self, dic:Dict[str, str] = None):
        self.jahr = 0
        self.whg_id = 0
        self.betrag = 0.0
        self.verteilung_jahre = 0
        self.year_bezahlt_am = 0
        XInterface.__init__(self, dic)

class XRechnungKurzList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XRechnungKurz, li)

class XSonstigeEinAusJahr(XInterface):
    def __init__(self, dic:Dict[str, str] = None):
        self.jahr = 0
        self.whg_id = 0
        self.betrag = 0.0
        self.ein_aus = ''
        self.art_kurz = ''
        XInterface.__init__(self, dic)

class XSonstigeEinAusJahrList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XSonstigeEinAusJahr, li)

class XMietverhaeltnis(XInterface):
    def __init__(self, dic: Dict[str, str] = None):
        self.mv_id = -1
        self.whg_id = -1
        # Identifikation der Wohnung
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.whg_bez = ''
        # Mieterdaten
        self.anrede = ''
        self.name = ''
        self.vorname = ''
        self.geboren_am = ''
        self.ausweis_id = ''
        self.telefon = ''
        self.mailto = ''
        self.iban = '' # Konto des Mieters
        # Mietverhältnisdaten
        self.vermietet_ab = ''
        self.vermietet_bis = ''
        self.kaution = -1
        self.kaution_angelegt_bei = ''
        self.inserat_text = ''
        self.inseriert_bei = ''
        self.bemerkung = ''
        XInterface.__init__(self, dic)

class XMietverhaeltnisList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XMietverhaeltnis, li)

class XVermieter(XInterface):
    def __init__(self, dic: Dict[str, str] = None):
        self.vermieter_id = 0
        self.name = ''
        self.vorname = ''
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.steuernummer = ''
        if not dic:
            dic = self.__dict__
        XInterface.__init__(self, dic)

class XVermieterList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XVermieter, li)

class XVerwalter(XInterface):
    def __init__(self, dic: Dict[str, str] = None):
        self.verwalter_id = 0
        self.firma = ''
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.telefon = ''
        self.email = ''
        if not dic:
            dic = self.__dict__
        XInterface.__init__(self, dic)

class XVerwalterList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XVerwalter, li)

class XWohnungDaten(XInterface):
    def __init__(self, dic: Dict[str, str] = None):
        self.whg_id = -1
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.whg_bez = ''
        self.angeschafft_am = ''
        self.einhwert_az = ''
        self.verwalter = '' #textual verwalter identification like 'Nittel, Nürnberg'
        self.vermieter = '' #textual vermieter identification like 'Martin Kendel, Schellenberg'
        self.verwalter_id = -1 #database id
        self.vermieter_id = -1 #database id
        if not dic:
            dic = self.__dict__
        XInterface.__init__(self, dic)

class XWohnungDetails(XInterface):
    def __init__(self, dic: Dict[str, str] = None):
        self.whg_id = -1
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.whg_bez = ''
        self.etage = 0
        self.anteil = 0
        self.iban_weg = ''
        self.zimmer = 0.0
        self.kueche = ''
        self.ebk = ''
        self.kuechengeraete = ''
        self.balkon = ''
        self.heizung = ''
        self.qm = 0
        self.bemerkung = ''
        self.tageslichtbad = ''
        self.badewanne = ''
        self.dusche = ''
        self.bidet = ''
        self.kellerabteil = ''
        self.aufzug = ''
        self.garage = ''
        XInterface.__init__(self, dic)

class XImmoStammdaten(XInterface):
    def __init__(self, dic: Dict[str, str]):
        self.name: str = ''
        self.vorname: str = ''
        self.steuernummer: str = ''
        self.strasse: str = ''
        self.plz: str = ''
        self.ort: str = ''
        self.whg_bez: str = ''
        self.qm: str  = ''
        self.angeschafft_am: str = ''
        self.einhwert_az: str = ''
        self.fewontzg: bool = ''
        self.isverwandt: bool = ''
        XInterface.__init__(self, dic)

class XMtlEinnahmen(XInterface):
    def __init__(self, dic: Dict[str, str]):
        self.gueltig_ab = ''
        self.gueltig_bis = ''
        self.netto_miete = ''
        self.nk_abschlag = ''
        XInterface.__init__(self, dic)

class XMtlEinnahmenList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XMtlEinnahmen, li)

class XAfa(XInterface):
    def __init__(self, dic: Dict[str, str]):
        self.lin_deg_knz = ''
        self.afa_wie_vorjahr = ''
        self.prozent = ''
        self.betrag = ''
        XInterface.__init__(self, dic)

class XMtlHausgeld(XInterface):
    def __init__(self, dic: dict = None):
        self.mea_id = None
        self.gueltig_ab = None
        self.gueltig_bis = None
        self.hg_netto_abschlag = None
        XInterface.__init__(self, dic)

class XMtlHausgeldList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XMtlHausgeld, li)

class XHausgeldAdjustment(XInterface):
    def __init__(self, dic: dict = None):
        self.sea_id = None
        self.vj = None
        self.betrag = None
        self.art_id = None
        self.art = None
        self.ein_aus = None
        XInterface.__init__(self, dic)

class XHausgeldAdjustmentList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XHausgeldAdjustment, li)

class XSonstigeKosten(XInterface):
    def __init__(self, dic: dict = None):
        self.sea_id = None
        self.vj = None
        self.betrag = None
        XInterface.__init__(self, dic)

class XSonstigeKostenList(XInterfaceList):
    def __init__(self, klass: type, li: list = None):
        XInterfaceList.__init__(self, XSonstigeKosten, li)


class XZurechnung(XInterface):
    def __init__(self, dic: dict = None):
        self.steuerl_zurechng_mann = None
        self.steuerl_zurechng_frau = None
        XInterface.__init__(self, dic)

class XErhaltungsaufwand:
    def __init__(self):
        self.voll_abzuziehen = 0
        self.vj_gesamtaufwand = 0
        self.abzuziehen_vj = 0
        self.abzuziehen_aus_vj_minus_4 = 0
        self.abzuziehen_aus_vj_minus_3 = 0
        self.abzuziehen_aus_vj_minus_2 = 0
        self.abzuziehen_aus_vj_minus_1 = 0
        self._switch = {
            0: 'abzuziehen_vj',
            1: 'abzuziehen_aus_vj_minus_1',
            2: 'abzuziehen_aus_vj_minus_2',
            3: 'abzuziehen_aus_vj_minus_3',
            4: 'abzuziehen_aus_vj_minus_4'
        }

    def addto_abzuziehen_aus_vj_minus(self, years: int, betrag: float) -> None:
        self.__dict__[self._switch.get(years)] += betrag

    def get_abzuziehen_aus_vj_minus(self, years: int) -> float or int:
        return self.__dict__[self._switch.get(years)]

    def roundAufwaende(self):
        for v in self._switch.values():
            self.__dict__[v] = round(self.__dict__[v])




def test():
    ea = XErhaltungsaufwand()
    ea.addto_abzuziehen_aus_vj_minus(2, 112.34)
    ea.roundAufwaende()
    n = ea.get_abzuziehen_aus_vj_minus(2)
    print(n)


if __name__ == '__main__':
    test()