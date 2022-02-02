import copy

from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QFont, Qt, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QHBoxLayout, QPushButton

from definitions import ICON_DIR
from icc.iccview import IccView
from interfaces import XMietobjektExt
from qtderivates import SmartDateEdit, BaseLabel, EditButton, \
    BaseBoldEdit, MultiLineEdit, HLine, LabelArial12, FixedWidth20Dummy, LabelTimes12, \
    LabelTimesBold12


class FatLabel( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, parent )
        self._font = QFont( "Arial", 12, weight=QFont.Bold )
        self.setFont( self._font )

############### MieterwechselView ########################
class MietobjektView( IccView ):
    save = Signal() # speichere Änderungen am Hauswart, der Masterobjekt-Bemerkung,
                            # des Mietobjekt-Containers und der Mietobjekt-Bemerkung
    edit_mieter = Signal()
    edit_miete = Signal()
    edit_verwaltung = Signal()
    edit_hausgeld = Signal()

    def __init__( self, x:XMietobjektExt ):
        IccView.__init__( self )
        self._mietobjekt = x
        self._btnSave = QPushButton()
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._anzCols = 8
        self._lblMasterId = FatLabel()
        #self._lblMasterName = FatLabel()
        self._bbeMasterName = BaseBoldEdit()
        #self._lblAdresse = FatLabel()
        self._bbeStrHnr = BaseBoldEdit()
        self._bbePlz = BaseBoldEdit()
        self._bbeOrt = BaseBoldEdit()
        #self._lblAnzWhg = FatLabel()
        self._bbeAnzWhg = BaseBoldEdit()
        #self._lblGesamtWfl = FatLabel()
        self._bbeGesamtWfl = BaseBoldEdit()
        self._sdVeraeussertAm = SmartDateEdit()
        self._beHauswart = BaseBoldEdit()
        self._beHauswartTelefon = BaseBoldEdit()
        self._beHauswartMailto = BaseBoldEdit()
        self._meBemerkungMaster = MultiLineEdit()
        self._beWhgBez = BaseBoldEdit()
        self._bbeQm = BaseBoldEdit()
        self._beContainerNr = BaseBoldEdit()
        self._meBemerkungMobj = MultiLineEdit()
        self._lblMieter = FatLabel()
        self._lblTelefonMieter = FatLabel()
        self._lblMailtoMieter = FatLabel()
        self._lblNettoMiete = FatLabel()
        self._lblNkv = FatLabel()
        self._lblKaution = FatLabel()
        self._lblVerwalter = FatLabel()
        self._lblWEG = FatLabel()
        self._lblHgvNetto = FatLabel()
        self._lblRueZuFue = FatLabel()
        self._lblHgvBrutto = FatLabel()

        self._createGui( x )
        self.connectWidgetsToChangeSlot()

    def _createGui( self, x:XMietobjektExt ):
        self._createToolBar( 0 )
        self._createHLine( 1 )
        self._createDummyRow( 2, 10 )
        r = self._createMasterDisplay( 3, x )
        self._createDummyRow( r + 1, 10 )
        self._createHLine( r + 2 )
        self._createMietObjektDisplay( r + 3, x )
        cols = self._layout.columnCount()
        self._layout.setColumnStretch( 7, 1 )
        rows = self._layout.rowCount()
        self._layout.setRowStretch( rows, 1 )

    def _createToolBar( self, r:int ):
        self._btnSave.setFixedSize( QSize( 30, 30 ) )
        self._btnSave.setIcon( QIcon( ICON_DIR + "save.png" ) )
        self._btnSave.setToolTip( "Änderungen des Hauswarts bzw. der Bemerkung des Master-Objekts speichern." )
        self._btnSave.clicked.connect( self.save.emit )
        tb = QHBoxLayout()
        tb.addWidget( self._btnSave )
        self._layout.addLayout( tb, r, 0, alignment=Qt.AlignLeft )

    def _createHLine( self, r:int ):
        line = HLine()
        self._layout.addWidget( line, r, 0, 1, self._anzCols )

    def _createDummyRow( self, r:int, h:int ):
        dummy = QWidget()
        dummy.setFixedHeight( h )
        self._layout.addWidget( dummy, r, 0 )

    def _createMasterDisplay( self, row:int, x:XMietobjektExt ) -> int:
        r, c = row, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols, alignment=Qt.AlignCenter )
        ####################### Master-ID
        lbl = LabelArial12( "Master-ID: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._lblMasterId.setText( str( x.master_id) )
        hbl.addWidget( self._lblMasterId, alignment=Qt.AlignLeft )
        ####################### Dummy
        dummy = FixedWidth20Dummy()
        hbl.addWidget( dummy, alignment=Qt.AlignLeft )
        ###################### Master-Name
        lbl = LabelArial12( "Master-Name: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeMasterName.setTextAndAdjustWidth( x.master_name )
        hbl.addWidget( self._bbeMasterName, alignment=Qt.AlignLeft )
        ####################### Dummy
        dummy = FixedWidth20Dummy()
        hbl.addWidget( dummy, alignment=Qt.AlignLeft )
        ##################### Straße
        lbl = LabelArial12( "Adresse: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeStrHnr.setTextAndAdjustWidth( x.strasse_hnr )
        hbl.addWidget( self._bbeStrHnr, alignment=Qt.AlignLeft )
        ###################### PLZ
        self._bbePlz.setTextAndAdjustWidth( x.plz )
        hbl.addWidget( self._bbePlz, alignment=Qt.AlignLeft )
        ###################### Ort
        self._bbeOrt.setTextAndAdjustWidth( x.ort )
        hbl.addWidget( self._bbeOrt, alignment=Qt.AlignLeft )
        ############# Anzahl Wohnungen
        r, c = r+1, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols, alignment=Qt.AlignCenter )
        lbl = LabelArial12( "Anzahl Wohng.: " )
        hbl.addWidget( lbl, alignment= Qt.AlignLeft )
        self._bbeAnzWhg.setText( str( x.anz_whg ) )
        self._bbeAnzWhg.setMaximumWidth( 25 )
        hbl.addWidget( self._bbeAnzWhg, alignment= Qt.AlignLeft )
        ############# Dummy
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        ############  Gesamt-Wohnfläche
        lbl = LabelArial12( "Gesamt-Wohnfläche (qm): " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeGesamtWfl.setText( str( x.gesamt_wfl ) )
        self._bbeGesamtWfl.setMaximumWidth( 45 )
        hbl.addWidget( self._bbeGesamtWfl, alignment=Qt.AlignLeft )
        ################# Dummy
        hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        ################# veräussert am
        lbl = LabelArial12( "veräußert am: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        if x.veraeussert_am:
            self._sdVeraeussertAm.setDateFromIsoString( x.veraeussert_am )
        self._sdVeraeussertAm.setFont( QFont( "Arial", 12, weight=QFont.Bold ) )
        self._sdVeraeussertAm.setMaximumWidth( 90 )
        hbl.addWidget( self._sdVeraeussertAm, alignment=Qt.AlignLeft )
        ################# Hauswart
        r, c = r+1, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols )
        lbl = LabelArial12( "Hauswart: " )
        #self._layout.addWidget( lbl, r, c, alignment=Qt.AlignCenter )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        #c = 1
        self._beHauswart.setTextAndAdjustWidth( x.hauswart )
        #self._layout.addWidget( self._beHauswart, r, c )
        hbl.addWidget( self._beHauswart, alignment=Qt.AlignLeft )
        #c = 2
        lbl = FixedWidth20Dummy()
        #self._layout.addWidget( lbl, r, c )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        #c = 3
        lbl = LabelArial12( "Telefon: " )
        #self._layout.addWidget( lbl, r, c )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        #c = 4
        self._beHauswartTelefon.setTextAndAdjustWidth( x.hauswart_telefon )
        #self._layout.addWidget( self._beHauswartTelefon, r, c )
        hbl.addWidget( self._beHauswartTelefon, alignment=Qt.AlignLeft )
        #c = 5
        #lbl = FixedWidthDummy( 10 )
        #self._layout.addWidget( lbl, r, c )
        #c = 6
        hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        lbl = LabelArial12( "mailto: " )
        #self._layout.addWidget( lbl, r, c )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        #c = 7
        self._beHauswartMailto.setText( x.hauswart_mailto )
        self._beHauswartMailto.setMinimumWidth( 250 )
        hbl.addWidget( self._beHauswartMailto, alignment=Qt.AlignLeft )
        #self._layout.addWidget( self._beHauswartMailto, r, c )

        #################### Bemerkung Master
        r, c = r+1, 0
        self._meBemerkungMaster.setText( x.bemerkung_masterobjekt )
        self._meBemerkungMaster.setMaximumHeight( 46 )
        self._meBemerkungMaster.setPlaceholderText( "<eBmerkungen zum Master-Objekt>" )
        self._layout.addWidget( self._meBemerkungMaster, r, c, 1, self._anzCols )

        return r

    def _createMietObjektDisplay( self, r: int, x: XMietobjektExt ):
        wrapper = QWidget()
        wrapper.setStyleSheet( "background: lightgray;" )
        hbl = QHBoxLayout()
        wrapper.setLayout( hbl )
        self._layout.addWidget( wrapper, r, 0, 1, self._anzCols )
        #################### Mietobjekt
        lbl = LabelTimes12( "Mietobjekt: " )
        hbl.addWidget( lbl, alignment=Qt.AlignRight )
        lbl = LabelTimesBold12( x.mobj_id )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        #################### Wohnungsbezeichnung
        lbl = LabelTimes12( "Bezeichnung: " )
        hbl.addWidget( lbl, alignment=Qt.AlignRight )
        self._beWhgBez.setText( x.whg_bez )
        self._beWhgBez.setStyleSheet( "background: white;" )
        hbl.addWidget( self._beWhgBez, alignment=Qt.AlignLeft )
        r += 1
        self._createHLine( r )
        #################### Mieter
        r, c = r+1, 0
        lbl = BaseLabel( "Mieter: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblMieter.setText( x.mieter )
        self._layout.addWidget( self._lblMieter, r, c, 1, 2 )
        ############################# Telefon + mobil Mieter
        c += 2
        lbl = BaseLabel( "Tel.: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblTelefonMieter.setText( x.telefon_mieter )
        self._layout.addWidget( self._lblTelefonMieter, r, c )
        ############################## Mailto Mieter
        c += 1
        lbl = BaseLabel( "mailto: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c += 1
        self._lblMailtoMieter.setText( x.mailto_mieter )
        self._layout.addWidget( self._lblMailtoMieter, r, c, 1, 2 )
        ################################## Button Edit Mietverhältnis
        c = 7
        btn = EditButton()
        btn.clicked.connect( self.edit_mieter.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        #################### Netto-Miete und NKV
        r, c = r+1, 0
        lbl = BaseLabel( "Netto-Miete: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblNettoMiete.setText( str( x.nettomiete ) )
        self._layout.addWidget( self._lblNettoMiete, r, c )
        c += 2 # NKV-Label soll linksbündig mit Tel.-Label des Master-Objekts sein
        lbl = BaseLabel( "NKV: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblNkv.setText( str( x.nkv ) )
        self._layout.addWidget( self._lblNkv, r, c )
        c += 1
        lbl = BaseLabel( "Kaution: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c += 1
        self._lblKaution.setText( str( x.kaution ) )
        self._layout.addWidget( self._lblKaution, r, c )
        ######################### Button Edit Miete
        c = 7
        btn = EditButton()
        btn.clicked.connect( self.edit_miete.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        #################### Verwalter
        r, c = r+1, 0
        lbl = BaseLabel( "Verwalter: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblVerwalter.setText( x.verwalter )
        self._layout.addWidget( self._lblVerwalter, r, c )
        #################### WEG-Name
        c += 2
        lbl = BaseLabel( "WEG-Name: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblWEG.setText( x.weg_name )
        self._layout.addWidget( self._lblWEG, r, c, 1, 4 )
        ######################## Button Edit Verwaltung
        c = 7
        btn = EditButton()
        btn.clicked.connect( self.edit_verwaltung.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        #################### HGV und RüZuFü
        r, c = r+1, 0
        lbl = BaseLabel( "HGV netto: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblHgvNetto.setText( str( x.hgv_netto ) )
        self._layout.addWidget( self._lblHgvNetto, r, c )
        c += 2
        lbl = BaseLabel( "RüZuFü: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblRueZuFue.setText( str( x.ruezufue ) )
        self._layout.addWidget( self._lblRueZuFue, r, c )
        c += 1
        lbl = BaseLabel( "HGV brutto: ")
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblHgvBrutto.setText( str( x.hgv_brutto) )
        self._layout.addWidget( self._lblHgvBrutto, r, c )
        ############################# Button Edit HGV
        c += 1
        btn = EditButton()
        btn.clicked.connect( self.edit_hausgeld.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        r += 1
        self._createDummyRow( r, 10 )
        #################### qm
        r, c = r+1, 0
        hbl = QHBoxLayout()
        hbl.addWidget( LabelArial12( "qm: " ), alignment=Qt.AlignLeft )
        self._bbeQm.setTextAndAdjustWidth( str( x.qm ) )
        hbl.addWidget( self._bbeQm, alignment=Qt.AlignLeft )
        #################### Dummy
        hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        #################### Container-Nr.
        #r += 1
        #c = 0
        #lbl = LabelArial12( "Container-Nr." )
        #self._layout.addWidget( lbl, r, c )
        hbl.addWidget( LabelArial12( "Container-Nr." ), alignment=Qt.AlignLeft )
        #c += 1
        self._beContainerNr.setTextAndAdjustWidth( x.container_nr )
        #self._layout.addWidget( self._beContainerNr, r, c )
        hbl.addWidget( self._beContainerNr, alignment=Qt.AlignLeft )
        self._layout.addLayout( hbl, r, c )
        ###################### Bemerkung zum Mietobjekt
        r, c = r + 1, 0
        self._meBemerkungMobj.setText( x.bemerkung_mietobjekt )
        self._meBemerkungMobj.setPlaceholderText( "<Bemerkungen zur Wohnung (Mietobjekt)>" )
        self._meBemerkungMobj.setMaximumHeight( 46 )
        self._layout.addWidget( self._meBemerkungMobj, r, c, 1, self._anzCols )

    def getMietobjektCopyWithChanges( self ) -> XMietobjektExt:
        xcopy:XMietobjektExt = copy.copy( self._mietobjekt )
        raise NotImplementedError( "MietobjektView.getMietobjektCopyWithChanges()" )

    def _guiToData( self, x:XMietobjektExt ):
        x.master_name = self._bbeMasterName.text()
        raise NotImplementedError( "MietobjektView._guiToData()" )

    def clear( self ):
        raise NotImplementedError( "MietobjektView.clear()" )

    def applyChanges( self ):
        raise NotImplementedError( "MietobjektView.applyChanges()" )

    def getModel( self ):
        return self._mietobjekt

#################################################################################
def onSaveChanges():
    print( "onSaveChanges" )

def onEditVerwaltung():
    print( "onEditVerwaltung" )

def test():
    x = XMietobjektExt()
    x.master_id = 17
    x.master_name = "BUEB_Saargemuend"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Klabautermannstraße 377"
    x.anz_whg = 8
    x.gesamt_wfl = 432
    x.veraeussert_am = "2024-12-01"
    x.hauswart = "Hans-Jörg Müller"
    x.hauswart_telefon = "06821 / 123456"
    x.hauswart_mailto = "mueller-hauswart@t-online.de"
    x.bemerkung_masterobjekt = "Außen hui Innen pfui"
    x.mobj_id = "kleist_11"
    x.whg_bez = "1. OG links"
    x.qm = 50
    x.container_nr = "098765/11"
    x.bemerkung_mietobjekt = "Wird unser HQ im Saarland"
    x.mieter = "Graf von Strübel-Lakaiendorf, Christian-Eberhard"
    x.nettomiete = 234.56
    x.nkv = 87.69
    x.verwalter = "GfH Häuserkacke"
    x.weg_name = "WEG Beispielstraße 22, 55432 Mühlheim"
    x.hgv_netto = 300.00
    x.ruezufue = 67.89
    x.hgv_brutto = 367.89

    app = QApplication()
    v = MietobjektView( x )
    v.save.connect( onSaveChanges )
    v.edit_verwaltung.connect( onEditVerwaltung )
    v.show()
    app.exec_()


if __name__ == "__main__":
    test()