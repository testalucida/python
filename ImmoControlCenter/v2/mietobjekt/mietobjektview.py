import copy

from PySide2.QtCore import Signal
from PySide2.QtGui import Qt, QFont
from PySide2.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QApplication

from base.baseqtderivates import FatLabel, BaseBoldEdit, LabelTimesBold12, SmartDateEdit, MultiLineEdit, HLine, \
    LabelTimes12, BaseLabel, EditIconButton, LabelArial12
from generictable_stuff.okcanceldialog import OkDialog, OkCancelDialog
from v2.icc.iccwidgets import IccTableView
from v2.icc.interfaces import XMietobjektExt

######################   MietobjektAuswahlView   #############################
class MietobjektAuswahlTableView( IccTableView ):
    """
    Wird im MietobjektAuswahlDialog verwendet
    """
    def __init__( self ):
        IccTableView.__init__( self )
        self.setAlternatingRowColors( True )

######################   MietobjektView   #############################
class MietobjektView( QWidget ):
    # save = Signal()  # speichere Änderungen am Hauswart, der Masterobjekt-Bemerkung,
    # des Mietobjekt-Containers und der Mietobjekt-Bemerkung
    edit_mieter = Signal( str ) # mv_id
    edit_miete = Signal( str ) # mv_id
    edit_hausgeld = Signal( str ) # mobj_id

    def __init__( self, x: XMietobjektExt ):
        QWidget.__init__( self )
        self._mietobjekt = x
        #self._btnSave = QPushButton()
        self._layout = QGridLayout()
        self._anzCols = 12
        self.setLayout( self._layout )
        # masterobjekt fields
        self._lblMasterId = FatLabel()
        self._bbeMasterName = LabelTimesBold12()
        self._bbeStrHnr = BaseBoldEdit()
        self._bbePlz = BaseBoldEdit()
        self._bbeOrt = BaseBoldEdit()
        self._bbeAnzWhg = BaseBoldEdit()
        self._bbeGesamtWfl = BaseBoldEdit()
        self._lblVerwalter = FatLabel()
        self._lblWEG = FatLabel()
        self._sdVeraeussertAm = SmartDateEdit()
        self._beHauswart = BaseBoldEdit()
        self._beHauswartTelefon = BaseBoldEdit()
        self._beHauswartMailto = BaseBoldEdit()
        self._meBemerkungMaster = MultiLineEdit()
        # mietobjekt fields
        self._lblMietobjekt = LabelTimesBold12()
        self._beWhgBez = LabelTimesBold12()
        self._bbeQm = BaseBoldEdit()
        self._beContainerNr = BaseBoldEdit()
        self._meBemerkungMobj = MultiLineEdit()
        self._lblMieter = FatLabel()
        self._lblTelefonMieter = FatLabel()
        self._lblMailtoMieter = FatLabel()
        self._lblNettoMiete = FatLabel()
        self._lblNkv = FatLabel()
        self._lblBruttoMiete = FatLabel()
        self._lblKaution = FatLabel()

        self._lblHgvNetto = FatLabel()
        self._lblRueZuFue = FatLabel()
        self._lblHgvBrutto = FatLabel()

        self._createGui( x )
        self.setData( x )
        #self.connectWidgetsToChangeSlot( self.onChange, self.onResetChangeFlag )

    def _createGui( self, x:XMietobjektExt ):
        self._layout.setVerticalSpacing( 15 )
        #self._createToolBar( 0 )
        # self._createHLine( 1, self._anzCols )
        # self._createDummyRow( 2, 10 )
        row = self._createMasterDisplay( 0 )
        # self._createDummyRow( 4, 10 )
        # self._createHLine( 5 )
        self._createMietObjektDisplay( row )
        # cols = self._layout.columnCount()
        # self._layout.setColumnStretch( 7, 1 )
        # rows = self._layout.rowCount()
        # self._layout.setRowStretch( rows, 1 )


    # def _createToolBar( self, r: int ):
    #     self._btnSave.setFixedSize( QSize( 30, 30 ) )
    #     self._btnSave.setIcon( QIcon( ICON_DIR + "save.png" ) )
    #     self._btnSave.setToolTip( "Änderungen des Hauswarts bzw. der Bemerkung des Master-Objekts speichern." )
    #     self._btnSave.setEnabled( False )
    #     self._btnSave.clicked.connect( self.save.emit )
    #     tb = QHBoxLayout()
    #     tb.addWidget( self._btnSave )
    #     self._layout.addLayout( tb, r, 0, alignment=Qt.AlignLeft )

    def _createHLine( self, r: int, columns:int=-1 ):
        line = HLine()
        if columns < 0: columns = self._layout.columnCount()
        self._layout.addWidget( line, r, 0, 1, columns )

    def _createDummyRow( self, r: int, h: int ):
        dummy = QWidget()
        dummy.setFixedHeight( h )
        self._layout.addWidget( dummy, r, 0 )

    def _createMasterDisplay( self, row: int ) -> int:
        #l = GridLayout()
        l = self._layout
        #self._layout.addLayout( l, row, 0, 1, self._anzCols )
        # l.setVerticalSpacing( 15 )
        r = row
        def _createMasterHeader( r:int ) -> int:
            self._createHLine( r, self._anzCols )
            r += 1
            wrapper = QWidget()
            wrapper.setStyleSheet( "background: lightgray;" )
            hbl = QHBoxLayout()
            wrapper.setLayout( hbl )
            self._layout.addWidget( wrapper, r, 0, 1, self._anzCols )
            #################### Master-ID
            lbl = LabelTimes12( "Master-ID: " )
            hbl.addWidget( lbl, alignment=Qt.AlignRight )
            hbl.addWidget( self._lblMasterId, alignment=Qt.AlignLeft )
            #################### Master-Name
            lbl = LabelTimes12( "Master-Name: " )
            hbl.addWidget( lbl, alignment=Qt.AlignRight )
            self._bbeMasterName.setText( "Dummy-Master" )
            #self._bbeMasterName.setStyleSheet( "background: white;" )
            hbl.addWidget( self._bbeMasterName, alignment=Qt.AlignLeft )
            r += 1
            self._createHLine( r )
            return r

        def _createMasterAddress( r: int ) -> int:
            #disabledFont = QFont( "Arial", 12, QFont.Bold )
            c = 0
            lbl = BaseLabel( "Adresse: " )
            l.addWidget( lbl, r, c )
            c = 1
            self._bbePlz.setMaximumWidth( 60 )
            self._bbePlz.setEnabled( False )
            self._bbePlz.setTextColor( "black" )
            l.addWidget( self._bbePlz, r, c )
            c = 2
            self._bbeOrt.setEnabled( False )
            self._bbeOrt.setTextColor( "black" )
            l.addWidget( self._bbeOrt, r, c, 1, 4 )
            c = 6
            self._bbeStrHnr.setEnabled( False )
            self._bbeStrHnr.setTextColor( "black" )
            l.addWidget( self._bbeStrHnr, r, c, 1, 7 )
            return r

        def _createMasterMore( r:int ) -> int:
            c = 0
            lbl = BaseLabel( "Anzahl Whg.: " )
            l.addWidget( lbl, r, c )
            c += 1
            self._bbeAnzWhg.setEnabled( False )
            self._bbeAnzWhg.setMaximumWidth( 40 )
            l.addWidget( self._bbeAnzWhg, r, c )
            c = 4
            lbl = BaseLabel( "Gesamt-Wfl.(qm):" )
            l.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
            c += 1
            self._bbeGesamtWfl.setEnabled( False )
            self._bbeGesamtWfl.setMaximumWidth( 40 )
            l.addWidget( self._bbeGesamtWfl, r, c )
            return r

        def _createVerwalter( r:int ) -> int:
            #################### Verwalter
            c = 0
            lbl = BaseLabel( "Verwalter: " )
            self._layout.addWidget( lbl, r, c )
            c = 1
            self._layout.addWidget( self._lblVerwalter, r, c, 1, 3 )
            # #################### WEG-Name
            c = 4
            lbl = BaseLabel( "WEG-Name: " )
            self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
            c = 5
            self._layout.addWidget( self._lblWEG, r, c, 1, 4 )
            # ######################## Button Edit Verwaltung
            # c = 11
            # btn = EditIconButton()
            # btn.clicked.connect( self.edit_verwaltung.emit )
            # self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
            return r + 1

        def _createMasterHauswart( r: int ) -> int:
            c = 0
            lbl = BaseLabel( "Hauswart: " )
            l.addWidget( lbl, r, c )
            c = 1
            l.addWidget( self._beHauswart, r, c, 1, 3 )
            c = 4
            l.addWidget( BaseLabel( "Telefon: " ), r, c, 1, 1, alignment=Qt.AlignRight )
            c = 5
            l.addWidget( self._beHauswartTelefon, r, c, 1, 2 )
            c = 7
            l.addWidget( BaseLabel( "mailto:" ), r, c, 1, 1, alignment=Qt.AlignRight )
            c = 8
            l.addWidget( self._beHauswartMailto, r, c, 1, 4 )
            return r

        def _createVeraeussertAm( r:int ) -> int:
            c = 0
            l.addWidget( BaseLabel( "veräußert am:" ), r, c )
            c = 1
            self._sdVeraeussertAm.setMaximumWidth( 90 )
            l.addWidget( self._sdVeraeussertAm, r, c )
            return r

        r = _createMasterHeader( r )
        r = _createMasterAddress( r+1 )
        r = _createMasterMore( r+1 )
        r = _createVerwalter( r+1 )
        r = _createMasterHauswart( r+1 )
        r = _createVeraeussertAm( r+1 )
        r += 1
        self._meBemerkungMaster.setMaximumHeight( 50 )
        l.addWidget( self._meBemerkungMaster, r, 0, 1, self._anzCols )
        l.setRowStretch( r, 1 )
        return r + 1

    def _createMietObjektDisplay( self, r: int ): #, x: XMietobjektExt ):
        self._createHLine( r, self._anzCols )
        r += 1
        wrapper = QWidget()
        wrapper.setStyleSheet( "background: lightgray;" )
        hbl = QHBoxLayout()
        wrapper.setLayout( hbl )
        self._layout.addWidget( wrapper, r, 0, 1, self._anzCols )
        #################### Mietobjekt
        lbl = LabelTimes12( "Mietobjekt: " )
        hbl.addWidget( lbl, alignment=Qt.AlignRight )
        hbl.addWidget( self._lblMietobjekt, alignment=Qt.AlignLeft )
        #################### Wohnungsbezeichnung
        lbl = LabelTimes12( "Bezeichnung: " )
        hbl.addWidget( lbl, alignment=Qt.AlignRight )
        #self._beWhgBez.setStyleSheet( "background: white;" )
        hbl.addWidget( self._beWhgBez, alignment=Qt.AlignLeft )
        r += 1
        self._createHLine( r )
        #################### Mieter
        r, c = r + 1, 0
        lbl = BaseLabel( "Mieter: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        #self._lblMieter.setText()
        self._layout.addWidget( self._lblMieter, r, c, 1, 4 )
        ############################# Telefon + mobil Mieter
        c += 5
        lbl = BaseLabel( "Tel.: " )
        self._layout.addWidget( lbl, r, c, alignment=Qt.AlignRight )
        c += 1
        #self._lblTelefonMieter.setText( x.telefon_mieter )
        self._layout.addWidget( self._lblTelefonMieter, r, c )
        ############################## Mailto Mieter
        c += 1
        lbl = BaseLabel( "mailto: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c += 1
        #self._lblMailtoMieter.setText( x.mailto_mieter )
        self._layout.addWidget( self._lblMailtoMieter, r, c, 1, 2 )
        ################################## Button Edit Mietverhältnis
        c = 11
        btn = EditIconButton()
        btn.clicked.connect( lambda x: self.edit_mieter.emit( self._mietobjekt.mv_id ) )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        #################### Netto-Miete und NKV
        r, c = r + 1, 0
        lbl = BaseLabel( "Netto-Miete: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        #self._lblNettoMiete.setText( str( x.nettomiete ) )
        self._layout.addWidget( self._lblNettoMiete, r, c )
        c = 2  # NKV-Label soll linksbündig mit Tel.-Label des Master-Objekts sein
        lbl = BaseLabel( "NKV: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c = 3
        #self._lblNkv.setText( str( x.nkv ) )
        self._layout.addWidget( self._lblNkv, r, c )
        c = 4
        lbl = BaseLabel( "Miete brutto: " )
        self._layout.addWidget( lbl, r, c, alignment=Qt.AlignRight )
        c = 5
        self._layout.addWidget( self._lblBruttoMiete, r, c )
        c = 8
        lbl = BaseLabel( "Kaution: " )
        self._layout.addWidget( lbl, r, c, alignment=Qt.AlignRight )
        c = 9
        self._layout.addWidget( self._lblKaution, r, c )
        # ######################### Button Edit Miete
        c = 11
        btn = EditIconButton()
        btn.clicked.connect( lambda x: self.edit_miete.emit( self._mietobjekt.mv_id ) )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        # #################### HGV und RüZuFü
        r, c = r + 1, 0
        lbl = BaseLabel( "HGV netto: " )
        self._layout.addWidget( lbl, r, c )
        c = 1
        #self._lblHgvNetto.setText( str( x.hgv_netto ) )
        self._layout.addWidget( self._lblHgvNetto, r, c )
        c = 2
        lbl = BaseLabel( "RüZuFü: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c = 3
        #self._lblRueZuFue.setText( str( x.ruezufue ) )
        self._layout.addWidget( self._lblRueZuFue, r, c )
        c = 4
        lbl = BaseLabel( "HGV brutto: " )
        self._layout.addWidget( lbl, r, c, alignment=Qt.AlignRight )
        c = 5
        #self._lblHgvBrutto.setText( str( x.hgv_brutto ) )
        self._layout.addWidget( self._lblHgvBrutto, r, c )
        # ############################# Button Edit HGV
        c = 11
        btn = EditIconButton()
        btn.clicked.connect( lambda x: self.edit_hausgeld.emit( self._mietobjekt.mobj_id ) )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        # #################### qm
        r, c = r + 1, 0
        lbl = LabelArial12( "qm: " )
        self._layout.addWidget( lbl, r, c )
        c = 1
        self._bbeQm.setMaximumWidth( 40 )
        #self._bbeQm.setText( str( x.qm ) )
        self._bbeQm.setEnabled( False )
        self._layout.addWidget( self._bbeQm, r, c )
        #################### Container-Nr.
        c = 2
        lbl = LabelArial12( "Container-Nr.:" )
        self._layout.addWidget( lbl, r, c, alignment=Qt.AlignRight )
        c = 3
        self._layout.addWidget( self._beContainerNr, r, c, 1, 4 )
        # ###################### Bemerkung zum Mietobjekt
        r, c = r + 1, 0
        #self._meBemerkungMobj.setText( x.bemerkung_mietobjekt )
        self._meBemerkungMobj.setPlaceholderText( "<Bemerkungen zur Wohnung (Mietobjekt)>" )
        self._meBemerkungMobj.setMaximumHeight( 46 )
        self._layout.addWidget( self._meBemerkungMobj, r, c, 1, self._anzCols )
        self._layout.setRowStretch( r, 1 )

    def setData( self, x: XMietobjektExt ):
        self._dataToGui( x )

    def getMietobjektCopyWithChanges( self ) -> XMietobjektExt:
        xcopy: XMietobjektExt = copy.copy( self._mietobjekt )
        self._guiToData( xcopy )
        return xcopy

    def _dataToGui( self, x:XMietobjektExt ):
        # data für Masterobjekt
        self._lblMasterId.setText( str( x.master_id ) )
        self._bbeMasterName.setText( x.master_name )
        self._bbeStrHnr.setText( x.strasse_hnr )
        self._bbeStrHnr.setCursorPosition( 0 )
        self._bbePlz.setText( x.plz )
        self._bbeOrt.setText( x.ort )
        self._bbeAnzWhg.setText( str( x.anz_whg ) )
        self._bbeGesamtWfl.setText( str( x.gesamt_wfl ) )
        self._lblVerwalter.setText( x.verwalter )
        self._lblWEG.setText( x.weg_name )
        self._beHauswart.setText( x.hauswart )
        self._beHauswart.setCursorPosition( 0 )
        self._beHauswartTelefon.setText( x.hauswart_telefon )
        self._beHauswartMailto.setText( x.hauswart_mailto )
        self._beHauswartMailto.setCursorPosition( 0 )
        if x.veraeussert_am:
            self._sdVeraeussertAm.setDateFromIsoString( x.veraeussert_am )
        self._meBemerkungMaster.setText( x.bemerkung_masterobjekt )
        # data für Mietobjekt
        self._lblMietobjekt.setText( x.mobj_id )
        self._beWhgBez.setText( x.whg_bez )
        self._lblMieter.setText( x.mieter )
        self._lblTelefonMieter.setText( x.telefon_mieter )
        self._lblMailtoMieter.setText( x.mailto_mieter )
        self._lblNettoMiete.setText( str(x.nettomiete) )
        self._lblNkv.setText( str(x.nkv) )
        self._lblBruttoMiete.setText( str(x.nettomiete + x.nkv) )
        self._lblKaution.setText( str(x.kaution) )
        self._lblHgvNetto.setText( str(x.hgv_netto) )
        self._lblRueZuFue.setText( str(x.ruezufue) )
        self._lblHgvBrutto.setText( str(x.hgv_brutto) )
        self._bbeQm.setText( str(x.qm) )
        self._beContainerNr.setText( x.container_nr )
        self._meBemerkungMobj.setText( x.bemerkung_mietobjekt )

    def _guiToData( self, x: XMietobjektExt ):
        # Masterobjekt
        x.strasse_hnr = self._bbeStrHnr.text()
        x.plz = self._bbePlz.text()
        x.ort = self._bbeOrt.text()
        x.verwalter = self._lblVerwalter.text()
        x.weg_name = self._lblWEG.text()
        x.veraeussert_am = self._sdVeraeussertAm.getDate()
        x.hauswart = self._beHauswart.text()
        x.hauswart_telefon = self._beHauswartTelefon.text()
        x.hauswart_mailto = self._beHauswartMailto.text()
        x.bemerkung_masterobjekt = self._meBemerkungMaster.toPlainText()
        # Mietobjekt
        x.whg_bez = self._beWhgBez.text()
        x.container_nr = self._beContainerNr.text()
        x.bemerkung_mietobjekt = self._meBemerkungMobj.toPlainText()

    def applyChanges( self ):
        self._guiToData( self._mietobjekt )

    def onChange( self ):
        self._btnSave.setEnabled( True )

    def onResetChangeFlag( self ):
        self._btnSave.setEnabled( False )

    def getModel( self ):
        return self._mietobjekt

##################   MietobjektDialog   ######################
class MietobjektDialog( OkCancelDialog ):
    def __init__( self, view:MietobjektView, title:str="" ):
        # OkDialog.__init__( self, title + " (nur Ansicht, Änderungen noch nicht möglich)" )
        OkCancelDialog.__init__( self, title  )
        self._view = view
        self.addWidget( view, 0 )
        # self.setOkButtonText( "Schließen (derzeit ohne Speichern)" )
        self.setOkButtonText( "OK" )
    #     self.setBeforeAcceptFunction( self.onOk )
    #
    # def onOk( self ) -> bool:
    #     print( "onOk" )
    #     return False



##################   TEST   TEST   TEST   #####################
# def onSaveChanges():
#     print( "onSaveChanges" )
#
# def onEditVerwaltung():
#     print( "onEditVerwaltung" )

def test():
    def validate() -> bool:
        print( "vasliddate")
        print( "mobj_id: ", x.mobj_id )
        return True

    x = XMietobjektExt()
    x.master_id = 17
    x.master_name = "NK-Kleist"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Klabautermannstraße 377"
    x.anz_whg = 8
    x.gesamt_wfl = 432
    x.veraeussert_am = "2024-12-01"
    x.hauswart = "Hans-Jürgen Müller-Westernhagen"
    x.hauswart_telefon = "06821 / 123456"
    x.hauswart_mailto = "mueller-hauswart@t-online.de"
    x.bemerkung_masterobjekt = "Außen hui Innen pfui"
    x.mobj_id = "kleist_11"
    x.whg_bez = "1. OG links"
    x.qm = 50
    x.container_nr = "098765/11"
    x.bemerkung_mietobjekt = "Wird unser HQ im Saarland"
    x.mieter = "Graf von Strübel-Lakaiendorf, Christian-Eberhard"
    x.telefon_mieter = "0171 / 11211345"
    x.mailto_mieter = "grastruelakai@t-online.de"
    x.nettomiete = 234.56
    x.nkv = 87.69
    x.verwalter = "GfH Häuserkacke und Versagen garantiert"
    x.weg_name = "WEG Beispielstraße 22, 55432 Mühlheim"
    x.hgv_netto = 300.00
    x.ruezufue = 67.89
    x.hgv_brutto = 367.89

    app = QApplication()
    v = MietobjektView( x )
    #v.save.connect( onSaveChanges )
    #v.show()
    dlg = MietobjektDialog( v, x.mobj_id )
    dlg.setBeforeAcceptFunction( validate )
    #dlg.exec_()
    dlg.show()
    app.exec_()
