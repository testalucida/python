from PySide2.QtCore import QAbstractTableModel
from typing import Any

class IccTableModel( QAbstractTableModel ):
    def __init__(self):
        QAbstractTableModel.__init__( self )

    def isChanged( self ) -> bool:
        return True

    def getChanges( self ) -> Any:
        return None