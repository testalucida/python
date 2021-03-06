import sys
# sys.path.append( "/home/martin/Projects/python/common" )
from typing import Tuple, Dict, List

sys.path.append( "../common" )
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QMdiSubWindow
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from business import BusinessLogic
from maincontroller import MainController

class ShutDownFilter( QtCore.QObject ):
    def __init__(self, win:QWidget, app:QApplication ):
        QtCore.QObject.__init__(self)
        self._win = win
        self._app = app

    def eventFilter(self, obj, event) -> bool:
        if obj is self._win and event.type() == QtCore.QEvent.Close:
            self.quit_app()
            event.ignore()
            return True
        return super(ShutDownFilter, self).eventFilter(obj, event)

    def quit_app(self):
        # TODO: copy immo.db to all-inkl server
        geom = self._win.geometry()
        print('CLEAN EXIT. x=%d - y=%d - w=%d - h=%d' % (geom.x(), geom.y(), geom.width(), geom.height() ) )
        writeGeometryOnShutdown( geom.x(), geom.y(), geom.width(), geom.height() )
        self._win.removeEventFilter(self)
        self._app.quit()

def getGeometryOnLastShutdown() -> Dict:
    f = open( "icc_settings.txt", "r" )
    s = f.read()
    parts = s.split( "," )
    d = dict()
    d["x"] = int( parts[0] )
    d["y"] = int( parts[1] )
    d["w"] = int( parts[2] )
    d["h"] = int( parts[3] )
    return d

def writeGeometryOnShutdown( x, y, w, h ) -> None:
    f = open( "icc_settings.txt", "w" )
    s = str( x ) + "," + str( y ) + "," + str( w ) + "," + str( h )
    f.write( s )

def main():
    app = QApplication()

    win = ImmoCenterMainWindow()
    # see: https://stackoverflow.com/questions/53097415/pyside2-connect-close-by-window-x-to-custom-exit-method
    shutDownFilter = ShutDownFilter(win, app)
    win.installEventFilter(shutDownFilter)

    win.show()
    try:
        pos_size = getGeometryOnLastShutdown()
        win.move( pos_size["x"], pos_size["y"] )
        win.resize( pos_size["w"], pos_size["h"] )
    except:
        win.resize( 1900, 1000 )

    ctrl = MainController( win )
    ctrl.showStartViews()
    #win.resize( 1901, 1000 )

    app.exec_()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
