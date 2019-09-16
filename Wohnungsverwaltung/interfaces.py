from dictwrapper import DictWrapper, DictWrapperList

class XMtlHausgeld(DictWrapper):
    def __init__(self, dic: dict = None):
        self.mea_id = None
        self.gueltig_ab = None
        self.gueltig_bis = None
        self.hg_netto_abschlag = None
        DictWrapper.__init__(self, dic)

class XMtlHausgeldList(DictWrapperList):
    def __init__(self, klass: type, li: list = None):
        DictWrapperList.__init__(self, XMtlHausgeld, li)


class XHausgeldAdjustment(DictWrapper):
    def __init__(self, dic: dict = None):
        self.sea_id = None
        self.vj = None
        self.betrag = None
        self.art_id = None
        self.art = None
        self.ein_aus = None
        DictWrapper.__init__(self, dic)

class XHausgeldAdjustmentList(DictWrapperList):
    def __init__(self, klass: type, li: list = None):
        DictWrapperList.__init__(self, XHausgeldAdjustment, li)


class XSonstigeKosten(DictWrapper):
    def __init__(self, dic: dict = None):
        self.sea_id = None
        self.vj = None
        self.betrag = None
        DictWrapper.__init__(self, dic)

class XSonstigeKostenList(DictWrapperList):
    def __init__(self, klass: type, li: list = None):
        DictWrapperList.__init__(self, XSonstigeKosten, li)


class XZurechnung(DictWrapper):
    def __init__(self, dic: dict = None):
        self.steuerl_zurechng_mann = None
        self.steuerl_zurechng_frau = None
        DictWrapper.__init__(self, dic)

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