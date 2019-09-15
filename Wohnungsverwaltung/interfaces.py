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

