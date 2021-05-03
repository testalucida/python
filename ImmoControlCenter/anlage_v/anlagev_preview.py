import sys
from typing import List

import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QFont, QPainter, QPen, Qt
from PySide2.QtWidgets import QGraphicsView, QMainWindow, QApplication

from anlage_v.anlagev_interfaces import XAnlageV_Zeile


class AnlageV_Preview( QMainWindow ):
    def __init__(self, zeileList:List[XAnlageV_Zeile] ):
        super().__init__()
        self._zeilen = zeileList
        self.title = "Anlage V Preview"
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize( 900, 900 )
        #self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent( self, event: PySide2.QtGui.QPaintEvent ):
        painter = QPainter( self )
        for z in self._zeilen:
            print( "drawing at %d, %d: '%s'" % (z.printX, z.printY, z.value ) )
            painter.drawText( z.printX * 3, z.printY * 3, z.value )

    def paintEvent__( self, event:PySide2.QtGui.QPaintEvent ):
        painter = QPainter( self )
        painter.setPen( QPen( Qt.green, 8, Qt.DashLine ) )
        painter.drawEllipse( 40, 40, 400, 400 )
        painter.drawText( 50, 100, "kjfdslkjfsd")

def test():
     app = QApplication()
     window = AnlageV_Preview()
     sys.exit( app.exec_() )


if __name__ == "__main__":
    test()