from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class MplCanvas(FigureCanvasQTAgg):
    # def __init__(self, width=5, height=4, dpi=100):
    #     self._width = width
    #     self._height = height
    #     self._dpi = dpi
    #     self._figure = Figure(figsize=(width, height), dpi=dpi)
    #     # https://www.geeksforgeeks.org/python/plot-multiple-plots-in-matplotlib/
    #     #self.axes = self._figure.add_subplot(111)
    #     self.axes = self._figure.subplots( 2 )
    #     # self.ax1 = self._figure.add_subplot( 1, 1, 1 )
    #     # self.ax2 = self._figure.add_subplot( 2, 1, 2 )
    #     #self.axes.grid()
    #     super(MplCanvas, self).__init__( self._figure )
    #
    #     self.toolbar = NavigationToolbar( self, self )
    def __init__(self, width=5, height=4, dpi=100):
        self._width = width
        self._height = height
        self._dpi = dpi
        self.figure = plt.figure( figsize=(width, height), dpi=dpi )
        # https://www.geeksforgeeks.org/python/plot-multiple-plots-in-matplotlib/
        self.ax1 = self.figure.add_subplot( 111 )
        # self.ax1 = self._figure.add_subplot(plt.subplot2grid( (4, 1), (0, 0), rowspan=1 ))
        # self.ax2 = self._figure.add_subplot(plt.subplot2grid( (4, 1), (1, 0), rowspan=3 ))
        super( MplCanvas, self ).__init__( self.figure )
        self.toolbar = NavigationToolbar( self, self )
        #plt.tight_layout()
        #self._figure.subplots_adjust( top=0.9 )
        # plt.setp( self.ax2.get_xticklabels(), fontsize=8 )
        # plt.setp( self.ax2.get_yticklabels(), fontsize=8 )
        #plt.setp( self.ax1.get_xticklabels(), fontsize=6 )
        #plt.setp( self.ax1.get_yticklabels(), fontsize=6 )


    def clear( self ):
        # da gibt es bessere Lösungen, z.B.:
        # https://stackoverflow.com/questions/19569052/matplotlib-how-to-remove-a-specific-line-or-curve
        # oder https://stackabuse.com/bytes/using-cla-clf-and-close-to-clear-a-plot-in-matplotlib/
        # self._figure.clear()
        # self._figure = Figure( figsize=(self._width, self._height), dpi=self._dpi )
        # self.figure = self._figure
        # self.axes = self._figure.add_subplot( 111 )
        # self.axes.grid()
        self.ax1.clear()
        # self.ax1.clear()
        # self.ax2.clear()
        self.draw()

    # def draw( self ):
    #     super().draw()
    #     rend = self.get_renderer()
    #     self._figure.draw( rend )

    def refresh( self ):
        super().resize( self._width, self._height )
