from v2.icc.iccmainwindow import IccMainWindow


def main():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    mainwin = IccMainWindow( "DEVELOP" )
    mainwin.show()
    app.exec_()

if __name__ == "__main__":
    main()