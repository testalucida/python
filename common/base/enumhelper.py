from enum import Enum
from typing import Any


class TestEnu( Enum ):
    m1 = "mem1"
    m2 = "mem2"

def getEnumFromValue( enu:Enum, value: Any ):
    for m in enu:
        #print( m.name, ": ", m.value )
        if m.value == value:
            return m

def test():
    e = getEnumFromValue( TestEnu, "mem2" )
    print( e )