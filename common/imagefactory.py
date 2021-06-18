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
    _plusIcon:QIcon = None
    _deleteIcon:QIcon = None
    _editIcon:QIcon = None

    @staticmethod
    def inst():
        if ImageFactory.__instance == None:
            ImageFactory()
        return ImageFactory.__instance

    def __init__(self):
        if ImageFactory.__instance != None:
            raise  Exception( "ImageFactory is a singleton!" )
        ImageFactory.__instance = self
        self._setImagePath()

        # path = os.getcwd()
        # if path.endswith( "ImmoControlCenter" ):
        #     self._imagePath = "./images/"
        # else:
        #     self._imagePath = "../images/"

    def _setImagePath( self ):
        """
        reads resources.txt and sets self._imagePath
        :return:
        """
        cwd = os.getcwd()
        f = open( "./resources.txt", "r" )
        lines = f.readlines()
        for l in lines:
            if l.startswith( "imagepath" ):
                parts = l.split( "=" )
                self._imagePath = parts[1][:-1] #truncate newline
                f.close()
                return
        raise Exception( "ImageFactory: cant find imagepath in resources.txt" )

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

    def getPlusIcon(self) -> QIcon:
        if self._plusIcon == None:
            self._plusIcon = QIcon(self._imagePath + "plus_30x30.png")
        return self._plusIcon

    def getEditIcon(self) -> QIcon:
        if self._editIcon == None:
            self._editIcon = QIcon(self._imagePath + "edit.png")
        return self._editIcon

    def getDeleteIcon(self) -> QIcon:
        if self._deleteIcon == None:
            self._deleteIcon = QIcon(self._imagePath + "cancel.png")
        return self._deleteIcon


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

