from PySide2.QtWidgets import QMdiSubWindow, QWidget
from typing import Any

class IccSubWindow( QMdiSubWindow ):
    def __init__( self, widget:QWidget, title:str, id:Any ):
        QMdiSubWindow.__init__( self )
        self._id = id
        self.setWidget( widget )
        self.setWindowTitle( title )

    def getId( self ) -> Any:
        return self._id