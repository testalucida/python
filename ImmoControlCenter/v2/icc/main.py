from PySide2.QtWidgets import QApplication

from v2.icc.iccmainwindow import IccMainWindow
from v2.icc.maincontroller import MainController


def main():
    app = QApplication()
    mainCtrl = MainController( "DEVELOP" )
    mainwin = mainCtrl.createGui()
    mainwin.show()
    app.exec_()

if __name__ == "__main__":
    main()