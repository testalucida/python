from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QFont, Qt, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QHBoxLayout, QPushButton
from generictable_stuff.okcanceldialog import OkCancelDialog
from iccdialog import IccDialog
from iccview import IccView
from interfaces import XMietverhaeltnis
from mietverhaeltnis.mietverhaeltnisgui import MietverhaeltnisView
from qtderivates import AuswahlDialog, BaseEdit, SmartDateEdit, BaseLabel, FloatEdit, IntEdit


############### MieterwechselView ########################
class MieterwechselView( IccView ):
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
        # neues Mietverhältnis
        self._neuesMietvh = MietverhaeltnisView()

        self._createGui()

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
        btn.setEnabled( True )
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
        l.addWidget( self._neuesMietvh, r, c, 1, 2 )

    def setAltesMietverhaeltnis( self, xmv:XMietverhaeltnis ):
        self._edAlterMieter.setText( xmv.name + ", " + xmv.vorname )
        self._edAlteNettomiete.setFloatValue( xmv.nettomiete )
        self._edAlteNKV.setFloatValue( xmv.nkv )
        if xmv.kaution:
            self._edAlteKaution.setIntValue( xmv.kaution )
        self._sdEndeMietverh.setDateFromIsoString( xmv.bis )

    def setNeuesMietverhaeltnis( self, xmv:XMietverhaeltnis ):
        self._neuesMietvh.setMietverhaeltnisData( xmv )

    def getNeuesMietverhaeltnisCopyWithChanges( self ) -> XMietverhaeltnis:
        return self._neuesMietvh.getMietverhaeltnisCopyWithChanges()

    def getAltesMietverhaeltnisMietEnde( self ) -> str:
        return self._sdEndeMietverh.getDate()

    def applyChanges( self ):
        self._neuesMietvh.applyChanges()

    def getModel( self ):
        return self._neuesMietvh.getMietverhaeltnisCopyWithChanges()


# def test():
#     dlg = MieterwechselDialog( "NK_Volkerstal" )
#     dlg.exec_()
#
# if __name__ == "__main__":
#     app = QApplication()
#     test()