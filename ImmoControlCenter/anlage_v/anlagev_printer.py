from typing import List

from PySide2.QtGui import QPainter
from PySide2.QtPrintSupport import QPrinter

from anlage_v.anlagev_interfaces import XAnlageV_Zeile


class AnlageV_Printer:
    def __init__( self, anlageV_zeilen:List[XAnlageV_Zeile] ):
        self._zeilen = anlageV_zeilen
        self.printer = QPrinter()
        self.painter = QPainter()

    def print( self ):
        self._preparePrint()
        for zeile in self._zeilen:
            if zeile.printFlag == True:
                print( "printing '%s'" % (zeile.value) )
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