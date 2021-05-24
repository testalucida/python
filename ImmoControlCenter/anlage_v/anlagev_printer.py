from typing import List

from PySide2.QtCore import QRect, QRectF
from PySide2.QtGui import QPainter, Qt
from PySide2.QtPrintSupport import QPrinter

from anlage_v.anlagev_interfaces import XAnlageV_Zeile


class AnlageV_Printer:
    def __init__( self, anlageV_zeilen:List[XAnlageV_Zeile] ):
        self._zeilen = anlageV_zeilen
        self.printer = QPrinter()
        self.painter = QPainter()

    def print( self ):
        self._preparePrint()
        #x = 100
        #y = 204
        for zeile in self._zeilen:
            if zeile.rtl:
                # rechtsbündig drucken. Das ist bei Zahlen der Fall. Das angegebene Rechteck ist mit
                # 30 mm Breite auf jeden Fall breit genug.
                rect = QRectF( zeile.printX, zeile.printY, 30, 6 )
                self.painter.drawText( rect, Qt.AlignRight, zeile.value )
                #y += 10
            else:
                self.painter.drawText( zeile.printX, zeile.printY, zeile.value )
            if zeile.new_page_after:
                self.printer.newPage()

        self.painter.end()

    def _preparePrint( self ):
        self.painter.begin( self.printer )
        self.painter.setWindow( 0, 0, 210, 297 )
        self.painter.setViewport( 0, 0, self.printer.width(), self.printer.height() )

        font = self.painter.font()
        font.setPointSize( 4 )  # 6mm height
        self.painter.setFont( font );