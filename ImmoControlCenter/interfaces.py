from typing import Dict

class XBase:
    def __init__( self, valuedict:Dict=None ):
        if valuedict:
            self.setFromDict( valuedict )

    def setFromDict( self, d: Dict ):
        _d = self.__dict__
        for k, v in d.items():
            _d[k] = v

class XServiceLeistung( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    kreditor:str = ""
    master_id:int = 0
    name:str = ""
    mobj_id:str = ""
    buchungstext:str = ""
    umlegbar:int = 0

class XSonstAus( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    saus_id:int = 0
    master_id:int = 0
    master_name:str = ""
    mobj_id:str = ""
    kreditor:str = ""
    rgnr:str = ""
    rgdatum:str = ""
    rgtext:str = ""  # der Text auf der Rechnung
    betrag:float = 0.0
    umlegbar:bool = False
    werterhaltend:bool = False
    buchungsdatum:str = ""
    buchungsjahr:int = 0
    buchungstext:str = "" # der Text auf dem Buchungsbeleg, der bei öfftl. Providern identifizierend ist. (Kundennummer, Vertragsnummer etc.)

def printX( x:XSonstAus ):
    print( x )
    d = x.__dict__
    for k, v in d.items():
        print( k, ": ", v )

def test():
    x = XSonstAus()
    x.saus_id = 1
    x.kreditor = "K. Frantz"
    x.master_id = 11
    x.mobj_id = "kleist_01"
    printX( x )

    x2 = XSonstAus()
    d = {
        "saus_id": 20,
        "master_id": "HOM_Remigius",
        "mobj_id": "remigius",
        "kreditor": "Aloysius",
        "rgnr": "ABC2020_6t543",
        "rgdatum": "2020-10-31",
        "betrag": 546.78
    }
    x2.setFromDict( d )
    printX( x2 )

    print( "---------------------------" )
    x3 = XSonstAus( d )
    printX( x3 )

if __name__ == "__main__":
    test()