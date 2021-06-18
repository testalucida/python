from PySide2 import QtWidgets
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QComboBox, QApplication

from generictable_stuff.generictableviewdialog import GenericTableViewDialog
from offene_posten.interface import XOffenerPosten
from offene_posten.offenepostentablemodel import OffenePostenTableModel


class OffenePostenDialog( GenericTableViewDialog ):
    def __init__(self, model:OffenePostenTableModel ):
        GenericTableViewDialog.__init__( self, model=model, isEditable=True )
        self.setWindowTitle( "Offene Posten" )

        self.resize(1800, 1280)

def test():
    app = QApplication()

    l = list()
    x = XOffenerPosten()
    x.id = 1
    x.mv_id = "Müller"
    x.erfasst_am = "2021-06-03"
    x.betrag = "123.45"
    x.bemerkung = "steht aus"
    l.append( x )

    x = XOffenerPosten()
    x.id = 2
    x.mv_id = "Himpfelhuber-Förrenschmidt"
    x.erfasst_am = "2021-06-03"
    x.betrag = "123.45"
    x.bemerkung = "steht aus trotz sechzehnmaliger Mahnung und Drohung"
    l.append( x )

    model = OffenePostenTableModel( l )

    dlg = OffenePostenDialog( model )
    dlg.exec_()

if __name__ == "__main__":
    test()