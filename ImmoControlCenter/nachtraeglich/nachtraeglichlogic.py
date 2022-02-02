import definitions
from business import BusinessLogic
from interfaces import XSonstAus, XMietobjektExt


class Nachtraeglich:
    def __init__(self):
        ## ACHTUNG: in definitions.py zuerst ROOT auf ändern,
        # sonst werden die Änderungen in der Test-Datenbank eingetragen.
        # !!!!!!!!!!!!!!!UND DANN WIEDER ZURÜCK ÄNDERN!!!!!!!!!!!!!
        return ## AUSKOMMENTIEREN
        self._busi = BusinessLogic.inst()

    def insertSonstigeAusgabe( self, x:XSonstAus ):
        if not x.master_id:
            ext:XMietobjektExt = self._busi.getMietobjektExt( x.mobj_id )
            x.master_id = ext.master_id
        self._busi.insertSonstigeAuszahlung( x )


def doInsertSonstAus( x:XSonstAus ):
    n = Nachtraeglich()
    try:
        n.insertSonstigeAusgabe( x )
        print( "done." )
    except Exception as ex:
        print( str( ex ) )

def insertReparatur():
    x = XSonstAus()
    x.mobj_id = "charlotte"
    x.kreditor = "Baufirma"
    x.betrag = -8587.72
    x.buchungsdatum = "2021-06-21"
    x.buchungsjahr = 2021
    x.umlegbar = 0
    x.werterhaltend = 0
    x.kostenart_lang = "Reparatur/Renovierung"
    x.buchungstext = "Gebäudedämmung./nEntnahme Rücklage gem. HGA 2020 vom 7.6.21"
    doInsertSonstAus( x )


def insertGrundsteuer():
    x = XSonstAus()
    x.mobj_id = "wilhelmmarx"
    x.kreditor = "Stadt Nürnberg"
    x.betrag = -32.02
    x.buchungsdatum = "2021-02-15"
    x.buchungsjahr = 2021
    x.umlegbar = 1
    x.werterhaltend = 0
    x.kostenart_lang = "Grundsteuer"
    x.buchungstext = "Grundsteuer; von Sparkasse"
    doInsertSonstAus( x )

insertReparatur()