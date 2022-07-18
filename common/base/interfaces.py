from typing import Dict, Any, List

class XBase:
    """
    Die Mutter aller Interfaces.
    Jedes Interface sollte von XBase abgeleitet werden, z.B. weil es einen DB-Lesezugriff gibt,
    der die gelesenen DB-Spalten einer DB-Row direkt in ein passendes von XBase abgeleitetes Interface verpackt.
    Außerdem werden die get- und setValue Methoden im BaseTableModel benötigt.

    XBase wird *intensivst* vom ImmoControlCenter benutzt, also Vorsicht beim Ändern.
    """
    def __init__( self, valuedict:Dict=None ):
        if valuedict:
            self.setFromDict( valuedict )

    def getValue( self, key ) -> Any:
        return self.__dict__[key]

    def setValue( self, key, value ):
        self.__dict__[key] = value

    def setFromDict( self, d: Dict ):
        _d = self.__dict__
        for k, v in d.items():
            _d[k] = v

    def equals( self, other ) -> bool:
        if other is None: return False
        return True if self.__dict__ == other.__dict__ else False

    def getKeys( self ) -> List:
        return list( self.__dict__.keys() )


class XAttribute( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )
        self.key = ""
        self.type = "" # one of int, float, string
        self.label = ""
        self.value = None
        self.options = list()
        self.editable = True

class TestItem( XBase ):
    def __init__( self ):
        XBase.__init__( self )
        self.nachname = ""
        self.vorname = ""
        self.plz = ""
        self.ort = ""
        self.str = ""
        self.alter = 0
        self.groesse = 0