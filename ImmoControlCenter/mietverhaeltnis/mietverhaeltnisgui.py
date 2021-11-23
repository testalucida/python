import copy

from PySide2 import QtCore
from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import Qt, QIcon
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QHBoxLayout, QApplication, QPushButton
from generictable_stuff.okcanceldialog import OkCancelDialog
from imagefactory import ImageFactory
from interfaces import XMietverhaeltnis
from qtderivates import BaseEdit, SmartDateEdit, BaseLabel, IntEdit, MultiLineEdit, FloatEdit, HLine


##################  MietverhaeltnisView  ################
class MietverhaeltnisView( QWidget ):
    save = Signal()
    dataChanged = Signal()
    def __init__( self, mietverhaeltnis:XMietverhaeltnis=None, withSaveButton:bool=False, parent=None ):
        QWidget.__init__( self, parent )
        self._mietverhaeltnis:XMietverhaeltnis = None
        self._withSaveButton = withSaveButton
        self._layout = QGridLayout()
        self._btnSave = QPushButton()
        self._sdBeginnMietverh = SmartDateEdit()
        self._sdBeginnMietverh.textChanged.connect( self.onChange )
        self._sdEndeMietverh = SmartDateEdit()
        self._sdEndeMietverh.textChanged.connect( self.onChange )
        self._edMieterName_1 = BaseEdit()
        self._edMieterName_1.textChanged.connect( self.onChange )
        self._edMieterVorname_1 = BaseEdit()
        self._edMieterVorname_1.textChanged.connect( self.onChange )
        self._edMieterName_2 = BaseEdit()
        self._edMieterName_2.textChanged.connect( self.onChange )
        self._edMieterVorname_2 = BaseEdit()
        self._edMieterVorname_2.textChanged.connect( self.onChange )
        self._edMieterTelefon = BaseEdit()
        self._edMieterTelefon.textChanged.connect( self.onChange )
        self._edMieterMobil = BaseEdit()
        self._edMieterMobil.textChanged.connect( self.onChange )
        self._edMieterMailto = BaseEdit()
        self._edMieterMailto.textChanged.connect( self.onChange )
        self._edAnzPers = IntEdit()
        self._edAnzPers.textChanged.connect( self.onChange )
        self._edNettomiete = FloatEdit()
        self._edNettomiete.textChanged.connect( self.onChange )
        self._edNkv = FloatEdit()
        self._edNkv.textChanged.connect( self.onChange )
        self._edKaution = IntEdit()
        self._edKaution.textChanged.connect( self.onChange )
        self._sdKautionBezahltAm = SmartDateEdit()
        self._sdKautionBezahltAm.textChanged.connect( self.onChange )
        self._txtBemerkung1 = MultiLineEdit()
        self._txtBemerkung1.textChanged.connect( self.onChange )
        self._txtBemerkung2 = MultiLineEdit()
        self._txtBemerkung2.textChanged.connect( self.onChange )
        self._createGui()
        if mietverhaeltnis:
            self.setMietverhaeltnisData( mietverhaeltnis )

    def onChange( self, newcontent:str=None ):
        if not self._btnSave.isEnabled():
            self.setSaveButtonEnabled()
        self.dataChanged.emit()

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

    def _createGui( self ):
        r = 0
        if self._withSaveButton:
            r = self._createSaveButton( r )
            r = self._addHorizontalLine( r )
        self._createFelder( r )
        self.setLayout( self._layout )

    def _createSaveButton( self, r:int ):
        btn = self._btnSave
        btn.clicked.connect( self.save.emit )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen am Mietverhältnis speichern" )
        icon = ImageFactory.inst().getSaveIcon()
        #icon = QIcon( "./images/save_30.png" )
        btn.setIcon( icon )
        size = QSize( 32, 32 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        hbox = QHBoxLayout()
        hbox.addWidget( btn )
        self._layout.addLayout( hbox, r, 0, alignment=Qt.AlignLeft )
        return r+1

    def _addHorizontalLine( self, r:int ):
        hline = HLine()
        self._layout.addWidget( hline, r, 0, 1, 2 )
        return r+1

    def _createFelder( self, r ):
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
        #self._edNettomiete.setEnabled( False )
        self._edNkv.setMaximumWidth( 100 )
        #self._edNkv.setEnabled( False )
        hbox = QHBoxLayout()
        hbox.addWidget( self._edNettomiete )
        hbox.addWidget( self._edNkv )
        hbox.addWidget( BaseLabel( "  Änderungen der Miete und NKV über Dialog 'Sollmiete'") )
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

        # cols = self._layout.columnCount()
        # print( cols, " columns" )

    def setNettoUndNkvEnabled( self, enabled:bool=True ):
        self._edNettomiete.setEnabled( enabled )
        self._edNkv.setEnabled( enabled )

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
        if mv.kaution:
            self._edKaution.setIntValue( mv.kaution )
        if mv.kaution_bezahlt_am:
            self._sdKautionBezahltAm.setDateFromIsoString( mv.kaution_bezahlt_am )
        self._txtBemerkung1.setText( mv.bemerkung1 )
        self._txtBemerkung2.setText( mv.bemerkung2 )

###############  MietverhaeltnisDialog  ##########################
class MietverhaeltnisDialog( OkCancelDialog ):
    def __init__(self, mietverhaeltnis:XMietverhaeltnis=None, parent=None):
        OkCancelDialog.__init__( self, parent )
        self.setWindowTitle( "Mietverhältnis " + mietverhaeltnis.mv_id + ": " + mietverhaeltnis.mobj_id )
        self._view = MietverhaeltnisView( mietverhaeltnis )
        self.addWidget( self._view, 0 )

    def getView( self ) -> MietverhaeltnisView:
        return self._view

def test():
    app = QApplication()
    v = MietverhaeltnisView( withSaveButton=True )
    v.show()
    app.exec_()