import os

_mywidgets_imagepath = ''

def _providePaths():
    global _mywidgets_imagepath
    scriptpath = os.path.realpath(__file__)
    scriptpath = scriptpath.replace('/paths.py', '')
    _mywidgets_imagepath = scriptpath + '/images'

_providePaths()

def getMyWidgetsImagePath() -> str:
    global _mywidgets_imagepath
    return _mywidgets_imagepath