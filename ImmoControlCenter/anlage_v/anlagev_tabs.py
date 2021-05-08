from PySide2 import QtWidgets
from PySide2.QtCore import QSize, Qt
from PySide2.QtWidgets import QApplication, QTabWidget, QHBoxLayout

from anlage_v.anlagev_view import AnlageVView, ToolbarButton


class AnlageVTabs( QTabWidget ):
    def __init__(self, parent=None ):
        QTabWidget.__init__(self, parent )


def test():
    app = QApplication()
    tabs = AnlageVTabs()
    v1 = AnlageVView()
    v2 = AnlageVView()
    tabs.addTab( v1, "Erste AnlageV" )
    tabs.addTab( v2, "Zweite AnlageV" )
    tabs.show()
    app.exec_()

if __name__ == "__main__":
    test()