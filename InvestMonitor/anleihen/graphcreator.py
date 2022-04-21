
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import drange
import numpy as np

from interface.interfaces import GraphData, DateBasedGraphData


class GraphCreator:
    def __init__( self, graphData:GraphData ):
        self.graphData = graphData
        self._titlefont = {'family':'serif', 'color':'blue', 'size':20}
        self._labelfont = {'color':'blue', 'size':14}

    def _prepareGraph( self ):
        plt.title( self.graphData.getTitle(), fontdict=self._titlefont, loc='left' )
        plt.xlabel( self.graphData.getXlabel(), fontdict=self._labelfont )
        plt.ylabel( self.graphData.getYlabel(), fontdict=self._labelfont )

    def showGraph( self ):
        self._prepareGraph()
        paths = self.graphData.getPaths()
        for path in paths:
            xvals = path.getXvalues()
            yvals = path.getYvalues()
            fmt = "o:" + path.getColor()
            label = path.getLegend()
            self._plot( xvals, yvals, fmt, label )
        plt.gcf().autofmt_xdate()
        plt.tick_params( axis='x', which='major', labelsize=8 )
        plt.legend()
        plt.tight_layout()
        plt.grid()
        plt.show()

    def _plot( self, xvals, yvals, fmt, label ):
        pass


class DateBasedGraphCreator( GraphCreator ):
    def __init__( self, graphData:DateBasedGraphData ):
        GraphCreator.__init__( self, graphData )

    def _plot( self, xvals, yvals, fmt, label ):
        plt.plot_date( xvals, yvals, fmt=fmt, label=label )





def test():
    d1 = datetime.datetime( 2021, 7, 2 )
    d2 = datetime.datetime( 2021, 7, 12 )
    delta = datetime.timedelta( hours=24 ) # delta: if 24: 1 day, 0:00:00; if 48: 2 days 0:00:00.
    #dates = drange( d1, d2, delta ) # contains a list containing 10 (if hours=24) or 5 (if hours=48)
                                    # num values representing a date each
    dates = [datetime.datetime( 2022, 3, 3 ),
             datetime.datetime( 2022, 3, 7 ),
             datetime.datetime( 2022, 3, 8 ),
             datetime.datetime( 2022, 3, 14 ),
             datetime.datetime( 2022, 3, 16 ),
             datetime.datetime( 2022, 3, 19 ),
             datetime.datetime( 2022, 3, 23 ),
             datetime.datetime( 2022, 4, 1 ),
             datetime.datetime( 2022, 4, 7 ),
             datetime.datetime( 2022, 4, 10 )]

    titlefont = {'family':'serif', 'color':'blue', 'size':20}
    labelfont = {'color':'blue', 'size':14}

    plt.title( "Kurse der DKB-Anleihen", fontdict=titlefont, loc='left' )
    #plt.xlabel( "Datum", fontdict=labelfont )
    plt.ylabel( "Kurs", fontdict=labelfont )

    #y = np.arange( len( dates ) )
    #yy = y ** 3
    kurse1 = [99.8, 100.0, 100.2, 99.4, 99.5, 100.8, 100.6, 101.0, 102.5, 99.1]
    plt.plot_date( dates, kurse1, fmt="o:y", label='Post Anleihe 16/24 (DE556992AB, N:300000, W:299000)' )
    kurse2 = [109.8, 97.0, 99.2, 100.4, 99.5, 100.0, 99.6, 103.0, 102.5, 99.1]
    plt.plot_date( dates, kurse2, fmt="o:%s" % "r", label='Mercedes' )

    plt.gcf().autofmt_xdate()

    plt.tick_params( axis='x', which='major', labelsize=8 )
    plt.legend()
    plt.tight_layout()
    plt.grid()
    plt.show()

