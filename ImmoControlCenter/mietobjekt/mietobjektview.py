import copy

from PySide2.QtCore import QSize, Signal
from PySide2.QtGui import QFont, Qt, QIcon
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QHBoxLayout, QPushButton, QLineEdit, QFormLayout, \
    QSpacerItem

from clearable import Clearable
from definitions import ICON_DIR
from icc.iccview import IccView
from interfaces import XMietobjektExt
from modifiyinfo import ModifyInfo
from qtderivates import SmartDateEdit, BaseLabel, EditButton, \
    BaseBoldEdit, MultiLineEdit, HLine, LabelArial12, FixedWidth20Dummy, LabelTimes12, \
    LabelTimesBold12


class FormLayout( QFormLayout ):
    def __init__( self ):
        QFormLayout.__init__( self )

    def addRow2( self, *args ):
        hbox = QHBoxLayout()
        for arg in args:
            if isinstance( arg, str ):
                lbl = BaseLabel()
                lbl.setTextAndAdjustWidth( arg )
                hbox.addWidget( lbl )
            elif isinstance( arg, int ):
                vdummy = QWidget()
                vdummy.setFixedWidth( arg )
                hbox.addWidget( vdummy )
            else:
                hbox.addWidget( arg )
        self.addRow( hbox )

def test2():
    app = QApplication()
    v = QWidget()
    f = FormLayout()
    v.setLayout( f )

    w1 = BaseBoldEdit()
    w1.setText( "123" )
    w1.setMaximumWidth( 60 )
    w2 = BaseBoldEdit()
    w2.setText( "BUEB_Saargemünd" )
    f.addRow2( "ID", w1, 10, "Master-Name:", w2 )
    w3 = BaseBoldEdit( "Klabautermannstr. 22" )
    w4 = BaseBoldEdit( "98766" )
    w5 = BaseBoldEdit( "Hintervordertupfing" )
    f.addRow2( "Adresse: ", w3, w4, w5 )

    v.show()
    app.exec_()

class GridLayout( QGridLayout ):
    def __init__(self):
        QGridLayout.__init__( self )

    def setColumnStretches( self, *args ):
        """
        :param args: Jedes Argument ist ein Tuple, bestehend aus dem Column-Index und dem Stretchfaktor für diese Column.
        :return:
        """
        for arg in args:
            self.setColumnStretch( arg[0], arg[1] )

    def setNoColumnStretches( self ):
        cols = self.columnCount()
        for c in range( 0, cols ):
            self.setColumnStretch( c, 0 )

    def stretchOnlyLastColumn( self ):
        self.setNoColumnStretches()
        self.setColumnStretch( self.columnCount()-1, 1 )

    def addRow( self, row:int, *args ):
        """
        :param row:
        :param args: Jedes Argument ist ein Tuple, bestehend aus
            1. einem String oder einem QWidget
            2. der Column-Span-Angabe
            3. (optional) der Align-Angabe
        :return:
        """
        c = 0
        for arg in args:
            if isinstance( arg, tuple ):
                rowspan = 1
                align = Qt.AlignLeft
                e1 = arg[0]
                colspan = arg[1]
                if len( arg ) == 3:
                    align = arg[2]
                if isinstance( e1, str ):
                    w = BaseLabel()
                    w.setTextAndAdjustWidth( e1 )
                else:
                    w = e1
                if align == Qt.AlignLeft:
                    self.addWidget( w, row, c, rowspan, colspan )
                else:
                    self.addWidget( w, row, c, rowspan, colspan, alignment=align )
                c += colspan
            elif isinstance( arg, int ):
                vdummy = QWidget()
                vdummy.setFixedWidth( arg )
                c += 1
            else:
                raise Exception( "Illegal Argument" )

def test3():
    app = QApplication()
    v = QWidget()
    f = GridLayout()
    v.setLayout( f )

    hw = BaseBoldEdit()
    hw.setText( "Hans Jürgen Müller" )
    tel = BaseBoldEdit()
    tel.setText( "06567/123456" )
    mail = BaseBoldEdit( "mueller-hauswart@t-online.de" )
    f.addRow( 0, ("Hauswart:", 1), (hw, 2), ("Telefon:", 2), (tel, 2), ("mailto:", 1), (mail, 2) )

    st = BaseBoldEdit( "Klabautermannstr. 22" )
    plz = BaseBoldEdit( "98766" )
    plz.setMaximumWidth(70)
    ort = BaseBoldEdit( "Hintervordertupfing" )
    f.addRow( 1, ("Adresse:", 1), (st, 2), (plz, 2), (ort, 5 ) )
    # f.addWidget( BaseBoldEdit( "COL 0" ), 2, 0, 1, 1 )
    # f.addWidget( BaseBoldEdit( "COL 1" ), 2, 1, 1, 1 )
    f.addRow( 2, (BaseBoldEdit( "COL 0" ), 1), (BaseBoldEdit( "COL 1" ), 2) )
    #f.stretchOnlyLastColumn()
    f.setColumnStretches( (1, 1 ) )
    print( f.columnCount(), " columns" )
    v.show()
    app.exec_()


class FatLabel( BaseLabel ):
    def __init__( self, text:str="", parent=None ):
        BaseLabel.__init__( self, parent )
        self._font = QFont( "Arial", 12, weight=QFont.Bold )
        self.setFont( self._font )

############### MieterwechselView ########################

class MietobjektView_inArbeit( QWidget, ModifyInfo ):  # IccView ):
    save = Signal()  # speichere Änderungen am Hauswart, der Masterobjekt-Bemerkung,
    # des Mietobjekt-Containers und der Mietobjekt-Bemerkung
    edit_mieter = Signal()
    edit_miete = Signal()
    edit_verwaltung = Signal()
    edit_hausgeld = Signal()

    def __init__( self, x: XMietobjektExt ):
        QWidget.__init__( self )
        ModifyInfo.__init__( self )
        Clearable.__init__( self )
        self._mietobjekt = x
        self._btnSave = QPushButton()
        self._layout = QGridLayout()
        self._anzCols = 12
        self.setLayout( self._layout )
        self._lblMasterId = FatLabel()
        self._bbeMasterName = BaseBoldEdit()
        self._bbeStrHnr = BaseBoldEdit()
        self._bbePlz = BaseBoldEdit()
        self._bbeOrt = BaseBoldEdit()
        self._bbeAnzWhg = BaseBoldEdit()
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
        self.setData( x )
        self.connectWidgetsToChangeSlot( self.onChange, self.onResetChangeFlag )

    def _createGui( self, x:XMietobjektExt ):
        self._createToolBar( 0 )
        self._createHLine( 1, self._anzCols )
        self._createDummyRow( 2, 10 )
        self._createMasterDisplay( 3 )
        # self._createDummyRow( 4, 10 )
        # self._createHLine( 5 )
        self._createMietObjektDisplay( 6, x )
        # cols = self._layout.columnCount()
        # self._layout.setColumnStretch( 7, 1 )
        # rows = self._layout.rowCount()
        # self._layout.setRowStretch( rows, 1 )


    def _createToolBar( self, r: int ):
        self._btnSave.setFixedSize( QSize( 30, 30 ) )
        self._btnSave.setIcon( QIcon( ICON_DIR + "save.png" ) )
        self._btnSave.setToolTip( "Änderungen des Hauswarts bzw. der Bemerkung des Master-Objekts speichern." )
        self._btnSave.setEnabled( False )
        self._btnSave.clicked.connect( self.save.emit )
        tb = QHBoxLayout()
        tb.addWidget( self._btnSave )
        self._layout.addLayout( tb, r, 0, alignment=Qt.AlignLeft )

    def _createHLine( self, r: int, columns:int=-1 ):
        line = HLine()
        if columns < 0: columns = self._layout.columnCount()
        self._layout.addWidget( line, r, 0, 1, columns )

    def _createDummyRow( self, r: int, h: int ):
        dummy = QWidget()
        dummy.setFixedHeight( h )
        self._layout.addWidget( dummy, r, 0 )

    def _createMasterDisplay( self, row: int ) -> int:
        l = GridLayout()
        self._layout.addLayout( l, row, 0, 1, self._anzCols )
        l.setVerticalSpacing( 15 )
        r = 0
        # Master-ID und Master-Name
        hbl = QHBoxLayout()
        hbl.addWidget( QWidget(), stretch=1, alignment=Qt.AlignLeft )
        hbl.addWidget( LabelArial12("Master-ID: " ), stretch=0, alignment=Qt.AlignLeft )
        hbl.addWidget( self._lblMasterId )
        hbl.addSpacing( 30 )

        self._bbeMasterName.setEnabled( False )
        hbl.addWidget( LabelArial12("Master-Name: " ), stretch=0, alignment=Qt.AlignLeft )
        hbl.addWidget( self._bbeMasterName, Qt.AlignLeft )
        hbl.addWidget( QWidget(), stretch=1, alignment=Qt.AlignLeft )
        l.addLayout( hbl, r, 0, 1, self._anzCols, Qt.AlignCenter )

        r += 1
        hline = HLine()
        l.addWidget( hline, r, 0, 1, self._anzCols )

        # Adresse
        r += 1
        self._bbePlz.setMaximumWidth( 60 )
        l.addRow( r, ("Adresse: ", 1 ), (self._bbeStrHnr, 2), (self._bbePlz, 2, Qt.AlignRight), (self._bbeOrt, 4) )
        # ...Anzahl Whgen u. Wohnfläche
        r += 1
        self._bbeAnzWhg.setEnabled( False )
        self._bbeAnzWhg.setMaximumWidth( 40 )
        self._bbeQm.setEnabled( False )
        self._bbeQm.setMaximumWidth( 40 )
        l.addRow( r, ("Anzahl Whg.:", 1), (self._bbeAnzWhg, 1), ("Gesamt-Wfl.(qm):", 3, Qt.AlignRight), (self._bbeQm, 1) )
        # ...Hauswart
        r += 1
        l.addRow( r, ("Hauswart:", 1), (self._beHauswart, 2), ("Telefon:", 2), (self._beHauswartTelefon, 2),
                  ("mailto:", 1), (self._beHauswartMailto, 1) )
        # ...veräußert am
        r += 1
        self._sdVeraeussertAm.setMaximumWidth( 90 )
        l.addRow( r, ("veräußert am:", 1), (self._sdVeraeussertAm, 1) )
        # ...Bemerkung
        r += 1
        self._meBemerkungMaster.setMaximumHeight( 50 )
        l.addWidget( self._meBemerkungMaster, r, 0, 1, self._anzCols )
        l.setColumnStretch( 6, 1 )
        l.setColumnStretch( 7, 1 )
        l.setColumnStretch( 8, 1 )
        return row + 1

    def _createMasterDisplay_( self, row: int, x: XMietobjektExt ) -> int:
        r, c = row, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols, alignment=Qt.AlignCenter )
        ####################### Master-ID
        lbl = LabelArial12( "Master-ID: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._lblMasterId.setText( str( x.master_id ) )
        hbl.addWidget( self._lblMasterId, alignment=Qt.AlignLeft )
        ####################### Dummy
        dummy = FixedWidth20Dummy()
        hbl.addWidget( dummy, alignment=Qt.AlignLeft )
        ###################### Master-Name
        lbl = LabelArial12( "Master-Name: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeMasterName.setTextAndAdjustWidth( x.master_name )
        self._bbeMasterName.setEnabled( False )
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
        r, c = r + 1, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols, alignment=Qt.AlignCenter )
        lbl = LabelArial12( "Anzahl Wohng.: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeAnzWhg.setText( str( x.anz_whg ) )
        self._bbeAnzWhg.setMaximumWidth( 25 )
        self._bbeAnzWhg.setEnabled( False )
        hbl.addWidget( self._bbeAnzWhg, alignment=Qt.AlignLeft )
        ############# Dummy
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        ############  Gesamt-Wohnfläche
        lbl = LabelArial12( "Gesamt-Wohnfläche (qm): " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeGesamtWfl.setText( str( x.gesamt_wfl ) )
        self._bbeGesamtWfl.setMaximumWidth( 45 )
        self._bbeGesamtWfl.setEnabled( False )
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
        r, c = r + 1, 0
        hbl = QHBoxLayout()
        self._layout.addLayout( hbl, r, c, 1, self._anzCols )
        lbl = LabelArial12( "Hauswart: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswart.setText( x.hauswart )
        hbl.addWidget( self._beHauswart, alignment=Qt.AlignLeft )
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        lbl = LabelArial12( "Telefon: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswartTelefon.setText( x.hauswart_telefon )
        hbl.addWidget( self._beHauswartTelefon, alignment=Qt.AlignLeft )
        hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        lbl = LabelArial12( "mailto: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswartMailto.setText( x.hauswart_mailto )
        self._beHauswartMailto.setMinimumWidth( 250 )
        hbl.addWidget( self._beHauswartMailto, alignment=Qt.AlignLeft )

        #################### Bemerkung Master
        r, c = r + 1, 0
        self._meBemerkungMaster.setText( x.bemerkung_masterobjekt )
        self._meBemerkungMaster.setMaximumHeight( 46 )
        self._meBemerkungMaster.setPlaceholderText( "<eBmerkungen zum Master-Objekt>" )
        self._layout.addWidget( self._meBemerkungMaster, r, c, 1, self._anzCols )

        return r

    def _createMietObjektDisplay( self, r: int, x: XMietobjektExt ):
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
        r, c = r + 1, 0
        lbl = BaseLabel( "Mieter: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblMieter.setText( x.mieter )
        self._layout.addWidget( self._lblMieter, r, c, 1, 4 )
        ############################# Telefon + mobil Mieter
        c += 5
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
        c = 11
        btn = EditButton()
        btn.clicked.connect( self.edit_mieter.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        #################### Netto-Miete und NKV
        r, c = r + 1, 0
        lbl = BaseLabel( "Netto-Miete: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblNettoMiete.setText( str( x.nettomiete ) )
        self._layout.addWidget( self._lblNettoMiete, r, c )
        c += 1  # NKV-Label soll linksbündig mit Tel.-Label des Master-Objekts sein
        lbl = BaseLabel( "NKV: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c += 1
        self._lblNkv.setText( str( x.nkv ) )
        self._layout.addWidget( self._lblNkv, r, c )
        c += 3
        lbl = BaseLabel( "Kaution: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblKaution.setText( str( x.kaution ) )
        self._layout.addWidget( self._lblKaution, r, c )
        # ######################### Button Edit Miete
        c = 11
        btn = EditButton()
        btn.clicked.connect( self.edit_miete.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        # #################### Verwalter
        r, c = r + 1, 0
        lbl = BaseLabel( "Verwalter: " )
        self._layout.addWidget( lbl, r, c )
        c += 1
        self._lblVerwalter.setText( x.verwalter )
        self._layout.addWidget( self._lblVerwalter, r, c )
        # #################### WEG-Name
        c += 1
        lbl = BaseLabel( "WEG-Name: " )
        self._layout.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
        c += 1
        self._lblWEG.setText( x.weg_name )
        self._layout.addWidget( self._lblWEG, r, c, 1, 4 )
        # ######################## Button Edit Verwaltung
        c = 11
        btn = EditButton()
        btn.clicked.connect( self.edit_verwaltung.emit )
        self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        # #################### HGV und RüZuFü
        # r, c = r + 1, 0
        # lbl = BaseLabel( "HGV netto: " )
        # self._layout.addWidget( lbl, r, c )
        # c += 1
        # self._lblHgvNetto.setText( str( x.hgv_netto ) )
        # self._layout.addWidget( self._lblHgvNetto, r, c )
        # c += 2
        # lbl = BaseLabel( "RüZuFü: " )
        # self._layout.addWidget( lbl, r, c )
        # c += 1
        # self._lblRueZuFue.setText( str( x.ruezufue ) )
        # self._layout.addWidget( self._lblRueZuFue, r, c )
        # c += 1
        # lbl = BaseLabel( "HGV brutto: " )
        # self._layout.addWidget( lbl, r, c )
        # c += 1
        # self._lblHgvBrutto.setText( str( x.hgv_brutto ) )
        # self._layout.addWidget( self._lblHgvBrutto, r, c )
        # ############################# Button Edit HGV
        # c += 1
        # btn = EditButton()
        # btn.clicked.connect( self.edit_hausgeld.emit )
        # self._layout.addWidget( btn, r, c, 1, 1, alignment=Qt.AlignRight )
        # r += 1
        # self._createDummyRow( r, 10 )
        # #################### qm
        # r, c = r + 1, 0
        # hbl = QHBoxLayout()
        # hbl.addWidget( LabelArial12( "qm: " ), alignment=Qt.AlignLeft )
        # self._bbeQm.setMaximumWidth( 40 )
        # self._bbeQm.setText( str( x.qm ) )
        # self._bbeQm.setEnabled( False )
        # hbl.addWidget( self._bbeQm, alignment=Qt.AlignLeft )
        # #################### Dummy
        # hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        #################### Container-Nr.
        # r += 1
        # c = 0
        # lbl = LabelArial12( "Container-Nr." )
        # self._layout.addWidget( lbl, r, c )
        # hbl.addWidget( LabelArial12( "Container-Nr." ), alignment=Qt.AlignLeft )
        # c += 1
        # self._beContainerNr.setText( x.container_nr )
        # self._layout.addWidget( self._beContainerNr, r, c )
        # hbl.addWidget( self._beContainerNr, alignment=Qt.AlignLeft )
        # self._layout.addLayout( hbl, r, c )
        # ###################### Bemerkung zum Mietobjekt
        # r, c = r + 1, 0
        # self._meBemerkungMobj.setText( x.bemerkung_mietobjekt )
        # self._meBemerkungMobj.setPlaceholderText( "<Bemerkungen zur Wohnung (Mietobjekt)>" )
        # self._meBemerkungMobj.setMaximumHeight( 46 )
        # self._layout.addWidget( self._meBemerkungMobj, r, c, 1, self._anzCols )

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
        self._bbePlz.setText( x.plz )
        self._bbeOrt.setText( x.ort )
        self._bbeAnzWhg.setText( str( x.anz_whg ) )
        self._bbeQm.setText( str( x.qm ) )
        self._beHauswart.setText( x.hauswart )
        self._beHauswartTelefon.setText( x.hauswart_telefon )
        self._beHauswartMailto.setText( x.hauswart_mailto )
        if x.veraeussert_am:
            self._sdVeraeussertAm.setDateFromIsoString( x.veraeussert_am )
        self._meBemerkungMaster.setText( x.bemerkung_masterobjekt )
        # data für Mietobjekt


    def _guiToData( self, x: XMietobjektExt ):
        x.strasse_hnr = self._bbeStrHnr.text()
        x.plz = self._bbePlz.text()
        x.ort = self._bbeOrt.text()
        x.veraeussert_am = self._sdVeraeussertAm.getDate()
        x.hauswart = self._beHauswart.text()
        x.hauswart_telefon = self._beHauswartTelefon.text()
        x.hauswart_mailto = self._beHauswartMailto.text()
        x.whg_bez = self._beWhgBez.text()
        x.container_nr = self._beContainerNr.text()

    def applyChanges( self ):
        self._guiToData( self._mietobjekt )

    def onChange( self ):
        self._btnSave.setEnabled( True )

    def onResetChangeFlag( self ):
        self._btnSave.setEnabled( False )

    def getModel( self ):
        return self._mietobjekt


##################################################################
class MietobjektView( QWidget, ModifyInfo ): # IccView ):
    save = Signal() # speichere Änderungen am Hauswart, der Masterobjekt-Bemerkung,
                            # des Mietobjekt-Containers und der Mietobjekt-Bemerkung
    edit_mieter = Signal()
    edit_miete = Signal()
    edit_verwaltung = Signal()
    edit_hausgeld = Signal()

    def __init__( self, x:XMietobjektExt ):
        QWidget.__init__( self )
        ModifyInfo.__init__( self )
        Clearable.__init__( self )
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
        self.connectWidgetsToChangeSlot( self.onChange, self.onResetChangeFlag )

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
        self._btnSave.setEnabled( False )
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

    def _createMasterDisplay__( self, row: int, x: XMietobjektExt ) -> int:
        l = QFormLayout()
        self._layout.addLayout( l, row, 0 )
        hbl = QHBoxLayout()
        hbl.addWidget( "Master-ID:" )
        l.addRow( "Master-ID:", self._lblMasterId )
        row += 1
        l.addRow( "Master-Name:", self._bbeMasterName )
        row += 1
        return row

    def _createMasterDisplay_( self, row: int, x: XMietobjektExt ) -> int:
        l = GridLayout()
        self._layout.addLayout( l, row, 0 )
        r = 0
        # Master-ID und Master-Name
        hbl = QHBoxLayout()

        l.addRow( )
        #...Anzahl Whgen u. Wohnfläche
        r += 1
        # ...Hauswart
        r += 1
        # ...Bemerkung
        r += 1
        #...veräußert am
        r += 1

        return row + 1

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
        self._bbeMasterName.setEnabled( False )
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
        self._bbeAnzWhg.setEnabled( False )
        hbl.addWidget( self._bbeAnzWhg, alignment= Qt.AlignLeft )
        ############# Dummy
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        ############  Gesamt-Wohnfläche
        lbl = LabelArial12( "Gesamt-Wohnfläche (qm): " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._bbeGesamtWfl.setText( str( x.gesamt_wfl ) )
        self._bbeGesamtWfl.setMaximumWidth( 45 )
        self._bbeGesamtWfl.setEnabled( False )
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
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswart.setText( x.hauswart )
        hbl.addWidget( self._beHauswart, alignment=Qt.AlignLeft )
        lbl = FixedWidth20Dummy()
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        lbl = LabelArial12( "Telefon: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswartTelefon.setText( x.hauswart_telefon )
        hbl.addWidget( self._beHauswartTelefon, alignment=Qt.AlignLeft )
        hbl.addWidget( FixedWidth20Dummy(), alignment=Qt.AlignLeft )
        lbl = LabelArial12( "mailto: " )
        hbl.addWidget( lbl, alignment=Qt.AlignLeft )
        self._beHauswartMailto.setText( x.hauswart_mailto )
        self._beHauswartMailto.setMinimumWidth( 250 )
        hbl.addWidget( self._beHauswartMailto, alignment=Qt.AlignLeft )

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
        self._bbeQm.setMaximumWidth( 40 )
        self._bbeQm.setText( str( x.qm ) )
        self._bbeQm.setEnabled( False )
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
        self._beContainerNr.setText( x.container_nr )
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
        self._guiToData( xcopy )
        return xcopy

    def _guiToData( self, x:XMietobjektExt ):
        x.strasse_hnr = self._bbeStrHnr.text()
        x.plz = self._bbePlz.text()
        x.ort = self._bbeOrt.text()
        x.veraeussert_am = self._sdVeraeussertAm.getDate()
        x.hauswart = self._beHauswart.text()
        x.hauswart_telefon = self._beHauswartTelefon.text()
        x.hauswart_mailto = self._beHauswartMailto.text()
        x.whg_bez = self._beWhgBez.text()
        x.container_nr = self._beContainerNr.text()

    def applyChanges( self ):
        self._guiToData( self._mietobjekt )


    def onChange( self ):
        self._btnSave.setEnabled( True )

    def onResetChangeFlag( self ):
        self._btnSave.setEnabled( False )

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
    x.verwalter = "GfH Häuserkacke"
    x.weg_name = "WEG Beispielstraße 22, 55432 Mühlheim"
    x.hgv_netto = 300.00
    x.ruezufue = 67.89
    x.hgv_brutto = 367.89

    app = QApplication()
    v = MietobjektView_inArbeit( x )
    v.save.connect( onSaveChanges )
    v.edit_verwaltung.connect( onEditVerwaltung )
    v.show()

    app.exec_()


if __name__ == "__main__":
    test()