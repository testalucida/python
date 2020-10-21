from PySide2.QtWidgets import QApplication
from mainwindow import MainWindow
from business import BusinessLogic
from controller import Controller


def main():
    app = QApplication()
    win = MainWindow()

    busi = BusinessLogic()
    busi.prepare()

    ctrl = Controller( win, busi )
    ctrl.startWork()

    win.show()
    app.exec_()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
