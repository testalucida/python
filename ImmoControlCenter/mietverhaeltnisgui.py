from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout
from generictable_stuff.okcanceldialog import OkCancelDialog
from qtderivates import BaseEdit, SmartDateEdit, BaseLabel, IntEdit, MultiLineEdit

##################  MietverhaeltnisView  ################
class MietverhaeltnisView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self._sdBeginnMietverh = SmartDateEdit()
        self._edMieterName_1 = BaseEdit()
        self._edMieterVorname_1 = BaseEdit()
        self._edMieterName_2 = BaseEdit()
        self._edMieterVorname_2 = BaseEdit()
        self._edMieterTelefon = BaseEdit()
        self._edMieterMailto = BaseEdit()
        self._edAnzPers = IntEdit()
        self._edNettomiete = BaseEdit()
        self._edNkv = BaseEdit()
        self._edKaution = BaseEdit()
        self._sdKautionBezahltAm = SmartDateEdit()
        self._txtBemerkung1 = MultiLineEdit()
        self._txtBemerkung2 = MultiLineEdit()
        self._createGui()

    def _createGui( self ):
        self._createFelder( )
        self.setLayout( self._layout )

    def _createFelder( self ):
        r = 0
        c = 0
        l = self._layout

        lbl = QLabel( "Beginn: " )
        l.addWidget( lbl, r, c )
        self._sdBeginnMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdBeginnMietverh, r, c + 1 )

        r += 1
        lbl = BaseLabel( "Name / Vorname 1. Mieter: " )
        l.addWidget( lbl, r, c )
        c+=1
        hbox = QHBoxLayout()
        hbox.addWidget( self._edMieterName_1 )
        hbox.addWidget( self._edMieterVorname_1 )
        l.addLayout( hbox, r, c )

        c = 0
        r += 1
        lbl = BaseLabel( "Name / Vorname 2. Mieter: " )
        l.addWidget( lbl, r, c )
        c += 1
        hbox = QHBoxLayout()
        hbox.addWidget( self._edMieterName_2 )
        hbox.addWidget( self._edMieterVorname_2 )
        l.addLayout( hbox, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Telefon: " ), r, c )
        c+=1
        l.addWidget( self._edMieterTelefon, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Mailadresse: " ), r, c )
        c+=1
        l.addWidget( self._edMieterMailto, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Anzahl Personen i.d. Whg: " ), r, c )
        c += 1
        self._edAnzPers.setMaximumWidth( 20 )
        l.addWidget( self._edAnzPers, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Nettomiete / NKV: " ), r, c )

        c+=1
        self._edNettomiete.setMaximumWidth( 100 )
        self._edNkv.setMaximumWidth( 100 )
        hbox = QHBoxLayout()
        hbox.addWidget( self._edNettomiete )
        hbox.addWidget( self._edNkv )
        l.addLayout( hbox, r, c, alignment=Qt.AlignLeft )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Kaution: " ), r, c )
        c+=1
        self._edKaution.setMaximumWidth( 100 )
        l.addWidget( self._edKaution, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "Kaution bezahlt am: " ), r, c )
        c+=1
        self._sdKautionBezahltAm.setMaximumWidth( 100 )
        l.addWidget( self._sdKautionBezahltAm, r, c )

        c=0
        r+=1
        l.addWidget( BaseLabel( "" ), r, c )

        r+=1
        l.addWidget( BaseLabel( "Bemerkungen: " ), r, c )
        c+=1
        hbox = QHBoxLayout()
        hbox.addWidget( self._txtBemerkung1 )
        hbox.addWidget( self._txtBemerkung2 )
        l.addLayout( hbox, r, c )

###############  MietverhaeltnisDialog  ##########################
class MieterwechselDialog( OkCancelDialog ):
    def __init__(self, miet_obj:str, parent=None):
        OkCancelDialog.__init__( self, parent )
        self.setWindowTitle( miet_obj )
        self._view = MietverhaeltnisView()
        self.addWidget( self._view, 0 )
