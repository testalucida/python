import copy

from PySide2.QtCore import Signal, QModelIndex
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QScrollArea, QVBoxLayout, QHBoxLayout

from generictable_stuff.generictableviewdialog import EditableTableViewWidget
from generictable_stuff.okcanceldialog import OkCancelDialog
from icctablemodel import IccTableModel
from imagefactory import ImageFactory
from interfaces import XNotiz
from notizen.notizentablemodel import NotizenTableModel
from qtderivates import BaseEdit, BaseLabel, MultiLineEdit, CheckBox


#######################  NotizEditor  ##########################
class NotizEditor( QWidget ):
    bezugAuswahlFirmaPressed = Signal()
    bezugAuswahlVwPressed = Signal()
    bezugAuswahlMieterPressed = Signal()

    def __init__( self, notiz:XNotiz=None, parent=None ):
        QWidget.__init__( self, parent )
        self.setWindowTitle( "Bearbeiten einer Notiz" )
        self._layout = QGridLayout( self )
        self._bezug = BaseEdit()
        self._btnAuswahlBezug_Firma = QPushButton( text="F" )
        self._btnAuswahlBezug_Firma.clicked.connect( self.bezugAuswahlFirmaPressed.emit )
        self._btnAuswahlBezug_Vw = QPushButton( text="V" )
        self._btnAuswahlBezug_Vw.clicked.connect( self.bezugAuswahlVwPressed.emit )
        self._btnAuswahlBezug_Mieter = QPushButton( text="M" )
        self._btnAuswahlBezug_Mieter.clicked.connect( self.bezugAuswahlMieterPressed.emit )
        self._caption = BaseEdit()
        self._edi = MultiLineEdit()
        self._erledigt = CheckBox( "erledigt" )
        self._notiz:XNotiz = None
        self._createGui()
        if notiz:
            self.setNotiz( notiz )

    def _createGui( self ):
        l = self._layout
        r = c = 0
        self._bezug.setPlaceholderText( "Bezug der Notiz" )
        l.addWidget( self._bezug )

        self._btnAuswahlBezug_Firma.setFixedWidth( 30 )
        self._btnAuswahlBezug_Firma.setToolTip( "Auswahldialog Firma öffnen" )
        self._btnAuswahlBezug_Vw.setFixedWidth( 30 )
        self._btnAuswahlBezug_Vw.setToolTip( "Auswahldialog Verwalter öffnen" )
        self._btnAuswahlBezug_Mieter.setFixedWidth( 30 )
        self._btnAuswahlBezug_Mieter.setToolTip( "Auswahldialog Mieter öffnen" )
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget( self._btnAuswahlBezug_Firma )
        buttonsLayout.addWidget( self._btnAuswahlBezug_Vw )
        buttonsLayout.addWidget( self._btnAuswahlBezug_Mieter )
        c += 1
        l.addLayout( buttonsLayout, r, c )

        r += 1
        c = 0
        self._caption.setPlaceholderText( "Überschrift der Notiz" )
        l.addWidget( self._caption, r, c, 1, 2 )
        r += 1
        l.addWidget( self._edi, r, c, 1, 2 )

        r += 1
        l.addWidget( self._erledigt, r, c )

        self.setLayout( l )

    def _dataToGui( self ) -> None:
        x = self._notiz
        self._bezug.setText( x.bezug )
        self._caption.setText( x.ueberschrift )
        self._edi.setText( x.text )
        self._erledigt.setChecked( (x.erledigt == 1) )

    def guiToData( self ) -> None:
        x = self._notiz
        x.bezug = self._bezug.text()
        x.ueberschrift = self._caption.text()
        x.text = self._edi.toPlainText()
        x.erledigt = 1 if self._erledigt.isChecked() else 0

    def setNotiz( self, notiz:XNotiz ):
        self._notiz = notiz
        self._bezug.setText( notiz.bezug )
        self._caption.setText( notiz.ueberschrift )
        self._edi.setText( notiz.text )
        self._erledigt.setChecked( True if notiz.erledigt == 1 else 0 )

    def setBezug( self, bezug:str ):
        self._bezug.setText( bezug )

    def getNotizCopyWithChanges( self ) -> XNotiz:
        """
        liefert eine Kopie des in ARbeit befindlichen XNotiz-Objekts.
        Die in der GUI vorgenommenen Änderungen sind darin enthalten.
        Die Änderungen sind NICHT in der Original-Notiz enthalten!
        Das Einfügen der Änderungen in die Original-Notiz passiert durch Aufruf von guiToData().
        :return: eine Kopie der Original-Notiz mit Änderungen
        """
        xcopy = copy.copy( self._notiz )
        xcopy.bezug = self._bezug.text()
        xcopy.ueberschrift = self._caption.text()
        xcopy.text = self._edi.toPlainText()
        xcopy.erledigt = 1 if self._erledigt.isChecked() else 0
        return xcopy

#######################  NotizEditDialog  ######################
class NotizEditDialog( OkCancelDialog ):
    """
    Dialog, der den OffenerPostenEditor beinhaltet.
    Zum Editieren eines einzelnen Offenen Postens.
    """
    def __init__(self, notiz:XNotiz=None, parent=None ):
        OkCancelDialog.__init__( self, parent )
        self._edi = NotizEditor( notiz )
        self.addWidget( self._edi, 0 )

    def getEditor( self ) -> NotizEditor:
        return self._edi

#######################  NotizenTableView  #####################
class NotizenTableViewWidget( EditableTableViewWidget ):
    """
    Tabelle mit Notizen (jede Row enstpricht einem XNotiz-Objekt)
    und 3 Buttons zur Neuanlage, zum Editieren und Löschen einer Notiz
    """
    def __init__(self, model:NotizenTableModel=None, parent=None):
        EditableTableViewWidget.__init__( self, model, True, parent )
        self.getTableView().setSortingEnabled( True )

########################  NotizenView  ###########################
class NotizenView( QWidget ):
    """
   Widget, das ein NotizenTableViewWidget enthält und zusätzlich einen Save-Button,
   um die Änderungen zu speichern
   """
    saveNotiz = Signal()

    def __init__(self, model:NotizenTableModel=None, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self._btnSave = QPushButton( self )
        self._btnSave.clicked.connect( self.saveNotiz.emit )
        self._ntv = NotizenTableViewWidget( model=model, parent=parent )
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

    def getModel( self ) -> NotizenTableModel:
        return self._ntv.getModel()

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

    def getNotizenTableViewWidget( self ) -> NotizenTableViewWidget:
        return self._ntv


def test():
    app = QApplication()
    n = XNotiz()
    n.bezug = "Ww224"
    n.text = "wichtiger Text zur wichtigen Notiz"
    n.ueberschrift = "wichtige Notiz"
    #v = NotizEditDialog( n )
    v = NotizenView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()