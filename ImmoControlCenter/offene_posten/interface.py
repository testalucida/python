from enum import Enum
from typing import Dict

from interfaces import setFromDict


class XOffenerPosten:
    def __init__( self, valuedict:Dict=None ):
        self.id = 0
        self.mv_id = ""  # Offener Posten bezieht sich entweder auf Mieter...
        self.vwg_id = 0  # ...oder auf Verwalter...
        self.firma = "" # ...oder auf Firma. Diese wird Freitext erfasst
        self.erfasst_am = ""
        self.gebucht_am = ""
        self.betrag = 0.0 # kleiner 0: ich schulde ; > 0: mir steht zu
        self.bemerkung = ""
        if valuedict:
            setFromDict( self, valuedict )
