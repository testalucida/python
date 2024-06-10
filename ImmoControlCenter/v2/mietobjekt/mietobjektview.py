import copy
from typing import Any

from PySide2.QtCore import Signal, QSize
from PySide2.QtGui import Qt, QFont, QPalette
from PySide2.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QApplication, QTextEdit, QFrame

from base.baseqtderivates import FatLabel, BaseBoldEdit, LabelTimesBold12, SmartDateEdit, MultiLineEdit, HLine, \
    LabelTimes12, BaseLabel, EditIconButton, LabelArial12, BaseBoldComboBox, BaseGridLayout, BaseWidget, BaseEdit, \
    BaseComboBox, BaseButton
from generictable_stuff.okcanceldialog import OkDialog, OkCancelDialog
from v2.icc.constants import ValueMapperHelper, Heizung
from v2.icc.iccwidgets import IccTableView
from v2.icc.interfaces import XMietobjektExt, XMasterobjekt, XMieterUndMietobjekt, XMietobjekt, XHausgeld, XMieter

############ TEST TEST TEST TEST  ###########################
def createXMietobjektExt() -> XMietobjektExt:
    x = XMietobjektExt()
    x.master_id = 17
    x.master_name = "NK-Kleist"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Klabautermannstraße 377"
    x.anz_whg = 8
    x.gesamt_wfl = 432
    x.veraeussert_am = "2024-12-01"
    x.heizung = "Gaszentralheizung"
    x.energieeffz = "F"
    x.verwalter = "Hausverwalter Kannundtunix, Neunkirchen"
    x.verwalter_telefon = "06821 / 232333"
    x.verwalter_mailto = "kannundtunix_hausverwaltung@kannundtunix.de"
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
    x.weg_name = "WEG Beispielstraße 22, 55432 Mühlheim"
    x.hgv_netto = 300.00
    x.ruezufue = 67.89
    x.hgv_brutto = 367.89
    return x

def createXMasterObjekt() -> XMasterobjekt:
    x = XMasterobjekt()
    x.master_id = 17
    x.master_name = "NK-Kleist"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Kleiststr. 3"
    x.veraeussert_am = "2023-05-08"
    x.anz_whg = 8
    x.gesamt_wfl = 400
    x.heizung = "Gasetagenheizung"
    x.energieeffz = "F"
    x.verwalter = "GfH Häuserkacke und Versagen garantiert"
    x.verwalter_telefon = "06821 / 22 34 55"
    x.verwalter_mailto = "info@gfh-verwaltung.de"
    x.hauswart = "Herr Falk Mäusegeier"
    x.hauswart_telefon = "0681 / 1 11 33 44"
    x.hauswart_mailto = "falk.maeusegeier@falknerei_saarbruecken.de"
    x.bemerkung = "Sehr schlaue Bemerkung"
    return x

def createXMieter() -> XMieter:
    x = XMieter()
    x.mieter = "Graf von Streusel-Lakaiendorf, Wolf-Eberhard"
    x.telefon = "0171 / 33 44 556"
    x.mailto = "grafstruelakai@t-manchmalonline.de"
    x.nettomiete = 1234.56
    x.nkv = 354.18
    x.bruttomiete = x.nettomiete + x.nkv
    x.kaution = 2500
    return x

# def createXMietobjekt2() -> XMietobjekt2:
#     x = XMietobjekt2()
#     x.mobj_id = "remigius"
#     x.whg_bez = "Whg. 91, 15. OG links"
#     x.qm = 100
#     x.container_nr = "ABX 333 JJF12"
#     x.bemerkung = "Ganz hübsche Wohnung in Homburg"
#     x.hgv_netto = 234.56
#     x.ruezufue = 76.32
#     x.hgv_brutto = x.hgv_netto + x.ruezufue
#     return x

# def createXMieterUndMietobjekt() -> XMieterUndMietobjekt:
#     xmiumio = XMieterUndMietobjekt()
#     xmiumio.mietobjekt = createXMietobjekt2()
#     xmiumio.mieter = createXMieter()
#     return xmiumio

############ TEST ENDE   TEST ENDE   TEST ENDE  ###########################

######################   MietobjektAuswahlView   #############################
class MietobjektAuswahlTableView( IccTableView ):
    """
    Wird im MietobjektAuswahlDialog verwendet
    """
    def __init__( self ):
        IccTableView.__init__( self )
        self.setAlternatingRowColors( True )


#########################  MasterView  ############################
class MasterView( QFrame ):
    show_verwalter = Signal( str )
    #show_hauswart = Signal( str )
    """
    Enthält die Masterobjekt-Daten.
    Besteht aus einer HeaderView im oberen Bereich und einer DataView im unteren Bereich.
    """
    ###########  MasterView.HeaderView  ################
    class HeaderView( QFrame ):
        def __init__( self, master_id: int, master_name: str, strasse_hnr: str, plz: str, ort: str,
                      veraeussert_am: str = "" ):
            QFrame.__init__( self )
            self._master_id = master_id
            self._master_name = master_name
            self._strasse_hnr = strasse_hnr
            self._plz = plz
            self._ort = ort
            self._veraeussert_am = veraeussert_am
            self._layout = BaseGridLayout()
            self.setLayout( self._layout )
            self._mleMasterHeader = MultiLineEdit()
            self._sdeVeraeussertAm = SmartDateEdit()
            self._createGui()
            self._dataToGui()

        def _createGui( self ):
            self.setStyleSheet( "HeaderView { background: lightgray; }" )
            l = self._layout
            e = self._mleMasterHeader
            e.setStyleSheet( "background: lightgray;" )
            e.setReadOnly( True )
            e.setFrameStyle( QFrame.NoFrame )
            e.setMaximumHeight( 70 )
            r, c = 0, 0
            l.addWidget( e, r, c, 1, 2 )
            r += 1
            vam = self._sdeVeraeussertAm
            vam.setStyleSheet( "background: white;" )
            vam.setMaximumWidth( 100 )
            l.addWidget( BaseLabel( "veräußert am: " ), r, c, 1, 1, alignment=Qt.AlignRight )
            c += 1
            l.addWidget( vam, r, c, 1, 1, alignment=Qt.AlignLeft )

        def _dataToGui( self ):
            e = self._mleMasterHeader
            html = 'Master-ID: <font size="+2"><b>' + str( self._master_id ) + '</font></b>' + \
                   '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Master-Name: <font size="+2"><b>' + \
                   self._master_name + '</font></b>'
            e.setHtml( html )
            e.setAlignment( Qt.AlignCenter )
            e.append( " " )
            e.append( "<b>" + self._strasse_hnr + "&nbsp;&nbsp;&nbsp;" + self._plz + "&nbsp;" + self._ort + "</b>" )
            e.setAlignment( Qt.AlignCenter )
            self._sdeVeraeussertAm.setValue( self._veraeussert_am )

        def getVeraeussertAm( self ) -> str:
            return self._sdeVeraeussertAm.getValue()

    ############  MasterView.DataView  ##################
    class DataView( QFrame ):
        show_verwalter = Signal()
        #show_hauswart = Signal()
        def __init__( self, x:XMasterobjekt ):
            QFrame.__init__( self )
            self._x = x
            self._layout = BaseGridLayout()
            self.setLayout( self._layout )
            self._lblAnzWhg = BaseEdit()
            self._lblGesamtWfl = BaseEdit()
            self._cboHeizung = BaseComboBox()
            self._cboHeizung.addItems( ValueMapperHelper.getDisplayValues( Heizung, issorted=False ) )
            self._cboEnergieEffz = BaseComboBox()
            self._cboEnergieEffz.addItems( ("", "A", "B", "C", "D", "E", "F", "G", "H") )
            self._mleVerwalter = MultiLineEdit()
            self._lblVerwalterTelefon = BaseEdit()
            self._lblVerwalterMailto = BaseEdit()
            self._btnVerwalterDetail = BaseButton("🔍")
            self._btnVerwalterDetail.clicked.connect( self.show_verwalter.emit )
            self._lblWegName = BaseEdit()
            self._mleHauswart = MultiLineEdit()
            self._lblHauswartTelefon = BaseEdit()
            self._lblHauswartMailto = BaseEdit()
            #self._btnHauswartDetail = BaseButton( "🔍" )
            #self._btnHauswartDetail.clicked.connect( self.show_hauswart.emit )
            self._mleBemerkung = MultiLineEdit()
            self._createGui()
            self._dataToGui()

        def _createGui( self ):
            l = self._layout
            l.setHorizontalSpacing( 20 )
            anz_cols = 7
            for c in range( 0, anz_cols-1 ):
                l.setColumnStretch( c, 0 )
            l.setColumnStretch( 1, 1 )
            l.setColumnStretch( anz_cols-1, 1 )

            r, c = 0, 0
            ## Anzahl Wohnungen und Gesamt-Wfl.
            l.addWidget( BaseLabel("Anzahl Wohnungen:"), r, c )
            c += 1
            self._lblAnzWhg.setFixedWidth( 50 )
            self._lblAnzWhg.setReadOnly( True )
            self._lblAnzWhg.setStyleSheet( "background: lightgray;" )
            l.addWidget( self._lblAnzWhg, r, c, 1, 1, alignment=Qt.AlignLeft )
            c += 2
            l.addWidget( BaseLabel( "Gesamt-Wfl.(qm):" ), r, c )
            c += 1
            self._lblGesamtWfl.setFixedWidth( 50 )
            self._lblGesamtWfl.setReadOnly( True )
            self._lblGesamtWfl.setStyleSheet( "background: lightgray;" )
            l.addWidget( self._lblGesamtWfl, r, c, 1, 1 )

            r += 1
            c = 0
            ## Heizung und Energie-Effizienzklasse
            l.addWidget( BaseLabel( "Heizung:" ), r, c )
            c += 1
            l.addWidget( self._cboHeizung, r, c, 1, 1 )
            c += 2
            l.addWidget( BaseLabel( "Energieeffz.klasse:" ), r, c )
            c += 1
            self._cboEnergieEffz.setFixedWidth( 50 )
            l.addWidget( self._cboEnergieEffz, r, c, 1, 1 )

            r += 1
            c = 0
            ## Verwalter
            l.addWidget( BaseLabel( "Verwalter:"), r, c )
            c += 1
            self._mleVerwalter.setReadOnly( True )
            self._mleVerwalter.setMaximumHeight( 50 )
            self._mleVerwalter.setStyleSheet( "background: lightgray;" )
            l.addWidget( self._mleVerwalter, r, c, 1, 2 )
            c += 2
            l.addWidget( BaseLabel( "Telefon:" ), r, c )
            c += 1
            l.addWidget( self._lblVerwalterTelefon, r, c )
            c += 1
            l.addWidget( BaseLabel( "mailto:" ), r, c )
            c += 1
            l.addWidget( self._lblVerwalterMailto, r, c, 1, 1 )
            c += 1
            self._btnVerwalterDetail.setFixedSize( QSize( 22, 22 ) )
            self._btnVerwalterDetail.setToolTip( "Details zum Verwalter anzeigen")
            l.addWidget( self._btnVerwalterDetail, r, c, 1, 1 )

            r += 1
            c = 0
            ## WEG-Name
            l.addWidget( BaseLabel( "WEG:" ), r, c )
            c += 1
            self._lblWegName.setReadOnly( True )
            l.addWidget( self._lblWegName, r, c, 1, 4 )

            r += 1
            c = 0
            ## Hauswart
            l.addWidget( BaseLabel( "Hauswart:" ), r, c )
            c += 1
            self._mleHauswart.setMaximumHeight( 50 )
            l.addWidget( self._mleHauswart, r, c, 1, 2 )
            c += 2
            l.addWidget( BaseLabel( "Telefon:" ), r, c )
            c += 1
            l.addWidget( self._lblHauswartTelefon, r, c, 1, 1 )
            c += 1
            l.addWidget( BaseLabel( "mailto:" ), r, c )
            c += 1
            l.addWidget( self._lblHauswartMailto, r, c, 1, 1 )

            r += 1
            c = 0
            ## Bemerkung
            self._mleBemerkung.setMaximumHeight( 60 )
            self._mleBemerkung.setPlaceholderText( "Bemerkungen zum Masterobjekt" )
            l.addWidget( self._mleBemerkung, r, c, 1, anz_cols )

        def _dataToGui( self ):
            x = self._x
            self._lblAnzWhg.setValue( str( x.anz_whg ) )
            self._lblGesamtWfl.setValue( str( x.gesamt_wfl ) )
            items = [self._cboHeizung.itemText(i) for i in range( self._cboHeizung.count() )]
            self._cboHeizung.setValue( x.heizung )

            self._cboEnergieEffz.setValue( x.energieeffz )
            self._mleVerwalter.setValue( x.verwalter )
            self._lblVerwalterTelefon.setValue( x.verwalter_telefon )
            self._lblVerwalterMailto.setValue( x.verwalter_mailto )
            self._lblWegName.setValue( x.weg_name )
            self._mleHauswart.setValue( x.hauswart )
            self._lblHauswartTelefon.setValue( x.hauswart_telefon )
            self._lblHauswartMailto.setValue( x.hauswart_mailto )
            self._mleBemerkung.setValue( x.bemerkung )

        def getChanges( self, xmaster:XMasterobjekt ):
            """
            Schreibt die Änderungen in <xmaster>
            :param xmaster:
            :return:
            """
            xmaster.heizung = self._cboHeizung.currentText()
            xmaster.energieeffz = self._cboEnergieEffz.currentText()
            xmaster.verwalter_telefon = self._lblVerwalterTelefon.getValue()
            xmaster.verwalter_mailto = self._lblVerwalterMailto.getValue()
            xmaster.hauswart = self._mleHauswart.getValue()
            xmaster.hauswart_telefon = self._lblHauswartTelefon.getValue()
            xmaster.hauswart_mailto = self._lblHauswartMailto.getValue()
            xmaster.bemerkung = self._mleBemerkung.getValue()

    #####################################################

    def __init__( self, x:XMasterobjekt ):
        QFrame.__init__( self )
        self._x = x
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._headerView = MasterView.HeaderView( x.master_id, x.master_name, x.strasse_hnr, x.plz, x.ort, x.veraeussert_am )
        self._dataView = MasterView.DataView( x )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        anz_cols = 1
        r, c = 0, 0
        l.addWidget( self._headerView, r, c, 1, anz_cols )
        r += 1
        l.addWidget( self._dataView, r, c, 1, anz_cols )

    def getMasterobjektCopyWithChanges( self ) -> XMasterobjekt:
        xcopy: XMasterobjekt = copy.copy( self._x )
        self._guiToData( xcopy )

    def _guiToData( self, x:XMasterobjekt ):
        x.veraeussert_am = self._headerView.getVeraeussertAm()
        x.heizung =

###########################################################################
def testDataView():
    app = QApplication()
    x = createXMasterObjekt()
    v = MasterView.DataView( x )
    v.show()
    app.exec_()

def testMasterView():
    app = QApplication()
    x = createXMasterObjekt()
    v = MasterView( x )
    v.show()
    sz:QSize = v.size()
    sz.setWidth( 1200 )
    v.resize( sz )
    app.exec_()

######################   MietobjektView  ALT #############################
class MietobjektView_( QWidget ):
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
        #self._bbeHeizung = BaseBoldEdit()
        self._cboHeizung = BaseBoldComboBox()
        self._cboHeizung.addItems( ("", "Gasetagenheizung", "Gaszentralheizung", "Ölzentralheizung", "Nachtspeicher") )
        #self._bbeEnergieEffz = BaseBoldEdit()
        self._cboEnergieEffz = BaseBoldComboBox()
        self._cboEnergieEffz.addItems( ("", "A", "B", "C", "D", "E", "F", "G", "H") )
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
            lbl = BaseLabel( "Gesamt-Wfl.(qm): " )
            l.addWidget( lbl, r, c, 1, 1, alignment=Qt.AlignRight )
            c += 1
            self._bbeGesamtWfl.setEnabled( False )
            self._bbeGesamtWfl.setMaximumWidth( 40 )
            l.addWidget( self._bbeGesamtWfl, r, c )

            r += 1
            c = 0
            l.addWidget( BaseLabel( "Heizung: " ), r, c )
            c += 1
            l.addWidget( self._cboHeizung, r, c, 1, 2 )
            c = 4
            l.addWidget( BaseLabel( "Energieeffz.klasse: " ), r, c )
            c += 1
            l.addWidget( self._cboEnergieEffz, r, c )
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
        if x.heizung:
            self._cboHeizung.setCurrentText( x.heizung )
        if x.energieeffz:
            self._cboEnergieEffz.setCurrentText( x.energieeffz )
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
        x.heizung = self._cboHeizung.currentText()
        x.energieeffz = self._cboEnergieEffz.currentText()
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

##########################  MieterUndMietobjektView  #############################################
class MieterUndMietobjektView( QFrame ):

    ###################  MieterUndMietobjektView.MobjView  ###############################
    class MobjView( QFrame ):
        def __init__(self, xmobj: XMietobjekt, xhg:XHausgeld ):
            QFrame.__init__( self )
            self._xmobj:XMietobjekt = xmobj
            self._xhg:XHausgeld = xhg
            self._mleHeader = MultiLineEdit()
            self._lblQm = BaseEdit()
            self._eContainerNr = BaseEdit()
            self._lblHgvNetto = BaseEdit()
            self._lblRuezufue = BaseEdit()
            self._lblHgvBrutto = BaseEdit()
            self._mleBemerkung = MultiLineEdit()
            self._layout = BaseGridLayout()
            self.setLayout( self._layout )
            self._createGui()
            self._dataToGui()

        def _createGui( self ):
            wBetrag = 60
            l = self._layout
            l.setHorizontalSpacing( 25 )
            anz_cols = 7
            for c in range( 0, anz_cols-1 ):
                l.setColumnStretch( c, 0 )
            l.setColumnStretch( anz_cols-1, 1 )
            e = self._mleHeader
            e.setStyleSheet( "background: lightgray;" )
            e.setReadOnly( True )
            e.setFrameStyle( QFrame.NoFrame )
            e.setMaximumHeight( 40 )
            r, c = 0, 0
            l.addWidget( e, r, c, 1, anz_cols )

            r += 1
            c = 0
            l.addWidget( BaseLabel( "qm:"), r, c )
            c += 1
            self._lblQm.setFixedWidth( wBetrag )
            self._lblQm.setReadOnly( True )
            l.addWidget( self._lblQm, r, c )
            c += 1
            l.addWidget( BaseLabel( "Container-Nr.:" ), r, c )
            c += 1
            l.addWidget( self._eContainerNr, r, c )

            r += 1
            c = 0
            l.addWidget( BaseLabel( "HGV netto:" ), r, c, 1, 1 )
            c += 1
            self._lblHgvNetto.setFixedWidth( wBetrag )
            self._lblHgvNetto.setReadOnly( True )
            l.addWidget( self._lblHgvNetto, r, c, 1, 1, alignment=Qt.AlignLeft )
            c += 1
            l.addWidget( BaseLabel( "RüZuFü:"), r, c, 1, 1 )
            c += 1
            self._lblRuezufue.setFixedWidth( wBetrag )
            self._lblRuezufue.setReadOnly( True )
            l.addWidget( self._lblRuezufue, r, c, 1, 1, alignment=Qt.AlignLeft )
            c += 1
            l.addWidget( BaseLabel( "HGV brutto:" ), r, c, 1, 1 )
            c += 1
            self._lblHgvBrutto.setFixedWidth( wBetrag )
            self._lblHgvBrutto.setReadOnly( True )
            l.addWidget( self._lblHgvBrutto, r, c, 1, 1, alignment=Qt.AlignLeft )

            r += 1
            c = 0
            self._mleBemerkung.setPlaceholderText( "Bemerkungen zum Mietobjekt" )
            self._mleBemerkung.setMaximumHeight( 60 )
            l.addWidget( self._mleBemerkung, r, c, 1, anz_cols )

        def _dataToGui( self ):
            x = self._xmobj
            e = self._mleHeader
            html = 'Mietobjekt: <font size="+2"><b>' + x.mobj_id + '</font></b>' + \
                   '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Bezeichnung: <font size="+2"><b>' + \
                   x.whg_bez + '</font></b>'
            e.setHtml( html )
            e.setAlignment( Qt.AlignCenter )
            self._lblQm.setValue( str(x.qm) )
            self._eContainerNr.setValue( x.container_nr )
            self._mleBemerkung.setValue( x.bemerkung )
            xhg = self._xhg
            self._lblHgvNetto.setValue( "%.2f" % xhg.hgv_netto )
            self._lblRuezufue.setValue( "%.2f" % xhg.ruezufue )
            self._lblHgvBrutto.setValue( "%.2f" % xhg.hgv_brutto )


    #####################  MieterUndMietobjektView.MieterView  ####################################
    class MieterView( QFrame ):
        def __init__(self, x:XMieter):
            QFrame.__init__( self )
            self._xmieter = x
            self._layout = BaseGridLayout()
            self.setLayout( self._layout )
            #self._mleHeader = MultiLineEdit()
            self._mleHeader = MultiLineEdit()
            self._eTelefon = BaseEdit()
            self._eMailto = BaseEdit()
            self._lblNettoMiete = BaseEdit()
            self._lblNkv = BaseEdit()
            self._lblBruttoMiete = BaseEdit()
            self._lblKaution = BaseEdit()
            self._mleBemerkung1 = MultiLineEdit()
            self._mleBemerkung2 = MultiLineEdit()
            self._createGui()
            self._dataToGui()

        def _createGui( self ):
            wBetrag = 60
            l = self._layout
            l.setHorizontalSpacing( 20 )
            anz_cols = 10
            for c in range( 0, anz_cols - 1 ):
                l.setColumnStretch( c, 0 )
            l.setColumnStretch( anz_cols - 1, 1 )

            r, c = 0, 0
            self._mleHeader.setReadOnly( True )
            self._mleHeader.setFrameStyle( QFrame.NoFrame )
            self._mleHeader.setStyleSheet( "background: lightgray;" )
            self._mleHeader.setFixedHeight( 40 )
            l.addWidget( self._mleHeader, r, c, 1, anz_cols )

            r += 1
            c = 0
            l.addWidget( BaseLabel("Telefon:"), r, c )
            c += 1
            self._eTelefon.setFixedWidth( 150 )
            l.addWidget( self._eTelefon, r, c, 1, 2 )
            c += 2
            l.addWidget( BaseLabel( "mailto:" ), r, c )
            c += 1
            self._eMailto.setFixedWidth( 260 )
            l.addWidget( self._eMailto, r, c, 1, 3 )


            r += 1
            c = 0
            l.addWidget( BaseLabel("Netto-Miete:"), r, c )
            c += 1
            self._lblNettoMiete.setReadOnly( True )
            self._lblNettoMiete.setFixedWidth( wBetrag )
            l.addWidget( self._lblNettoMiete, r, c )
            c += 2
            l.addWidget( BaseLabel( "NKV:" ), r, c )
            c += 1
            self._lblNkv.setReadOnly( True )
            self._lblNkv.setFixedWidth( wBetrag )
            l.addWidget( self._lblNkv, r, c )
            c += 1
            l.addWidget( BaseLabel( "Brutto-Miete:" ), r, c )
            c += 1
            self._lblBruttoMiete.setReadOnly( True )
            self._lblBruttoMiete.setFixedWidth( wBetrag )
            l.addWidget( self._lblBruttoMiete, r, c )
            c += 1
            l.addWidget( BaseLabel( "Kaution:" ), r, c )
            c += 1
            self._lblKaution.setFixedWidth( wBetrag )
            self._lblKaution.setReadOnly( True )
            l.addWidget( self._lblKaution, r, c )

            r += 1
            c = 0
            self._mleBemerkung1.setMaximumHeight( 80 )
            self._mleBemerkung1.setPlaceholderText( "Bemerkungen zum Mieter" )
            l.addWidget( self._mleBemerkung1, r, c, 1, 5 )
            c += 5
            self._mleBemerkung2.setMaximumHeight( 80 )
            self._mleBemerkung2.setPlaceholderText( "Weitere Bemerkungen zum Mieter" )
            l.addWidget( self._mleBemerkung2, r, c, 1, 5 )

        def _dataToGui( self ):
            x = self._xmieter
            e = self._mleHeader
            html = 'Mieter: <font size="+2"><b>' + x.mieter + '</font></b>'
            e.setHtml( html )
            e.setAlignment( Qt.AlignCenter )
            self._eTelefon.setValue( x.telefon )
            self._eMailto.setValue( x.mailto )
            self._lblNettoMiete.setValue( "%.2f" % x.nettomiete )
            self._lblNkv.setValue( "%.2f" % x.nkv )
            self._lblBruttoMiete.setValue( "%.2f" % x.bruttomiete )
            self._lblKaution.setValue( str( x.kaution ) )
            self._mleBemerkung1.setValue( x.bemerkung1 )
            self._mleBemerkung2.setValue( x.bemerkung2 )

    #################################################
    def __init__( self, xmiumo:XMieterUndMietobjekt ):
        QFrame.__init__( self )
        self._xmiumo = xmiumo
        #self._mleHeader = MultiLineEdit()
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mobjView = MieterUndMietobjektView.MobjView( xmiumo.mietobjekt, xmiumo.hausgeld )
        self._mieterView = MieterUndMietobjektView.MieterView( xmiumo.mieter )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        l.setHorizontalSpacing( 25 )

        r, c = 0, 0
        l.addWidget( self._mobjView, r, c )
        r += 1
        l.addWidget( self._mieterView, r, c )


##############################################################
def testMieterUndMietobjektView():
    app = QApplication()
    #x = createXMieterUndMietobjekt()
    #v = MieterUndMietobjektView( x )
    #v.show()
    app.exec_()

def testMieterView():
    app = QApplication()
    x = createXMieter()
    v = MieterUndMietobjektView.MieterView( x )
    v.show()
    app.exec_()

def testMobjView():
    app = QApplication()
    xmo = XMietobjekt()
    xmo.mobj_id = "remigius"
    xmo.whg_bez = "Whg 7, Haus A, 2. OG li"
    xmo.qm = 100
    xmo.container_nr = "A123 B16"
    xmo.bemerkung = "Braucht unbedingt eine neue Wohnungstür"
    xhg = XHausgeld()
    xhg.hgv_netto = 312.90
    xhg.ruezufue = 77.50
    xhg.hgv_brutto = xhg.hgv_netto + xhg.ruezufue

    v = MieterUndMietobjektView.MobjView( xmo, xhg )
    v.show()
    app.exec_()

########   MietobjektView  ####################################
class MietobjektView( QFrame ):
    def __init__( self, x: XMietobjektExt ):
        QFrame.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mietobjExt = x
        self._masterView = MasterView( self._createXMasterobjekt() )
        self._mieterUndMietobjView = MieterUndMietobjektView( self._createXMieterUndMietobjekt() )
        self._createGui()

    def _createXMasterobjekt( self ) -> XMasterobjekt:
        ext = self._mietobjExt
        x = XMasterobjekt()
        x.master_id = ext.master_id
        x.master_name = ext.master_name
        x.strasse_hnr = ext.strasse_hnr
        x.plz = ext.plz
        x.ort = ext.ort
        x.gesamt_wfl = ext.gesamt_wfl
        x.anz_whg = ext.anz_whg
        x.verwalter = ext.verwalter
        x.verwalter_telefon = ext.verwalter_telefon
        x.verwalter_mailto = ext.verwalter_mailto
        x.weg_name = ext.weg_name
        x.hauswart = ext.hauswart
        x.hauswart_telefon = ext.hauswart_telefon
        x.hauswart_mailto = ext.hauswart_mailto
        x.veraeussert_am = ext.veraeussert_am
        x.heizung = ext.heizung
        x.energieeffz = ext.energieeffz
        x.bemerkung = ext.bemerkung_masterobjekt
        return x

    def _createXMieterUndMietobjekt( self ) -> XMieterUndMietobjekt:
        x = self._mietobjExt
        xmum = XMieterUndMietobjekt()
        xmo:XMietobjekt = xmum.mietobjekt
        xmo.mobj_id = x.mobj_id
        xmo.whg_bze = x.whg_bez
        xmo.qm = x.qm
        xmo.container_nr = x.container_nr
        xmo.bemerkung = x.bemerkung_mietobjekt
        xmi:XMieter = xmum.mieter
        xmi.mieter = x.mieter
        xmi.telefon = x.telefon_mieter
        xmi.mailto = x.mailto_mieter
        xmi.nettomiete = x.nettomiete
        xmi.nkv = x.nkv
        xmi.bruttomiete = xmi.nettomiete + xmi.nkv
        xmi.kaution = x.kaution
        xmi.bemerkung1 = x.bemerkung1_mieter
        xmi.bemerkung2 = x.bemerkung2_mieter
        xhg:XHausgeld = xmum.hausgeld
        xhg.hgv_netto = x.hgv_netto
        xhg.ruezufue = x.ruezufue
        xhg.hgv_brutto = x.hgv_brutto
        return xmum

    def _createGui( self ):
        l = self._layout
        l.setVerticalSpacing( 15 )

        r, c = 0, 0
        l.addWidget( self._masterView, r, c )

        r += 1
        l.addWidget( self._mieterUndMietobjView, r, c )

    def getMietobjektCopyWithChanges( self ) -> XMietobjektExt:
        xcopy: XMietobjektExt = copy.copy( self._mietobjekt )
        self._guiToData( xcopy )
        return xcopy

    def applyChanges( self ):
        self._guiToData( self._mietobjExt )

    def getModel( self ):
        return self._mietobjExt

    @staticmethod
    def getPreferredWidth() -> int:
        return 1350

    @staticmethod
    def getPreferredSize() -> QSize:
        return QSize( MietobjektView.getPreferredWidth(), 786 )

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

def testMietobjektNeu():
    app = QApplication()
    x = createXMietobjektExt()
    v = MietobjektView( x )
    v.show()
    # sz:QSize = v.size()
    # print( sz.width(), " ", sz.height() )
    # sz.setWidth(1350)
    v.resize( v.getPreferredSize() )
    app.exec_()

def testHeader2():
    app = QApplication()
    w = BaseWidget()
    w.setStyleSheet( "background: lightgray;" )
    l = QGridLayout()
    w.setLayout( l )
    e = QTextEdit()
    e.setReadOnly( True )
    e.setFrameStyle( QFrame.NoFrame )
    l.addWidget( e, 0, 0, 1, 1 )
    id = "17"
    stra = "Kleiststr. 2"
    html = 'Master-ID: <font size="+2"><b>' + id + '</font></b>' + \
           '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Master-Name: <font size="+2"><b>' + stra + '</font></b>'
    e.setHtml( html )
    e.setAlignment( Qt.AlignCenter )
    e.append( " " )
    e.append( "Kaiserstr. 252, <b>Saarbrücken</b>" )
    e.setAlignment( Qt.AlignCenter )
    w.show()
    app.exec_()


def test():
    def validate() -> bool:
        print( "validate")
        print( "mobj_id: ", x.mobj_id )
        return True

    x = createXMietobjektExt()
    app = QApplication()
    v = MietobjektView( x )
    # v.save.connect( onSaveChanges )
    # v.show()
    dlg = MietobjektDialog( v, x.mobj_id )
    dlg.setBeforeAcceptFunction( validate )
    # dlg.exec_()
    dlg.show()
    app.exec_()

def testBackground():
    app = QApplication()
    v = QWidget()
    l = BaseGridLayout()
    v.setLayout( l )

    w = QWidget()
    hbl = QHBoxLayout()
    w.setLayout( hbl )
    w.setStyleSheet( "background: green;" )
    lbl = BaseLabel( "Ich bin ein Label" )
    hbl.addWidget( lbl, alignment=Qt.AlignLeft )
    lbl2 = FatLabel( "123" )
    hbl.addWidget( lbl2, alignment=Qt.AlignLeft )

    l.addWidget( w, 0, 0 )

    v.show()
    app.exec_()

def testHeader():
    app = QApplication()

    x = XMietobjektExt()
    x.master_id = 17
    x.master_name = "NK-Kleist"
    x.plz = "66538"
    x.ort = "Neunkirchen"
    x.strasse_hnr = "Klabautermannstraße 377"

    w = QWidget()
    l = BaseGridLayout()
    w.setLayout( l )
    mle = MultiLineEdit()
    mle.setReadOnly( True )
    mle.setStyleSheet( "background: green;" )
    txt = "Master-ID: " + str(x.master_id) + "\t" + "Master-Name: " + x.master_name
    mle.append( txt )
    mle.setAlignment( Qt.AlignCenter )
    mle.append( " " )
    txt = x.strasse_hnr + ", " + x.plz + " " + x.ort
    mle.append( txt )
    mle.setAlignment( Qt.AlignCenter )
    l.addWidget( mle, 0, 0, 1, 1 )  #, alignment=Qt.AlignCenter )

    mle2 = MultiLineEdit()
    html = "<html>Eine <b>Testzeile</b></html>"
    mle2.setHtml( html )
    mle2.setAlignment( Qt.AlignCenter )
    l.addWidget( mle2, 1, 0, 1, 1 )
    w.show()

    app.exec_()

