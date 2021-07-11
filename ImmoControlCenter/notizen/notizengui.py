from PySide2.QtCore import Signal, QModelIndex
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QScrollArea, QVBoxLayout

from generictable_stuff.generictableviewdialog import EditableTableViewWidget
from icctablemodel import IccTableModel
from imagefactory import ImageFactory
from interfaces import XNotiz
from notizen.notizentablemodel import NotizenTableModel
from qtderivates import BaseEdit, BaseLabel

#######################  NotizEditor  ##########################
class NotizEditor( QWidget ):
    def __init__( self, notiz:XNotiz, parent=None ):


#######################  NotizenTableView  #####################
class NotizenTableView( EditableTableViewWidget ):
    """
    Tabelle mit Notizen (jede Row enstpricht einem XNotiz-Objekt
    """
    def __init__(self, model:NotizenTableModel=None, parent=None):
        EditableTableViewWidget.__init__( self, model, True, parent )

########################  NotizenView  ###########################
class NotizenView( QWidget ):
    saveNotiz = Signal()

    """
    Widget, das eine NotizenTableView enthält und zusätzlich einen Save-Button,
    um die Änderungen zu speichern
    """
    def __init__(self, model:NotizenTableModel=None, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self._btnSave = QPushButton( self )
        self._btnSave.clicked.connect( self._onSave )
        self._ntv = NotizenTableView( model=model, parent=parent )
        # self._ntv.createItem.connect( self._onCreateItem )
        # self._ntv.editItem.connect( self._onEditItem )
        # self._ntv.deleteItem.connect( self._onDeleteItem )
        self._createGui()

    def _createGui( self ):
        r = c = 0
        l = self._layout
        icon = ImageFactory.inst().getSaveIcon()
        self._btnSave.setIcon( icon )
        l.addWidget( self._btnSave, r, c, Qt.AlignLeft )
        r += 1
        l.addWidget( self._ntv, r, c )
        self.setLayout( self._layout )

    def _onSave( self ):
        self.saveNotiz.emit()

    def getNotizenTableView( self ) -> NotizenTableView:
        return self._ntv


def test():
    app = QApplication()
    v = NotizenView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()