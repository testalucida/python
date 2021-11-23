from typing import List

from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QApplication


class XBaseGuiInfo:
    def __init__( self ):
        self.attr_name = ""
        self.widget:QWidget = None # das Widget, das im View an der gewünschten Stelle angezeigt wird
        self.label = "" # Text, der in der View links vom Widget angezeigt wird
        self.tooltip = ""
        self.row = 0
        self.column = 0
        self.isActive:bool = True # ob das Widget aktiv ist
        self.stylesheet = "" # Ein String, der der QWidget.setStyleSheet-Methode übergeben wird, z.B.:
                             # QWidget.setStyleSheet( "background: solid white;" ), oder
                             # "QLabel { background-color : gray; color : white; }"


#########  XBaseView ######################
class XBaseView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )


#########  XBaseGuiBuilder ####################
class XBaseGuiBuilder:
    def __init__( self, guiInfoList:List[XBaseGuiInfo]=None ):
        self._guiInfoList:List[XBaseGuiInfo] = guiInfoList
        if not guiInfoList:
            self._guiInfoList = list()
        self._view:XBaseView = None
        self._layout:QGridLayout = None

    def addGuiInfo( self, attr_name:str, widget:QWidget, row:int, column:int, isActive:bool=True, stylesheet:str="" ):
        x = XBaseGuiInfo()
        x.attr_name = attr_name
        x.widget = widget
        x.row = row
        x.column = column
        x.isActive = isActive
        x.stylesheet = stylesheet
        self._guiInfoList.append( x )

    def addGuiInfo2( self, guiInfo:XBaseGuiInfo ):
        self._guiInfoList.append( guiInfo )

    def createView( self, parent=None ) -> XBaseView:
        self._view = XBaseView( parent )
        self._layout = QGridLayout()
        self._view.setLayout( self._layout )
        self._populateView()
        return self._view

    def _populateView( self ):
        for gi in self._guiInfoList:
            self._layout.addWidget( gi.widget, gi.row, gi.column )


def test():
    app = QApplication()
    builder = XBaseGuiBuilder()
    x = XBaseGuiInfo()
    x.attr_name = "_name"
    x.widget = QLabel( "dies ist ein Label" )
    x.label = "Label1: "
    x.tooltip = "Tooltip1"
    x.row = 0
    x.column = 0
    builder.addGuiInfo2( x )
    view = builder.createView()
    view.show()
    app.exec_()

if __name__ == "__main__":
    test()