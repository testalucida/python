import matplotlib
from pandas import DataFrame

from base.baseqtderivates import BaseGridLayout

matplotlib.use('Qt5Agg')
from PySide2.QtWidgets import QWidget, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

#############################################################
class InfoPanel( QWidget ):
    """
    Ein InfoPanel enthält alle Informationen zu einem Wertpapier (Aktie, Fonds- oder ETF-Anteil)
    und einen Graph, der die Kursentwicklung eines Zeitraums anzeigt.
    """
    def __init__(self):
        QWidget.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mplCanvas = MplCanvas()
        self._createGui()

    def _createGui( self ):
        l = self._layout
        l.addWidget( self._mplCanvas, 0, 0 )

    def plot( self, df:DataFrame ):
        df.plot( ax=self._mplCanvas.axes )

##########  TEST ###  TEST  ###################################################
def test():
    app = QApplication()
    ip = InfoPanel()
    df = pd.DataFrame( [
        [0, 10], [5, 15], [2, 20], [15, 25], [4, 10],
    ], columns=['A', 'B'] )
    ip.plot( df )
    ip.show()
    app.exec_()