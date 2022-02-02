from PySide2.QtWidgets import QWidget

from interfaces import XHandwerkerKurz


class IccCommonController:
    """
    Dieser Controller dient für verschiedene kleine Views wie z.B. die Handwerker-Neuanlage.
    Deshalb ist er nicht von IccController abgeleitet, sondern wird von den View-Controllern aufgerufen,
    die seine Dienste brauchen (z.B. GeplantController)
    """
    def __init__( self ):
        pass

    def controlHandwerkerNeu( self ):
        x = XHandwerkerKurz()