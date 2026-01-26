from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QApplication, QSpacerItem, QSizePolicy

from base.baseqtderivates import BaseWidget, BaseGridLayout, BaseLabel
from base.basetableview import BaseTableView
from interface.interfaces import XAllocationViewModel


class AllocationTableView(BaseTableView):
    def __init__(self):
        BaseTableView.__init__(self)

class AllocationView(BaseWidget):
    def __init__(self):
        BaseWidget.__init__(self)
        self._model:XAllocationViewModel = None
        self.setWindowTitle("Allokationen des Depots")
        self._layout = BaseGridLayout()
        self.setLayout(self._layout)
        self._lblGesamtwertLabel = BaseLabel( "Gesamtwert" )
        self._lblLaender = BaseLabel("Länder")
        self._lblSektoren = BaseLabel("Sektoren")
        self._lblFirmen = BaseLabel("Firmen")
        self._lblGesamtwertValue = BaseLabel()
        self._tvLaender = AllocationTableView()
        self._tvSektoren = AllocationTableView()
        self._tvFirmen = AllocationTableView()
        self._createGui()

    def _createGui( self ):
        l = self._layout
        r = c = 0
        vspacer = QtWidgets.QSpacerItem( 10, 20, vData=QSizePolicy.Policy.Fixed )
        l.addItem( vspacer, r, c )
        r += 1
        c = 0
        l.addWidget( self._lblGesamtwertLabel, r, c )
        c += 1
        hl = QHBoxLayout()
        hl.addWidget(self._lblGesamtwertValue)
        self._lblGesamtwertValue.setFont(QFont("Ubuntu", 16, QFont.Weight.Bold))
        hl.addWidget(BaseLabel("Euro"))
        l.addLayout(hl, r, c, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        r += 1
        c = 0
        vspacer = QtWidgets.QSpacerItem( 10, 30, vData=QSizePolicy.Policy.Fixed )
        l.addItem(vspacer, r, c)
        r += 1
        c = 0
        l.addWidget(self._lblLaender, r, c)
        c += 1
        l.addWidget(self._tvLaender, r, c)
        r += 1
        c = 0
        l.addWidget(self._lblSektoren, r, c)
        c += 1
        l.addWidget( self._tvSektoren, r, c )
        r += 1
        c = 0
        l.addWidget(self._lblFirmen, r, c)
        c += 1
        l.addWidget(self._tvFirmen, r, c)
        r += 1
        c = 0
        #vspacer = QtWidgets.QSpacerItem(10, 10, vData=QSizePolicy.Policy.Expanding)
        #l.addItem(vspacer, r, c)

    def setAllocationViewModel( self, model:XAllocationViewModel ):
        self._model = model
        self._dataToGui()

    def _dataToGui( self ):
        m = self._model
        self._lblGesamtwertValue.setValue(str(m.depot_gesamtwert))
        self._tvLaender.setModel(m.stmLaender)
        self._tvSektoren.setModel(m.stmSektoren)
        self._tvFirmen.setModel(m.stmFirmen)


def test():
    from logic.imonlogic import testGetAllocationViewModel
    app = QApplication()
    model = testGetAllocationViewModel()
    v = AllocationView()
    v.setAllocationViewModel(model)
    v.show()
    app.exec()

if __name__ == "__main__":
    test()
