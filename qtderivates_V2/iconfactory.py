import os

from PySide2.QtGui import QIcon

class UsedIcons:
    __instance = None
    __icons = dict()

    @staticmethod
    def inst():
        if UsedIcons.__instance == None:
            UsedIcons()
        return UsedIcons.__instance

    def __init__( self ):
        if UsedIcons.__instance != None:
            raise Exception( "UsedIcons is a singleton!" )
        UsedIcons.__instance = self

    def getIcon( self, path ) -> QIcon:
        try:
            return UsedIcons.__icons[path]
        except:
            icon = QIcon( path )
            UsedIcons.__icons[path] = icon
            return icon


class IconFactory:
    def __init__( self ):
        self._icons = UsedIcons.inst()

    def getIcon( self, path ) -> QIcon:
        return self._icons.getIcon( path )