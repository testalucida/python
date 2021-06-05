from typing import List

from PySide2.QtCore import QRect, QRectF
from PySide2.QtGui import QPainter, Qt
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import QDialog

from anlage_v.anlagev_interfaces import XAnlageV_Zeile


class AnlageV_Printer:
    def __init__( self ):
        self.printer = QPrinter()
        self.painter = QPainter()
        self._nCall = 0

    def print( self, anlageV_zeilen:List[XAnlageV_Zeile] ):
        if self._nCall > 0:
            self.printer.newPage()
        for zeile in anlageV_zeilen:
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
        self._nCall += 1

    def showPrintDialog( self ) -> bool:
        printDialog = QPrintDialog( self.printer )
        ret = printDialog.exec_()
        if ret == QDialog.Accepted:
            self._preparePrint()
            return True
        return False

    def _preparePrint( self ):
        self.painter.begin( self.printer )
        self.painter.setWindow( 0, 0, 210, 297 )
        self.painter.setViewport( 0, 0, self.printer.width(), self.printer.height() )

        font = self.painter.font()
        font.setPointSize( 4 )  # 6mm height
        self.painter.setFont( font )

    def end( self ):
        self.painter.end()