from typing import List

import jsonpickle

from icc.icclogic import IccLogic
from interfaces import XHandwerkerKurz
from mietobjekt.mietobjektucc import MietobjektUcc
from returnvalue import ReturnValue


class IccUcc:
    """
    Serverseitig (simuliert).
    Hier laufen ALLE Requests vom Client ein.
    Allgemeine Requests wie getMasterobjektNamen() werden hier direkt behandelt,
    objektspezifische werden an die jeweiligen UCC weitergeleitet.
    Werden vom clientseitigen Service Aufrufparameter mitgegeben, sind diese im json-Format und müssen erst
    decodiert werden.
    Returnwerte werden in ReturnValue-Objekte gesteckt, die dann in json-strings encodiert und zurückgegeben werden.
    Die Rückgabe erfolgt in dieser Simulation per return, in Realität müsste hier eine webserverspezifische Übergabe
    erfolgen.
    """

    @staticmethod
    def getHandwerkerNachBranchen() -> str:
        """
        Liefert Firmennamen geordnet nach Branchen
        :return: einen json-encoded ReturnValue
        """
        logic = IccLogic()
        try:
            firmenlist = logic.getHandwerkerNachBranchen()
            rv = ReturnValue.fromValue( firmenlist )
        except Exception as ex:
            rv = ReturnValue.fromException( ex )
        jsn = jsonpickle.encode( rv )
        return jsn

