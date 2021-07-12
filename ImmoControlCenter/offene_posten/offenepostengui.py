import copy

from PySide2 import QtWidgets
from PySide2.QtCore import QModelIndex, QSize, Signal, QAbstractTableModel
from PySide2.QtGui import QFont, Qt
from PySide2.QtWidgets import QWidget, QComboBox, QApplication, QGridLayout, QLabel, QLineEdit, QPushButton, \
    QPlainTextEdit, QListView, QDialog, QVBoxLayout, QMessageBox

from icctablemodel import IccTableModel
from imagefactory import ImageFactory
from qtderivates import IntDisplay, SmartDateEdit, FloatEdit, AuswahlDialog
from generictable_stuff.generictableviewdialog import GenericTableViewDialog, EditableTableViewWidget
from generictable_stuff.okcanceldialog import OkCancelDialog
from interfaces import XOffenerPosten
from offene_posten.offenepostentablemodel import OffenePostenTableModel

########################################################

class OffenerPostenEditor( QWidget ):
    """
    Zum Editieren eines einzelnen Offenen Postens.
    """
    debiKrediAuswahlFirmaPressed = Signal()
    debiKrediAuswahlVwPressed = Signal()

    def __init__( self, x:XOffenerPosten, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._erfasstAm = SmartDateEdit()
        self._debiKredi = QLineEdit()
        self._btnAuswahlDebiKredi_Firma = QPushButton( text="..." )
        self._btnAuswahlDebiKredi_Firma.clicked.connect( self._onDebiKrediAuswahl_Firma )
        self._btnAuswahlDebiKredi_Vw = QPushButton( text="..." )
        self._btnAuswahlDebiKredi_Vw.clicked.connect( self._onDebiKrediAuswahl_Vw )
        self._betrag = FloatEdit()
        self._betragBeglichen = FloatEdit()
        self._letzteBuchungAm = SmartDateEdit()
        self._bemerkung = QPlainTextEdit()
        self._offenerPosten:XOffenerPosten = x
        self._createGui()
        self._dataToGui()

    def _createGui( self ):
        r = c = 0
        l = self._layout
        self._erfasstAm.setPlaceholderText( "erfasst am" )
        self._erfasstAm.setToolTip( "Erfassungsdatum des Offenen Postens" )
        self._erfasstAm.setMaximumWidth( 90 )
        l.addWidget( self._erfasstAm, r, c )
        c += 1
        self._debiKredi.setMinimumWidth( 250 )
        self._debiKredi.setPlaceholderText( "Debitor oder Kreditor" )
        self._debiKredi.setToolTip( "Debitor oder Kreditor eintragen" )
        l.addWidget( self._debiKredi, r, c )

        c += 1
        vbox = QVBoxLayout()
        vbox.addWidget( self._btnAuswahlDebiKredi_Firma )
        self._btnAuswahlDebiKredi_Firma.setFixedSize( QSize( 30, 30 ) )
        self._btnAuswahlDebiKredi_Firma.setToolTip( "Öffnet einen Dialog zur Auswahl einer Firma "
                                              "als Debitor oder Kreditor" )
        vbox.addWidget( self._btnAuswahlDebiKredi_Vw )
        self._btnAuswahlDebiKredi_Vw.setFixedSize( QSize( 30, 30 ) )
        self._btnAuswahlDebiKredi_Vw.setToolTip( "Öffnet einen Dialog zur Auswahl eines Verwalters "
                                                 "als Debitor oder Kreditor" )
        l.addLayout( vbox, r, c )
        #l.addWidget( self._btnAuswahlDebiKredi, r, c )

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
        self._letzteBuchungAm.setPlaceholderText( "letzte Buchg" )
        self._letzteBuchungAm.setToolTip( "Datum der letzten (Teil-)Buchung" )
        self._letzteBuchungAm.setMaximumWidth( 90 )
        l.addWidget( self._letzteBuchungAm, r, c )
        c += 1
        self._bemerkung.setToolTip( "Bemerkung - z.B. Dokumentation von Teilzahlungen" )
        self._bemerkung.setPlaceholderText( "Bemerkung" )
        self._bemerkung.setMaximumHeight( 60 )
        l.addWidget( self._bemerkung, r, c )

    def _dataToGui( self ) -> None:
        x = self._offenerPosten
        self._erfasstAm.setDateFromIsoString( x.erfasst_am )
        self._debiKredi.setText( x.debi_kredi )
        self._betrag.setFloatValue( x.betrag )
        self._betragBeglichen.setFloatValue( x.betrag_beglichen )
        if x.letzte_buchung_am:
            self._letzteBuchungAm.setDateFromIsoString( x.letzte_buchung_am )
        self._bemerkung.setPlainText( x.bemerkung )

    def guiToData( self ) -> None:
        x = self._offenerPosten
        x.erfasst_am = self._erfasstAm.getDate()
        x.debi_kredi = self._debiKredi.text()
        x.betrag = self._betrag.getFloatValue()
        x.betrag_beglichen = self._betragBeglichen.getFloatValue()
        x.letzte_buchung_am = self._letzteBuchungAm.getDate()
        x.bemerkung = self._bemerkung.toPlainText()

    def getOposCopyWithChanges( self ) -> XOffenerPosten:
        """
        liefert eine Kopie des in ARbeit befindlichen XOffenerPosten-Objekts.
        Die in der GUI vorgenommenen Änderungen sind darin enthalten.
        Die Änderungen sind NICHT im Original-OPOS enthalten!
        Das Einfügen der Änderungen in das Original-OPOS passiert durch Aufruf von guiToData().
        :return: eine Kopie des Original-OPOS mit Änderungen
        """
        xcopy = copy.copy( self._offenerPosten )
        xcopy.erfasst_am = self._erfasstAm.getDate()
        xcopy.debi_kredi = self._debiKredi.text()
        xcopy.betrag = self._betrag.getFloatValue()
        xcopy.betrag_beglichen = self._betragBeglichen.getFloatValue()
        xcopy.letzte_buchung_am = self._letzteBuchungAm.getDate()
        xcopy.bemerkung = self._bemerkung.toPlainText()
        return xcopy

    def _onDebiKrediAuswahl_Firma( self ):
        self.debiKrediAuswahlFirmaPressed.emit()

    def _onDebiKrediAuswahl_Vw( self ):
        self.debiKrediAuswahlVwPressed.emit()

    def setOffenerPosten( self, x:XOffenerPosten ):
        self._offenerPosten = x
        if x.erfasst_am > "":
            self._erfasstAm.setDateFromIsoString( x.erfasst_am )
        self._debiKredi.setText( x.debi_kredi )
        self._betrag.setFloatValue( x.betrag )
        self._betragBeglichen.setFloatValue( x.betrag_beglichen )
        if x.letzte_buchung_am > "":
            self._letzteBuchungAm.setDateFromIsoString( x.letzte_buchung_am )
        self._bemerkung.setPlainText( x.bemerkung )

    def getOffenerPosten( self ) -> XOffenerPosten:
        x = self._offenerPosten
        if x is None: return XOffenerPosten()
        x.erfasst_am = self._erfasstAm.getDate()
        x.debi_kredi = self._debiKredi.text()
        x.betrag = self._betrag.getFloatValue()
        x.betrag_beglichen = self._betragBeglichen.getFloatValue()
        x.letzte_buchung_am = self._letzteBuchungAm.getDate()
        x.bemerkung = self._bemerkung.toPlainText()
        return x

    def setDebiKredi( self, debikredi:str ):
        self._debiKredi.setText( debikredi )

########################################################

class OffenerPostenEditDialog( OkCancelDialog ):
    """
    Dialog, der den OffenerPostenEditor beinhaltet.
    Zum Editieren eines einzelnen Offenen Postens.
    """
    chooseVerwalterSignal = Signal()
    chooseFirmaSignal = Signal()

    def __init__( self, x:XOffenerPosten, parent=None ):
        OkCancelDialog.__init__( self, parent )
        self._edi = OffenerPostenEditor( x )
        self._edi.debiKrediAuswahlFirmaPressed.connect( self.chooseFirmaSignal.emit )
        self._edi.debiKrediAuswahlVwPressed.connect( self.chooseVerwalterSignal.emit )
        self.addWidget( self._edi, 0 )

    def onRejected( self ):
        self.reject()

    def getEditor( self ) -> OffenerPostenEditor:
        return self._edi


########################################################

class OffenePostenView( QWidget ):
    createOposSignal = Signal()
    editOposSignal = Signal( QModelIndex )
    deleteOposSignal = Signal( QModelIndex )
    saveChangesSignal = Signal()

    def __init__(self, oposmodel:IccTableModel, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self._btnSave = QPushButton( self )
        self._etv = EditableTableViewWidget( model=oposmodel, isEditable=True, parent=parent )
        self._etv.createItem.connect( self._onCreateItem )
        self._etv.editItem.connect( self._onEditItem )
        self._etv.deleteItem.connect( self._onDeleteItem )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        btn = self._btnSave
        btn.clicked.connect( self.saveChangesSignal.emit )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen an den Offenen Posten speichern" )
        icon = ImageFactory.inst().getSaveIcon()
        btn.setIcon( icon )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        btn.setIconSize( QSize( 30, 30 ) )
        l.addWidget( btn, 0, 0, alignment=Qt.AlignLeft )
        l.addWidget( self._etv, 1, 0 )
        self.setLayout( self._layout )

    def _onCreateItem( self ):
        self.createOposSignal.emit()

    def _onEditItem( self, item ):
        self.editOposSignal.emit( item )

    def _onDeleteItem( self, item ):
        self.deleteOposSignal.emit( item )

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

    def getModel( self ):
        #return self._etv.getModel()
        return self._etv.getTableView().model()

    def showException( self, title: str, exception: str, moretext: str = None ):
        # todo: show Qt-Errordialog
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle( title )
        msgbox.setIcon( QMessageBox.Critical )
        msgbox.setText( exception )
        if moretext:
            msgbox.setInformativeText( moretext )
        msgbox.exec_()

########################################################

# class OffenePostenDialog( GenericTableViewDialog ):
#     """
#     Dialog, der offene Posten in einer Liste enthält.
#     Jeder Posten kann editiert oder gelöscht werden.
#     Neue Posten können angelegt werden.
#     """
#     def __init__(self, model:OffenePostenTableModel, parent=None ):
#         GenericTableViewDialog.__init__( self, model=model, isEditable=True, parent=parent )
#         self.setWindowTitle( "Offene Posten" )
#         self.setOkButtonText( "Speichern" )

########################################################

def onEdit( index:QModelIndex ):
    print( "onEdit, %d/%d" % (index.row(), index.column() ) )

def onDebiKrediAuswahlFirma():
    print( "debiKrediAuswahlFirma" )
    dlg = AuswahlDialog()
    dlg.appendItem( "AFDSLKJF" )
    dlg.appendItem( "BVBVBVBVB" )
    if dlg.exec_() == QDialog.Accepted:
        l = dlg.getSelection()
        t = l[0]
        print( "Auswahl Firma: ", t[0], "/", t[1] )

def onDebiKrediAuswahlVw():
    print( "debiKrediAuswahlVw" )
    dlg = AuswahlDialog()
    dlg.appendItem( "Verwalter Sepp" )
    dlg.appendItem( "Verwalter Depp" )
    if dlg.exec_() == QDialog.Accepted:
        l = dlg.getSelection()
        t = l[0]
        print( "Auswahl Verwalter: ", t[0], "/", t[1] )

def testOffenerPostenEditor():
    app = QApplication()
    v = OffenerPostenEditor()
    v.show()

    x = XOffenerPosten()
    x.opos_id = 1
    x.mv_id = "mueller_hajo"
    x.debi_kredi = "Müller, Hajo"
    x.erfasst_am = "2021-06-03"
    x.betrag = 123.45
    x.betrag_beglichen = 33.44
    x.letzte_buchung_am = "2021-07-01"
    x.bemerkung = "steht aus"

    v.setOffenerPosten( x )
    v.debiKrediAuswahlFirmaPressed.connect( onDebiKrediAuswahlFirma )
    v.debiKrediAuswahlVwPressed.connect( onDebiKrediAuswahlVw )
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

    v = OffenePostenView( model )
    v.show()
    # dlg = OffenePostenDialog( model )
    # dlg.editItem.connect( onEdit )
    # dlg.exec_()

    app.exec_()

if __name__ == "__main__":
    test()
    #testOffenerPostenEditor()