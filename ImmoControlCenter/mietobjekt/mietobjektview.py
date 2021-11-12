from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QFont, Qt, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QHBoxLayout, QPushButton

from definitions import ICON_DIR
from iccview import IccView
from interfaces import XMietobjektExt
from qtderivates import SmartDateEdit, BaseLabel, EditButton, \
    BaseBoldEdit, MultiLineEdit, HLine, LabelArial12, FixedWidth20Dummy, FixedWidthDummy, LabelTimes12, LabelTimesBold12


class FatLabel( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, parent )
        self._font = QFont( "Arial", 12, weight=QFont.Bold )
        self.setFont( self._font )

############### MieterwechselView ########################
class MietobjektView( IccView ):
    save_changes = Signal() # speichere Änderungen am Hauswart, der Masterobjekt-Bemerkung,
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
        self._lblMasterName = FatLabel()
        self._lblAdresse = FatLabel()
        self._lblAnzWhg = FatLabel()
        self._lblGesamtWfl = FatLabel()
        self._sdVeraeussertAm = SmartDateEdit()
        self._beHauswart = BaseBoldEdit()
        self._beHauswartTelefon = BaseBoldEdit()
        self._beHauswartMailto = BaseBoldEdit()
        self._meBemerkungMaster = MultiLineEdit()
        self._beWhgBez = BaseBoldEdit()
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
        self._btnSave.clicked.connect( self.save_changes.emit )
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
        self._lblMasterName.setText( x.master_name )
        hbl.addWidget( self._lblMasterName, alignment=Qt.AlignLeft )
        ####################### Dummy
        dummy = FixedWidth20Dummy()
        hbl.addWidget( dummy, alignment=Qt.AlignLeft )
        ##################### Adresse
        lbl = LabelArial12( "Adresse: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._lblAdresse.setText( x.strasse_hnr + ", " + x.plz + " " + x.ort )
        hbl.addWidget( self._lblAdresse, alignment=Qt.AlignLeft )
        ############# Anzahl Wohnungen
        r, c = r+1, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols, alignment=Qt.AlignCenter )
        lbl = LabelArial12( "Anzahl Wohng.: " )
        hbl.addWidget( lbl, alignment= Qt.AlignLeft )
        self._lblAnzWhg.setText( str( x.anz_whg ) )
        hbl.addWidget( self._lblAnzWhg, alignment= Qt.AlignLeft )
        ############# Dummy
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        ############  Gesamt-Wohnfläche
        lbl = LabelArial12( "Gesamt-Wohnfläche: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._lblGesamtWfl.setText( str( x.gesamt_wfl ) + " qm" )
        hbl.addWidget( self._lblGesamtWfl, alignment=Qt.AlignLeft )
        ################# Hauswart
        r, c = r+1, 0
        lbl = LabelArial12( "Hauswart: " )
        self._layout.addWidget( lbl, r, c )
        c = 1
        self._beHauswart.setText( x.hauswart )
        self._layout.addWidget( self._beHauswart, r, c )
        c = 2
        lbl = FixedWidth20Dummy()
        self._layout.addWidget( lbl, r, c )
        c = 3
        lbl = LabelArial12( "Telefon: " )
        self._layout.addWidget( lbl, r, c )
        c = 4
        self._beHauswartTelefon.setText( x.hauswart_telefon )
        self._layout.addWidget( self._beHauswartTelefon, r, c )
        c = 5
        lbl = FixedWidthDummy( 10 )
        self._layout.addWidget( lbl, r, c )
        c = 6
        lbl = LabelArial12( "mailto: " )
        self._layout.addWidget( lbl, r, c )
        c = 7
        self._beHauswartMailto.setText( x.hauswart_mailto )
        self._beHauswartMailto.setMinimumWidth( 250 )
        self._layout.addWidget( self._beHauswartMailto, r, c )
        #################### Bemerkung Master
        r, c = r+1, 0
        self._meBemerkungMaster.setText( x.bemerkung_masterobjekt )
        self._meBemerkungMaster.setMaximumHeight( 46 )
        self._meBemerkungMaster.setPlaceholderText( "<Bmerkungen zum Master-Objekt>" )
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
        #################### Container-Nr.
        r += 1
        c = 0
        lbl = LabelArial12( "Container-Nr." )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._beContainerNr.setText( x.container_nr )
        self._layout.addWidget( self._beContainerNr, r, c )
        r, c = r + 1, 0
        self._meBemerkungMobj.setText( x.bemerkung_mietobjekt )
        self._meBemerkungMobj.setPlaceholderText( "<Bemerkungen zur Wohnung (Mietobjekt)>" )
        self._meBemerkungMobj.setMaximumHeight( 46 )
        self._layout.addWidget( self._meBemerkungMobj, r, c, 1, self._anzCols )

    def getMietobjektCopyWithChanges( self ) -> XMietobjektExt:
        pass

    def clear( self ):
        pass

    def applyChanges( self ):
        pass

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
    x.master_name = "NK_Kleist"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Kleiststr. 3"
    x.anz_whg = 8
    x.gesamt_wfl = 432
    x.veraeussert_am = "21.12.2024"
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
    v.save_changes.connect( onSaveChanges )
    v.edit_verwaltung.connect( onEditVerwaltung )
    v.show()
    app.exec_()


if __name__ == "__main__":
    test()