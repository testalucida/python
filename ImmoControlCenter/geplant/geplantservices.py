import jsonpickle
from typing import List
from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantucc import GeplantUcc
from interfaces import XGeplant
from returnvalue import ReturnValue


class GeplantServices:
    """
    Clientseitig. Wird vom Controller aufgerufen.
    Die lesenden Services erhalten JSON-Strings von den serverseitig korrespondierenden UCC-Methoden, wandeln diese
    in Objekte um und geben sie zurück an den Controller
    Die schreibenden Services erhalten Objekte vom Controller, wandeln diese in JSON-Strings um und geben sie weiter
    an die UCC-Methoden.
    """
    @staticmethod
    def getDistinctYears() -> List[int]:
        gucc = GeplantUcc()
        jsn = gucc.getDistinctYears()
        years = jsonpickle.decode( jsn )
        return years


    @staticmethod
    def getPlanungenModel( jahr:int=None) -> XBaseTableModel:
        gucc = GeplantUcc()
        # jsn = gucc.getPlanungen( jahr )
        # model = jsonpickle.decode( jsn )
        jsn = gucc.getPlanungen( jahr )
        planungslist = jsonpickle.decode( jsn )
        model = XBaseTableModel( planungslist, jahr )
        return model

    @staticmethod
    def save( x:XGeplant ):
        gucc = GeplantUcc()
        jsn = jsonpickle.encode( x )
        jsn = gucc.save( jsn )
        rv:ReturnValue = jsonpickle.decode( jsn )

def test2():
    klass = globals()["XBaseTableModel"]
    instance = klass()
    print( instance )

def test1():
    class A( object ):
        def __init__( self ):
            self.attr1 = "bla"

    class AA( A ):
        def __init__(self):
            A.__init__( self )
            self.attr2 = "blaa"
            self.attr3 = "blubb"

    a = A()
    jsn = jsonpickle.encode( a )
    a2 = jsonpickle.decode( jsn ) # a2 ist ein dict, kein AA :(
    print( a2 )

def test():
    years = GeplantServices.getDistinctYears()
    print( years )

    model = GeplantServices.getPlanungenModel( 2021 )
    print( model )