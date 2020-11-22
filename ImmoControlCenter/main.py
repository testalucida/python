from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
#from mainwindow import MainWindow
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
        print('CLEAN EXIT')
        self._win.removeEventFilter(self)
        self._app.quit()

def main():
    app = QApplication()
    #app = MyApp()
    win = ImmoCenterMainWindow()
    ctrl = MainController( win )
    ctrl.onMainWindowAction( MainWindowAction.OPEN_MIETE_VIEW )
    ctrl.onMainWindowAction( MainWindowAction.OPEN_HGV_VIEW )

    # see: https://stackoverflow.com/questions/53097415/pyside2-connect-close-by-window-x-to-custom-exit-method
    shutDownFilter = ShutDownFilter(win, app)
    win.installEventFilter(shutDownFilter)
    win.show()

    app.exec_()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
