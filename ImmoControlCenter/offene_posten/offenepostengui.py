from PySide2 import QtWidgets
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QComboBox, QApplication

from generictable_stuff.generictableviewdialog import GenericTableViewDialog
from interfaces import XOffenerPosten
from offene_posten.offenepostentablemodel import OffenePostenTableModel


class OffenerPostenEditor( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )

class OffenePostenDialog( GenericTableViewDialog ):
    def __init__(self, model:OffenePostenTableModel ):
        GenericTableViewDialog.__init__( self, model=model, isEditable=True )
        self.setWindowTitle( "Offene Posten" )


def test():
    app = QApplication()

    l = list()
    x = XOffenerPosten()
    x.opos_id = 1
    x.mv_id = "mueller_hajo"
    x.debi_kredi = "Müller, Hajo"
    x.erfasst_am = "2021-06-03"
    x.betrag = 123.45
    x.betrag_beglichen = 33.44
    x.letzte_buchung_am = "2021-07-01"
    x.bemerkung = "steht aus"
    l.append( x )

    x = XOffenerPosten()
    x.opos_id = 2
    x.mv_id = "himpfelhuberfoerrenschmidt_pauljohann"
    x.debi_kredi = "Himpfelhober-Förrenschmidt, Pauljohann"
    x.erfasst_am = "2021-06-03"
    x.betrag = 876.90
    x.bemerkung = "steht aus trotz sechzehnmaliger Mahnung und Drohung"
    l.append( x )

    model = OffenePostenTableModel( l )

    dlg = OffenePostenDialog( model )
    dlg.exec_()

if __name__ == "__main__":
    test()