from PySide2 import QtWidgets
from PySide2.QtCore import QModelIndex, QSize
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QComboBox, QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, \
    QPlainTextEdit
from qtderivates import IntDisplay, SmartDateEdit, FloatEdit
from generictable_stuff.generictableviewdialog import GenericTableViewDialog
from generictable_stuff.okcanceldialog import OkCancelDialog
from interfaces import XOffenerPosten
from offene_posten.offenepostentablemodel import OffenePostenTableModel

########################################################

class OffenerPostenEditor( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._erfasstAm = SmartDateEdit()
        self._debiKredi = QLineEdit()
        self._btnAuswahlDebiKredi = QPushButton( text="..." )
        self._betrag = FloatEdit()
        self._betragBeglichen = FloatEdit()
        self._letzteBuchungAm = SmartDateEdit()
        self._bemerkung = QPlainTextEdit()
        self._createGui()

    def _createGui( self ):
        r = c = 0
        l = self._layout
        self._erfasstAm.setPlaceholderText( "erfasst am" )
        self._erfasstAm.setToolTip( "Erfassungsdatum des Offenen Postens" )
        self._erfasstAm.setMaximumWidth( 90 )
        l.addWidget( self._erfasstAm, r, c )
        c += 1
        self._debiKredi.setPlaceholderText( "Debitor oder Kreditor" )
        self._debiKredi.setToolTip( "Debitor oder Kreditor eintragen" )
        l.addWidget( self._debiKredi, r, c )
        c += 1
        self._btnAuswahlDebiKredi.setFixedSize( QSize(30,30) )
        self._btnAuswahlDebiKredi.setToolTip( "Öffnet einen Dialog zur Auswahl des Debitors/Kreditors" )
        l.addWidget( self._btnAuswahlDebiKredi, r, c )
        c += 1
        self._betrag.setPlaceholderText( "Betrag" )
        self._betrag.setToolTip( "Ursprünglicher offener Betrag. '-' = Debit, '+' = Kredit" )
        self._betrag.setFixedWidth( 80 )
        l.addWidget( self._betrag, r, c )
        c += 1
        self._betragBeglichen.setPlaceholderText( "bezahlt" )
        self._betragBeglichen.setToolTip( "Bereits bezahlter Betrag" )
        self._betragBeglichen.setFixedWidth( 80 )
        l.addWidget( self._betragBeglichen, r, c )
        c += 1
        self._letzteBuchungAm.setPlaceholderText( "erfasst am" )
        self._letzteBuchungAm.setToolTip( "Wann der letzte Teilbetrag gebucht wurde" )
        self._letzteBuchungAm.setMaximumWidth( 90 )
        l.addWidget( self._letzteBuchungAm, r, c )
        c += 1
        self._bemerkung.setToolTip( "Bemerkung - z.B. Dokumentation von Teilzahlungen" )
        self._bemerkung.setPlaceholderText( "Bemerkung" )
        self._bemerkung.setMaximumHeight( 60 )
        l.addWidget( self._bemerkung, r, c )


########################################################

class OffenerPostenEditDialog( OkCancelDialog ):
    def __init__( self, parent=None ):
        OkCancelDialog.__init__( self, parent )
        self._edi = OffenerPostenEditor()
        self.addWidget( self._edi, 0 )

########################################################

class OffenePostenDialog( GenericTableViewDialog ):
    """
    Dialog, der offene Posten in einer Liste enthält.
    Jeder Posten kann editiert oder gelöscht werden.
    Neue Posten können angelegt werden.
    """
    def __init__(self, model:OffenePostenTableModel ):
        GenericTableViewDialog.__init__( self, model=model, isEditable=True )
        self.setWindowTitle( "Offene Posten" )
        self.setOkButtonText( "Speichern" )
        self.createItem.connect( self._onCreateItem )
        self.okPressed.connect( self._onSave )

    def _onCreateItem( self ):
        print( "onCreateItem" )
        dlg = OffenerPostenEditDialog()
        dlg.setModal( True )
        dlg.exec_()

    def _onSave( self ):
        print( "OffenePostenDialog.onSave" )

########################################################

def onEdit( index:QModelIndex ):
    print( "onEdit, %d/%d" % (index.row(), index.column() ) )

def testOffenerPostenEditor():
    app = QApplication()
    v = OffenerPostenEditor()
    v.show()
    app.exec_()

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
    dlg.editItem.connect( onEdit )
    dlg.exec_()

    #app.exec_()

if __name__ == "__main__":
    #test()
    testOffenerPostenEditor()