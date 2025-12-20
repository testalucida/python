import datetime
from typing import List, Dict, Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout
import matplotlib.pyplot as plt

import datehelper
from base.baseqtderivates import BaseGridLayout, BaseComboBox, BaseLabel
from gui.mplcanvas import MplCanvas


class CurrenciesPanel(QFrame):
    """
    Ein Panel, das ein MplCanvas beinhaltet, auf dem verschiedene Währungen im Verhältnis zum Euro
    abgebildet werden.
    Außerdem (dar4über) eine ComboBox, mit der die ANzahl der anzuzeigenden Jahre eingestellt werden kann.
    Wird die ComboBox geändert, wird ein years_count_changed Signal emitted
    """
    years_count_changed = Signal(int)
    def __init__(self):
        QFrame.__init__( self )
        self.setWindowTitle( "Währungsentwicklung")
        self._layout = BaseGridLayout()
        self.setLayout(self._layout)
        self._cboYears:BaseComboBox = BaseComboBox()
        self._mplCanvas = MplCanvas()
        self._days:List = None
        self._currencyDict:Dict = None
        self._createGui()
        self.resize( self.sizeHint() )

    def _createGui( self ):
        l = self._layout
        hl = QHBoxLayout()
        r = c = 0
        l.addLayout(hl, r, c)
        hl.addWidget(BaseLabel("Angezeigte Jahre: "))
        self._cboYears.addItems(("1", "2", "3", "4", "5"))
        self._cboYears.setMaximumWidth(40)
        self._cboYears.currentIndexChanged.connect(self._onCboYearsChanged)
        hl.addWidget(self._cboYears, alignment=Qt.AlignmentFlag.AlignLeft)
        r +=1
        c = 0
        l.addWidget(self._mplCanvas, r, c, 1, 2 )

    def _onCboYearsChanged( self ):
        sYears = self._cboYears.itemText(self._cboYears.currentIndex())
        self.years_count_changed.emit( int(sYears))

    def _plot( self ):
        plt.tight_layout()
        self._mplCanvas.figure.subplots_adjust( top=0.9 )
        plt.setp( self._mplCanvas.ax1.get_xticklabels(), fontsize=8 )
        plt.setp( self._mplCanvas.ax1.get_yticklabels(), fontsize=8 )
        colors = ("black", "blue", "green", "red", "yellow")
        c = 0
        for key, valuelist in self._currencyDict.items():
            self._mplCanvas.ax1.plot( self._days, valuelist, color=colors[c], label="1€ -> %s" % key )
            c += 1
            if c >= len(colors): c = 0
        self._mplCanvas.ax1.legend( fontsize=8 )
        self._mplCanvas.ax1.grid()

    def setCurrencies( self, days:Iterable, currencies:Dict ):
        """
        @param days: Tage, für die das Währungsverhältnis angezeigt werden soll
        @param currencies: ein Dictionary mit folgendem Aufbau:
            key = <Currency>, value = Liste von floats.
        Der Index jedes days-Eintrags entspricht dem des float-Values in der jeweiligen Currency-Liste
        """
        self._days = days
        self._currencyDict = currencies
        self._mplCanvas.clear()
        self._plot()
        self._mplCanvas.draw()

def test():
    from PySide6.QtWidgets import QApplication
    today = datehelper.getCurrentDate()
    days = (datetime.datetime(2025,11,1,0),
         datetime.datetime(2025,11,2,0),
         datetime.datetime(2025,11,3,0),
         datetime.datetime(2025,11,4,0),
         datetime.datetime(2025,11,5,0))

    dic = {"USD" : (1.08, 1.09, 1.05, 1.02, 1.02),
           "CHF" : (1.10, 1.09, 1.12, 1.11, 1.10),
           "AUD" : (0.81, 0.79, 0.80, 0.82, 0.85)}
    app = QApplication()
    cp = CurrenciesPanel()
    cp.setCurrencies(days, dic)
    cp.show()
    app.exec()

if __name__ == '__main__':
    test()