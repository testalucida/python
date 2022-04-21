import datehelper
from anleihen.graphcreator import GraphCreator, DateBasedGraphCreator
from anleihen.graphdataprovider import GraphDataProvider
import sys

sys.path.append( "../common" )

def main():
    prov = GraphDataProvider()
    graphData = prov.getAnleiheData()
    graphCreator = DateBasedGraphCreator( graphData )
    graphCreator.showGraph()

if __name__ == "__main__":
    main()