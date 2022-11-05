from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication

from v2.icc.iccmainwindow import IccMainWindow
from v2.icc.maincontroller import MainController


def main():
    app = QApplication()
    mainCtrl = MainController( "DEVELOP" )
    mainwin = mainCtrl.createGui()
    mainwin.show()
    # w = mainwin.getPreferredWidth()
    # h = mainwin.height()
    # mainwin.resize( QSize(w, h) )
    app.exec_()

if __name__ == "__main__":
    main()