import datetime
import datehelper
from anleihen.anleihedatareader import getAllDKBAnleihen
from interface.interfaces import  DateBasedGraphData, Path, Point

class GraphDataProvider:
    def __init__( self ):
        y = datehelper.getCurrentYear()

    def getAnleiheData( self ) -> DateBasedGraphData:
        """
        Provides a list of PopoTables each containing all anleihen on a particular day
        :return:
        """
        # get all Anleihen
        popotableList = getAllDKBAnleihen()
        l = len( popotableList )
        if l == 0:
            raise ValueError( "PopoTableList doesn't contain any PopoTable" )
        # # first and last date to show in the graph (x-axis)
        # firstdateiso = popotableList[0].getSnapshotDate()
        # lastdateiso = popotableList[l-1].getSnapshotDate()
        # firstdate = datehelper.getDateFromIsoString( firstdateiso )
        # lastdate = datehelper.getDateFromIsoString( lastdateiso )
        # delta = datetime.timedelta( hours=24 )
        # dates = drange( firstdate, lastdate, delta )

        #create a list containing all snaphots dates and instantiate a GraphData object using this list
        isodates = [d.getSnapshotDate() for d in popotableList]
        tmpdates = [datehelper.getDateFromIsoString( iso ) for iso in isodates]
        dates = [datetime.datetime( d.year, d.month, d.day ) for d in tmpdates]
        graphData = DateBasedGraphData( dates )
        graphData.setTitle( "Kurse der DKB Anleihen" )
        graphData.setYlabel( "Kurs" )
        colors = ["r", "b", "g", "y", "c", "k", "m"]
        last_used_color_idx = -1
        for popotable in popotableList:
            for popo in popotable.popoList:
                path = graphData.getPathById( popo.isin )
                if not path:
                    path = Path( popo.isin )
                    path.setLegend( popo.bezeichnung +
                                    " (" + popo.isin + ", N=" + str(popo.nennwert) + ", W=" + str(popo.kurswert) + ")" )
                    last_used_color_idx += 1
                    if last_used_color_idx >= len( colors ): last_used_color_idx = 0
                    path.setColor( colors[last_used_color_idx] )
                    graphData.addPath( path )
                idx = isodates.index( popotable.getSnapshotDate() )
                x = dates[idx]
                path.addPoint( Point(x, popo.kurs ) )

        return graphData




def test():
    prov = GraphDataProvider()
    prov.getAnleiheData()





