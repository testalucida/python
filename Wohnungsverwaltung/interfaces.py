from typing import Dict, List, Text
from xinterface import XInterface, XInterfaceList

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