import sys

from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QSplashScreen
sys.path.append( "../" )
sys.path.append( "../common" )
print( "sys.path: ", sys.path )
from controller.maincontroller import MainController
from imon.definitions import ICON_DIR



def main():
    app = QApplication( sys.argv )
    pixmap = QPixmap( ICON_DIR + "splash.png" )
    splash = QSplashScreen( pixmap )
    splash.show()
    app.processEvents()
    ctrl = MainController()
    win = ctrl.createMainWindow()
    win.show()
    splash.finish( win )
    return app.exec_()

if __name__ == "__main__":
    main()