import copy

from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout
from generictable_stuff.okcanceldialog import OkCancelDialog
from interfaces import XMietverhaeltnis
from qtderivates import BaseEdit, SmartDateEdit, BaseLabel, IntEdit, MultiLineEdit, FloatEdit


##################  MietverhaeltnisView  ################
class MietverhaeltnisView( QWidget ):
    def __init__( self, mietverhaeltnis:XMietverhaeltnis=None, parent=None ):
        QWidget.__init__( self, parent )
        self._mietverhaeltnis:XMietverhaeltnis = None
        self._layout = QGridLayout()
        self._sdBeginnMietverh = SmartDateEdit()
        self._sdEndeMietverh = SmartDateEdit()
        self._edMieterName_1 = BaseEdit()
        self._edMieterVorname_1 = BaseEdit()
        self._edMieterName_2 = BaseEdit()
        self._edMieterVorname_2 = BaseEdit()
        self._edMieterTelefon = BaseEdit()
        self._edMieterMobil = BaseEdit()
        self._edMieterMailto = BaseEdit()
        self._edAnzPers = IntEdit()
        self._edNettomiete = FloatEdit()
        self._edNkv = FloatEdit()
        self._edKaution = IntEdit()
        self._sdKautionBezahltAm = SmartDateEdit()
        self._txtBemerkung1 = MultiLineEdit()
        self._txtBemerkung2 = MultiLineEdit()
        self._createGui()
        if mietverhaeltnis:
            self.setMietverhaeltnisData( mietverhaeltnis )

    def _createGui( self ):
        self._createFelder( )
        self.setLayout( self._layout )

    def _createFelder( self ):
        r = 0
        c = 0
        l = self._layout

        lbl = QLabel( "Beginn: " )
        l.addWidget( lbl, r, c )
        c+=1
        self._sdBeginnMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdBeginnMietverh, r, c )

        c=0
        r += 1
        l.addWidget( BaseLabel( "Ende: " ), r, c )
        c+=1
        self._sdEndeMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdEndeMietverh, r, c )

        c = 0
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

        c = 0
        r += 1
        l.addWidget( BaseLabel( "Mobil: " ), r, c )
        c += 1
        l.addWidget( self._edMieterMobil, r, c )

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

    def _guiToData( self, x:XMietverhaeltnis ):
        """
        Überträgt die Änderungen, die der User im GUI gemacht hat, in das
        übergebene XMietverhaeltnis-Objekt
        :param x: XMietverhaeltnis-Objekt, in das die geänderten Daten übertragen werden
        :return:
        """
        x.von = self._sdBeginnMietverh.getDate()
        x.bis = self._sdEndeMietverh.getDate()
        x.name = self._edMieterName_1.text()
        x.vorname = self._edMieterVorname_1.text()
        x.name2 = self._edMieterName_2.text()
        x.vorname2 = self._edMieterVorname_2.text()
        x.telefon = self._edMieterTelefon.text()
        x.mobil = self._edMieterMobil.text()
        x.mailto = self._edMieterMailto.text()
        x.anzahl_pers = self._edAnzPers.getIntValue()
        x.nettomiete = self._edNettomiete.getFloatValue()
        x.nkv = self._edNkv.getFloatValue()
        x.kaution = self._edKaution.getIntValue()
        x.kaution_bezahlt_am = self._sdKautionBezahltAm.getDate()
        x.bemerkung1 = self._txtBemerkung1.toPlainText()
        x.bemerkung2 = self._txtBemerkung2.toPlainText()

    def getMietverhaeltnisCopyWithChanges( self ) -> XMietverhaeltnis:
        """
        gibt eine Kopie der Mietverhaeltnis-Schnittstellendaten mit Änderungen zurück.
        Diese Kopie kann für Validierungszwecke verwendet werden.
        :return: Kopie von XMietverhaeltnis
        """
        mvcopy = copy.copy( self._mietverhaeltnis )
        self._guiToData( mvcopy )
        return mvcopy

    def applyChanges( self ):
        """
        überträgt die Änderungen, die der User im GUI gemacht hat, in das
        originale XMietverhaeltnis-Objekt.
        """
        self._guiToData( self._mietverhaeltnis )

    def setMietverhaeltnisData( self, mv:XMietverhaeltnis ):
        """
        Daten, die im GUI angezeigt und geändert werden können.
        :param mv:
        :return:
        """
        self._mietverhaeltnis = mv
        if mv.von:
            self._sdBeginnMietverh.setDateFromIsoString( mv.von )
        if mv.bis:
            self._sdEndeMietverh.setDateFromIsoString( mv.bis )
        self._edMieterName_1.setText( mv.name )
        self._edMieterVorname_1.setText( mv.vorname )
        self._edMieterName_2.setText( mv.name2 )
        self._edMieterVorname_2.setText( mv.vorname2 )
        self._edMieterTelefon.setText( mv.telefon )
        self._edMieterMobil.setText( mv.mobil )
        self._edMieterMailto.setText( mv.mailto )
        self._edAnzPers.setIntValue( mv.anzahl_pers )
        self._edNettomiete.setFloatValue( mv.nettomiete )
        self._edNkv.setFloatValue( mv.nkv )
        self._edKaution.setIntValue( mv.kaution )
        if mv.kaution_bezahlt_am:
            self._sdKautionBezahltAm.setDateFromIsoString( mv.kaution_bezahlt_am )
        self._txtBemerkung1.setText( mv.bemerkung1 )
        self._txtBemerkung2.setText( mv.bemerkung2 )

    ###############  MietverhaeltnisDialog  ##########################
class MieterwechselDialog( OkCancelDialog ):
    def __init__(self, miet_obj:str, parent=None):
        OkCancelDialog.__init__( self, parent )
        self.setWindowTitle( miet_obj )
        self._view = MietverhaeltnisView()
        self.addWidget( self._view, 0 )
