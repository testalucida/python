from typing import List, Dict

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollMiete, XSollHausgeld, XVerwaltung


class HausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )


##################################################################################

def test():
    data = HausgeldData()
    # l = data.getSollHausgelder( 2022 )
    #print( l )