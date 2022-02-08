import copy

from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QFont, Qt, QIcon
from PySide2.QtWidgets import QGridLayout, QLabel, QHBoxLayout, QPushButton, QApplication
from icc.iccview import IccView
from interfaces import XMietverhaeltnis, XMieterwechsel
from mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisView
from qtderivates import BaseEdit, SmartDateEdit, BaseLabel, FloatEdit, IntEdit


############### MieterwechselView ########################
class MieterwechselView( IccView ):
    """
    Enthält ein paar Felder für das aktive ("alte") Mietverhältnis,
    sowie eine MietverhaeltnisView für das Folge-MV.
    Die Methode onChange() der MietverhaeltnisView wird umgebogen auf die onChange()-Methode dieser View.
    """
    mieterwechsel_save = Signal()
    def __init__( self ):
        IccView.__init__( self )
        self._layout = QGridLayout()
        self._btnSave = QPushButton()
        # altes Mietverhältnis
        self._edAlterMieter = BaseEdit()
        self._edAlteNettomiete = FloatEdit()
        self._edAlteNKV = FloatEdit()
        self._edAlteKaution = IntEdit()
        self._sdEndeMietverh = SmartDateEdit()
        self._sdEndeMietverh.textChanged.connect( self.onChang )
        # neues Mietverhältnis
        self._neuesMietvhView = MietverhaeltnisView( enableBrowsing=False )
        self._neuesMietvhView.dataChanged.connect( self.onChang )
        self._mieterwechsel:XMieterwechsel = None

        self._createGui()

    def onChang( self ):
        if not self._btnSave.isEnabled():
            self.setSaveButtonEnabled()

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

    def _createGui( self ):
        self._createSaveButton()
        r = self._createGuiAlterMieter()
        r+=1
        self._layout.addWidget( QLabel( "" ), r, 0 )
        r+=1
        self._createGuiNeuerMieter( r )
        self.setLayout( self._layout )

    def _createSaveButton( self ):
        btn = self._btnSave
        btn.clicked.connect( self.mieterwechsel_save.emit )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen dieser View speichern" )
        icon = QIcon( "./images/save_30.png" )
        btn.setIcon( icon )
        size = QSize( 32, 32 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        hbox = QHBoxLayout()
        hbox.addWidget( btn )
        self._layout.addLayout( hbox, 0, 0, alignment=Qt.AlignLeft )

    def _createGuiAlterMieter( self ) -> int:
        l = self._layout
        r = 1
        c = 0
        lbl = BaseLabel( "Aktuelles / letztes Mietverhältnis " )
        lbl.setFont( QFont( "Arial", 12, QFont.Bold ) )
        l.addWidget( lbl, r, c, 1, 2 )

        r+=1
        lbl = QLabel( "Mieter: " )
        l.addWidget( lbl, r, c )
        self._edAlterMieter.setReadOnly( True )
        l.addWidget( self._edAlterMieter, r, c + 1 )

        r+=1
        lbl = BaseLabel( "Nettomiete / NKV : " )
        l.addWidget( lbl, r, c )

        c+=1
        hbox = QHBoxLayout()
        self._edAlteNettomiete.setReadOnly( True )
        self._edAlteNettomiete.setMaximumWidth( 100 )
        hbox.addWidget( self._edAlteNettomiete )

        self._edAlteNKV.setReadOnly( True )
        self._edAlteNKV.setMaximumWidth( 100 )
        hbox.addWidget( self._edAlteNKV )
        l.addLayout( hbox, r, c, Qt.AlignLeft )

        c = 0
        r += 1
        lbl = BaseLabel( "Kaution: " )
        l.addWidget( lbl, r, c )

        c+=1
        self._edAlteKaution.setReadOnly( True )
        self._edAlteKaution.setMaximumWidth( 100 )
        l.addWidget( self._edAlteKaution, r, c )

        c = 0
        r += 1
        lbl = QLabel( "Ende des Mietverhältnisses: " )
        l.addWidget( lbl, r, c )

        self._sdEndeMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdEndeMietverh, r, c + 1 )
        return r

    def _createGuiNeuerMieter( self, r: int ):
        c = 0
        l = self._layout
        lbl = BaseLabel( "Neues Mietverhältnis" )
        lbl.setFont( QFont( "Arial", 12, QFont.Bold ) )
        l.addWidget( lbl, r, c )

        r += 1
        l.addWidget( self._neuesMietvhView, r, c, 1, 2 )

    def setMieterwechselData( self, xmieterwechsel:XMieterwechsel ):
        self._mieterwechsel = xmieterwechsel
        self._setAltesMietverhaeltnisFields( xmieterwechsel.mietverhaeltnis_alt )
        self._setNeuesMietverhaeltnisFields( xmieterwechsel.mietverhaeltnis_next )
        self.setSaveButtonEnabled( False )

    def getMieterwechselData( self ) -> XMieterwechsel:
        return self._mieterwechsel

    def _setAltesMietverhaeltnisFields( self, xmv:XMietverhaeltnis ):
        self._edAlterMieter.setText( xmv.name + ", " + xmv.vorname )
        self._edAlteNettomiete.setFloatValue( xmv.nettomiete )
        self._edAlteNKV.setFloatValue( xmv.nkv )
        if xmv.kaution:
            self._edAlteKaution.setIntValue( xmv.kaution )
        self._sdEndeMietverh.setDateFromIsoString( xmv.bis )

    def _setNeuesMietverhaeltnisFields( self, xmv:XMietverhaeltnis ):
        self._neuesMietvhView.setMietverhaeltnisData( xmv )

    def getMieterwechselDataCopyWithChanges( self ) -> XMieterwechsel:
        xmwcopy = copy.copy( self._mieterwechsel )
        mvneu:XMietverhaeltnis = self._neuesMietvhView.getMietverhaeltnisCopyWithChanges()
        xmwcopy.mietverhaeltnis_next = mvneu
        xmwcopy.mietverhaeltnis_alt.bis = self._sdEndeMietverh.getDate()
        return xmwcopy

    def applyChanges( self ):
        self._neuesMietvhView.applyChanges()
        # nur das Ende-Datum ist bei den Daten des alten MV änderbar
        self._mieterwechsel.mietverhaeltnis_alt.bis = self._sdEndeMietverh.getDate()

    def getModel( self ):
        return None



def test():
    app = QApplication()
    v = MieterwechselView()
    v.show()
    app.exec_()