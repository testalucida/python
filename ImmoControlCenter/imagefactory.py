import os

from PySide2.QtGui import QIcon


class ImageFactory:
    __instance = None
    _imagePath = ""
    _okIcon:QIcon = None
    _nokIcon:QIcon = None
    _printIcon:QIcon = None
    _printAllIcon:QIcon = None
    _saveIcon:QIcon = None
    _openIcon:QIcon = None

    @staticmethod
    def inst():
        if ImageFactory.__instance == None:
            ImageFactory()
        return ImageFactory.__instance

    def __init__(self):
        if ImageFactory.__instance != None:
            raise  Exception( "ImageFactory is a singleton!" )
        ImageFactory.__instance = self
        path = os.getcwd()
        if path.endswith( "ImmoControlCenter" ):
            self._imagePath = "./images/"
        else:
            self._imagePath = "../images/"

    def getOkIcon(self) -> QIcon:
        if self._okIcon == None:
            self._okIcon = QIcon( self._imagePath + "greensquare20x20.png")
        return self._okIcon

    def getNokIcon(self) -> QIcon:
        if self._nokIcon == None:
            self._nokIcon = QIcon(self._imagePath + "redsquare20x20.png")
        return self._nokIcon

    def getOpenIcon(self) -> QIcon:
        if self._openIcon == None:
            self._openIcon = QIcon(self._imagePath + "open.png")
        return self._openIcon

    def getPrintIcon( self ) -> QIcon:
        path = os.getcwd()
        print( path )
        if self._printIcon == None:
            self._printIcon = QIcon( self._imagePath + "print_30.png" )
        return self._printIcon

    def getPrintAllIcon( self ) -> QIcon:
        path = os.getcwd()
        print( path )
        if self._printAllIcon == None:
            self._printAllIcon = QIcon( self._imagePath + "printall_30.png" )
        return self._printAllIcon

    def getSaveIcon( self ) -> QIcon:
        if self._saveIcon == None:
            self._saveIcon = QIcon( self._imagePath + "save_30.png" )
        return self._saveIcon

