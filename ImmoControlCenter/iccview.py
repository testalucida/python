from abc import abstractmethod, ABC
from typing import Any

from PySide2.QtWidgets import QWidget, QTableView

class IccViewMeta( type(QWidget), type(ABC) ):
    pass

class IccView( QWidget, ABC, metaclass=IccViewMeta ):
    def __init__( self ):
        QWidget.__init__( self, None )


    @abstractmethod
    def getModel( self ) -> Any:
        pass

    @abstractmethod
    def setModel( self, model:Any ) ->None:
        pass

    @abstractmethod
    def addJahr( self, jahr:int ) -> None:
        pass

    @abstractmethod
    def getTableView( self ) -> QTableView:
        pass