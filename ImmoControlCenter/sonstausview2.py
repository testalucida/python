from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSize, Qt, QDate, QPoint
from PySide2.QtGui import QIcon, QDoubleValidator, QFont, QIntValidator
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit, QCheckBox, QPushButton, QCalendarWidget, \
    QVBoxLayout, QDialog, QBoxLayout, QHBoxLayout, QTextEdit, QSpinBox, QLabel, QTableView, QMessageBox, \
    QAbstractItemView
from typing import List

from icctablemodel import IccTableModel
from interfaces import XSonstAus, XSonstAusSummen
from qtderivates import IntDisplay, SmartDateEdit, FloatEdit
from sonstaustablemodel import SonstAusTableModel
from tableviewext import TableViewExt
from datehelper import *

#######################  EditableCombo ###########################
class EditableCombo( QComboBox ):
    def __init__( self, parent=None ):
        QComboBox.__init__( self, parent )
        self.setEditable( True )

#########################  SonstigeAusgabenView  ##############################
class SonstigeAusgabenView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        #self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._summenLayout = QHBoxLayout()
        self._btnSave = QPushButton( self )
        self._editSearch = QLineEdit( self )
        self._btnSearchFwd = QPushButton( self )
        self._btnDbSearch = QPushButton( self )

        # self._idSummeAus = IntDisplay( self )
        # self._idSummeW = IntDisplay( self )
        # self._idSummeU = IntDisplay( self )
        # self._summenfont = QFont( "Times New Roman", 16, weight=QFont.Bold )
        # self._summenartfont = QFont( "Times New Roman", 9 )

        self._cboBuchungsjahr = QtWidgets.QComboBox( self )
        self._tvAuszahlungen = TableViewExt( self )

        self._buchungsdatumLayout = QHBoxLayout()
        self._sdBuchungsdatum = SmartDateEdit( self )
        self._btnAddDay = QPushButton( self )
        self._btnClearBuchungsdatum = QPushButton( self )

        self._objektRefLayout = QHBoxLayout()
        self._cboMasterobjekt = QComboBox( self )
        self._cboMietobjekt = QComboBox( self )

        self._editRechnungLineLayout = QHBoxLayout()
        self._cboKreditor = EditableCombo( self )
        self._cboBuchungstext = EditableCombo( self )
        self._sdRechnungsdatum = SmartDateEdit( self )
        self._feBetrag = FloatEdit( self )
        self._cboKostenart = QComboBox( self )
        self._cbUmlegbar = QCheckBox( self )
        self._cbWerterhaltend = QCheckBox( self )
        self._teBemerkung = QTextEdit( self )
        self._btnOk = QPushButton( self )
        self._btnClear = QPushButton( self )
        # actions für ContextMenu
        #self._contextMenuActions:List[QAction] = None
        # Callbacks
        self._buchungsjahrChangedCallback = None
        self._saveActionCallback = None
        self._searchActionCallback = None
        self._dbSearchActionCallback = None
        self._masterobjektChangedCallback = None
        self._mietobjektChangedCallback = None
        self._kreditorChangedCallback = None
        self._submitChangesCallback = None
        self._justEditing:XSonstAus = None
        self._suspendCallbacks = False

        self._createGui()

    def _createGui( self ):
        self._assembleToolbar()
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        #self._assembleSummen()
        # self._toolbarLayout.addStretch( 50 )
        # self._toolbarLayout.addLayout( self._summenLayout )
        ### tableView
        tv = self._tvAuszahlungen
        tv.setSelectionBehavior( QAbstractItemView.SelectRows )
        tv.setAlternatingRowColors( True )
        tv.verticalHeader().setVisible( False )
        tv.horizontalHeader().setMinimumSectionSize( 0 )
        self._mainLayout.addWidget( tv, 1, 0, 1, 1 )
        self._assembleBuchungsUndRechnungsdatum()
        self._mainLayout.addLayout( self._buchungsdatumLayout, 2, 0, alignment=Qt.AlignLeft )
        self._assembleObjektReference()
        self._mainLayout.addLayout( self._objektRefLayout, 3, 0, alignment=Qt.AlignLeft )
        self._assembleRechnungsdaten()
        self._mainLayout.addLayout( self._editRechnungLineLayout, 4, 0, alignment=Qt.AlignLeft )

    def _assembleToolbar( self ):
        #### Combobox Buchungsjahr
        font = QFont( "Arial", 14, weight=QFont.Bold )
        self._cboBuchungsjahr.setFont( font )
        self._cboBuchungsjahr.setToolTip(
            "Das hier eingestellte Jahr bestimmt die Rechnungen, die in der Tabelle angezeigt werden." )
        self._cboBuchungsjahr.currentIndexChanged.connect( self.onBuchungsjahrChanged )
        self._toolbarLayout.addWidget( self._cboBuchungsjahr, stretch=0, alignment=Qt.AlignLeft )

        #### save button
        btn = self._btnSave
        btn.clicked.connect( self.onSave )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen dieser View speichern" )
        icon = QIcon( "./images/save_30.png" )
        btn.setIcon( icon )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        self._toolbarLayout.addWidget( btn, stretch=0 )

        ### search field for tableview search
        edi = self._editSearch
        edi.setPlaceholderText( "Suche in Tabelle" )
        edi.returnPressed.connect( self._onSearch )
        edi.setToolTip( "Suchbegriff eingeben" )
        self._toolbarLayout.addWidget( edi, stretch=0 )
        btn = self._btnSearchFwd
        btn.clicked.connect( self._onSearch )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        btn.setToolTip( "Suche nach eingegebenem Begriff" )
        icon = QIcon( "./images/arrow_dn_30.png" )
        btn.setIcon( icon )
        btn.setEnabled( True )
        self._toolbarLayout.addWidget( btn, stretch=0 )

    def _assembleBuchungsUndRechnungsdatum( self ):
        lbl = QLabel( self, text="Buchungsdatum: " )
        lbl.setFixedWidth( 150 )
        self._buchungsdatumLayout.addWidget( lbl )
        self._sdBuchungsdatum.setFixedWidth( 85 )
        self._sdBuchungsdatum.setToolTip( "Buchungsdatum. Kann leer bleiben, wenn Buchung noch nicht erfolgt ist" )
        self._buchungsdatumLayout.addWidget( self._sdBuchungsdatum )
        size = QSize( 25, 25 )
        self._btnAddDay.setIcon( QIcon( "./images/plus.png" ) )
        self._btnAddDay.setFixedSize( size )
        self._btnAddDay.setToolTip( "Buchungsdatum um 1 Tag erhöhen" )
        self._btnAddDay.clicked.connect( self.onAddDayToBuchungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnAddDay )
        self._btnClearBuchungsdatum.setIcon( QIcon( "./images/cancel.png" ) )
        self._btnClearBuchungsdatum.setFixedSize( size )
        self._btnClearBuchungsdatum.setToolTip( "Buchungsdatum löschen" )
        self._btnClearBuchungsdatum.clicked.connect( self.onClearBuchungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnClearBuchungsdatum )

        self._sdRechnungsdatum.setPlaceholderText( "Datum Rg." )
        self._sdRechnungsdatum.setMaximumWidth( 85 )
        self._sdRechnungsdatum.setToolTip( "optional: Datum der Rechnung" )
        self._buchungsdatumLayout.addSpacing( 10 )
        lbl = QLabel( text="Rechnungsdatum (optional): " )
        lbl.setFixedWidth( 200 )
        self._buchungsdatumLayout.addWidget( lbl )
        self._buchungsdatumLayout.addWidget( self._sdRechnungsdatum )

    def _assembleObjektReference( self ):
        lbl = QLabel( self, text="Betroffenes Objekt: " )
        lbl.setFixedWidth( 150 )
        self._objektRefLayout.addWidget( lbl )
        self._cboMasterobjekt.setFixedWidth( 155 )
        self._cboMasterobjekt.setPlaceholderText( "Haus" )
        self._cboMasterobjekt.setToolTip( "Haus, auf das sich die Zahlung bezieht" )
        self._cboMasterobjekt.currentIndexChanged.connect( self.onMasterobjektChanged )
        self._objektRefLayout.addWidget( self._cboMasterobjekt )
        self._cboMietobjekt.setPlaceholderText( "Wohnung" )
        self._cboMietobjekt.setToolTip( "optional: Wohnung, auf die sich die Zahlung bezieht" )
        self._cboMietobjekt.currentIndexChanged.connect( self.onMietobjektChanged )
        self._objektRefLayout.addWidget( self._cboMietobjekt )

    def _assembleRechnungsdaten( self ):
        self._cboKreditor.setToolTip( "Kreditor" )
        self._cboKreditor.setFixedWidth( 200 )
        self._cboKreditor.currentIndexChanged.connect( self.onKreditorChanged )
        self._editRechnungLineLayout.addWidget( self._cboKreditor )
        self._cboBuchungstext.setToolTip( "Identifikation der Zahlung durch Rechnungsnummer oder Buchungstext" )
        self._cboBuchungstext.setMinimumWidth( 100 )
        self._editRechnungLineLayout.addWidget( self._cboBuchungstext, stretch=2 )

        #Button for DB-Search
        btn = self._btnDbSearch
        btn.clicked.connect( self._onDbSearch )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        btn.setToolTip( "Suche Buchungstext in der DB" )
        icon = QIcon( "./images/search_30.png" )
        btn.setIcon( icon )
        btn.setEnabled( True )
        self._editRechnungLineLayout.addWidget( btn )

        # self._sdRechnungsdatum.setPlaceholderText( "Datum Rg." )
        # self._sdRechnungsdatum.setMaximumWidth( 85 )
        # self._sdRechnungsdatum.setToolTip( "optional: Datum der Rechnung" )
        # self._editRechnungLineLayout.addWidget( self._sdRechnungsdatum, stretch=0, alignment=Qt.AlignLeft )
        self._feBetrag.setPlaceholderText( "Betrag" )
        self._feBetrag.setMaximumWidth( 70 )
        self._feBetrag.setToolTip( "Positive Beträge sind Aus-, negative Einzahlungen (Gutschriften)" )
        self._editRechnungLineLayout.addWidget( self._feBetrag, stretch=0, alignment=Qt.AlignLeft )

        # Combobox Kostenart
        self._cboKostenart.setPlaceholderText( "Kostenart" )
        self._cboKostenart.setFixedWidth( 70 )
        self._cboKostenart.setToolTip( "Kostenart einstellen" )
        self._editRechnungLineLayout.addWidget( self._cboKostenart, stretch=0, alignment=Qt.AlignLeft )

        vbox = QVBoxLayout()
        vbox.setSpacing( 0 )
        self._cbUmlegbar.setText( "uml" )
        self._cbUmlegbar.setToolTip( "Ob die Auszahlung auf den/die Mieter umlegbar sind" )
        vbox.addWidget( self._cbUmlegbar )
        self._cbWerterhaltend.setText( "wert" )
        self._cbWerterhaltend.setToolTip( "Ob die Auszahlung der Werterhaltung der Wohnung dient" )
        vbox.addWidget( self._cbWerterhaltend )
        self._editRechnungLineLayout.addLayout( vbox )

        self._teBemerkung.setPlaceholderText( "Bemerkung zur Auszahlung" )
        self._teBemerkung.setMaximumSize( QtCore.QSize( 16777215, 50 ) )
        self._editRechnungLineLayout.addWidget( self._teBemerkung, stretch=1 )

        vbox = QVBoxLayout()
        self._btnOk.setIcon( QIcon( "./images/checked.png" ) )
        self._btnOk.setDefault( True )
        self._btnOk.setToolTip( "Neue oder geänderte Daten in Tabelle übernehmen (kein Speichern)" )
        self._btnOk.clicked.connect( self.onOkEditFields )
        vbox.addWidget( self._btnOk )
        self._btnClear.setIcon( QIcon( "./images/cancel.png" ) )
        self._btnClear.setToolTip( "Änderungen verwerfen und Felder leeren" )
        self._btnClear.clicked.connect( self.onClearEditFields )
        vbox.addWidget( self._btnClear )
        self._editRechnungLineLayout.addLayout( vbox )

    # def setContextMenuActions( self, actions:List[QAction] ) -> None:
    #     self._contextMenuActions = actions

    def getSummen( self ) -> XSonstAusSummen:
        summen = XSonstAusSummen()
        summen.summe_aus = self._idSummeAus.getIntValue()
        summen.summe_werterhaltend = self._idSummeW.getIntValue()
        summen.summe_umlegbar = self._idSummeU.getIntValue()
        return summen

    def onAddDayToBuchungsdatum( self ):
        val = self._sdBuchungsdatum.getDate()
        if val:
            dt = getQDateFromIsoString( val )
            dt = dt.addDays( 1 )
            self._sdBuchungsdatum.setDate( dt.year(), dt.month(), dt.day() )

    def onClearBuchungsdatum( self ):
        self._sdBuchungsdatum.clear()

    def setSaveButtonEnabled( self, enable:bool=True ):
        self._btnSave.setEnabled( enable )

    def onSave( self ):
        if self._saveActionCallback:
            self._saveActionCallback()

    def _onSearch( self ):
        if self._searchActionCallback:
            self._searchActionCallback( self._editSearch.text() )

    def _onDbSearch( self ):
        if self._dbSearchActionCallback:
            #self._dbSearchActionCallback( self._editDbSearch.text() )
            searchstring = self._cboBuchungstext.currentText()
            if searchstring:
                self._dbSearchActionCallback( searchstring )

    def onBuchungsjahrChanged( self, newindex ):
        """
        Slot für die Änderung des Buchungsjahrs.
        :param newindex:
        :return:
        """
        if self._buchungsjahrChangedCallback:
            jahr = int( self._cboBuchungsjahr.currentText() )
            self._buchungsjahrChangedCallback( jahr )

    def onMasterobjektChanged( self, newindex:int ):
        if self._masterobjektChangedCallback and not self._suspendCallbacks:
            self._masterobjektChangedCallback( self._cboMasterobjekt.currentText() )

    def onMietobjektChanged( self, newindex:int ):
        pass

    def onKreditorChanged( self, newindex:int ):
        if self._kreditorChangedCallback and not self._suspendCallbacks:
            self._kreditorChangedCallback( self._cboMasterobjekt.currentText(),
                                           self._cboMietobjekt.currentText(),
                                           self._cboKreditor.currentText() )

    def onOkEditFields( self, arg ):
        """
        OK gedrückt. Änderungen an Callback-Funktion melden.
        :param arg:
        :return:
        """
        if self._submitChangesCallback:
            x:XSonstAus = self._getEditedXSonstAus()
            ok:bool = self._submitChangesCallback( x )
            if ok:
                self._tvAuszahlungen.clearSelection()
                if x.saus_id <= 0: # neuer Eintrag in Tabelle, nach unten scrollen
                    self._tvAuszahlungen.scrollToBottom()

    def _getEditedXSonstAus( self ) -> XSonstAus:
        x:XSonstAus = self._justEditing if self._justEditing else XSonstAus()
        x.buchungsjahr = int( self._cboBuchungsjahr.currentText() )
        x.buchungsdatum = self._sdBuchungsdatum.getDate()
        idx = self._cboMasterobjekt.currentIndex()
        x.master_name = "" if idx < 0 else self._cboMasterobjekt.currentText()
        idx = self._cboMietobjekt.currentIndex()
        x.mobj_id = "" if idx < 0 else self._cboMietobjekt.currentText()
        x.kreditor = self._cboKreditor.currentText()
        x.buchungstext = self._cboBuchungstext.currentText()
        x.rgdatum = self._sdRechnungsdatum.getDate()
        x.betrag = self._feBetrag.getFloatValue() * (-1)
        x.umlegbar = self._cbUmlegbar.isChecked()
        x.werterhaltend = self._cbWerterhaltend.isChecked()
        x.rgtext = self._teBemerkung.toPlainText()
        return x

    def onClearEditFields( self, arg ):
        self.clearEditFields()
        self._tvAuszahlungen.clearSelection()

    def getAuszahlungenTableView( self ) -> QTableView:
        return self._tvAuszahlungen

    def setAuszahlungenTableModel( self, tm:SonstAusTableModel ):
        self._tvAuszahlungen.setModel( tm )
        self._tvAuszahlungen.resizeColumnsToContents()
        #self._tvAuszahlungen.setColumnWidth( 0, 10 )
        #self._tvAuszahlungen.setColumnWidth( 1, 10 )

    def setBuchungsjahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr-Combobox
        :param jahre:
        :return:
        """
        for jahr in jahre:
            self._cboBuchungsjahr.addItem( str( jahr ) )

    def setBuchungsjahr( self, jahr:int ) -> None:
        """
        setzt das Jahr, das in der Buchungsjahr-Combobox anzuzeigen ist
        :param jahr:
        :return:
        """
        self._cboBuchungsjahr.setCurrentText( str( jahr ) )

    def setBuchungsdatum( self, tag:int, monat:str ):
        """
        setzt Buchungstag und -monat.
        Das Jahr ergibt sich aus dem eingestellten Buchungsjahr
        :param tag:
        :param monat:
        :return:
        """
        # self._sbTag.setValue( tag )
        # self._cboMonat.setCurrentText( monat )
        self._sdBuchungsdatum.\
            setDate( int(self._cboBuchungsjahr.currentText()), getMonthIndex( monat ), tag )

    def setMasterobjekte( self, masterobjekte:List[str] ):
        for obj in masterobjekte:
            self._cboMasterobjekt.addItem( obj )

    def setMietobjekte( self, mietobjekte:List[str] ):
        self._cboMietobjekt.clear()
        for obj in mietobjekte:
            self._cboMietobjekt.addItem( obj )
        self._cboMietobjekt.setCurrentIndex( 0 )

    def selectMietobjekt( self, mobj_id:str ):
        self._cboMietobjekt.setCurrentText( mobj_id )

    def clearMietobjekte( self ):
        self._cboMietobjekt.clear()

    def setKreditoren( self, kreditoren:List[str] ):
        self._cboKreditor.clear()
        for k in kreditoren:
            self._cboKreditor.addItem( k )
        self._cboKreditor.setCurrentIndex( -1 )

    def selectKreditor( self, kreditor:str ):
        self._cboKreditor.setCurrentText( kreditor )

    def setLeistungsidentifikationen( self, idents:List[str] ):
        self._cboBuchungstext.clear()
        for i in idents:
            self._cboBuchungstext.addItem( i )
        #self._cboRechnungsIdent.showPopup()

    def setCurrentLeistungsidentifikation( self, leistident:str ) -> None:
        self._cboBuchungstext.setCurrentText( leistident )

    def getCurrentMasterobjekt( self ) -> str:
        return self._cboMasterobjekt.currentText()

    def getCurrentMietobjekt( self ) -> str:
        return self._cboMietobjekt.currentText()

    def getCurrentKreditor( self ) -> str:
        return self._cboKreditor.currentText()

    def setCurrentKreditor( self, kreditor:str ) -> None:
        self._cboKreditor.setCurrentText( kreditor )

    def getCurrentLeistungsidentifikation( self ) -> str:
        return self._cboBuchungstext.currentText()

    def resetKreditoren( self ):
        self._cboKreditor.setCurrentIndex( -1 )

    def clearKreditoren( self ):
        self._cboKreditor.clear()

    def setKostenarten( self, kostenarten:List[str] ):
        self._cboKostenart.clear()
        for k in kostenarten:
            self._cboKostenart.addItem( k )
        self._cboKostenart.setCurrentIndex( -1 )

    def getCurrentKostenart( self ) -> str:
        return self._cboKostenart.currentText()

    def selectKostenart( self, kostenart:str ):
        self._cboKostenart.setCurrentText( kostenart )

    def resetKostenart( self ):
        self._cboKostenart.setCurrentIndex( -1 )

    def clearEditFields( self ):
        self._suspendCallbacks = True
        #self._sdBuchungsdatum.clear()
        self._cboMasterobjekt.setCurrentIndex( -1 )
        self._cboMietobjekt.setCurrentIndex( -1 )
        self._cboKreditor.setCurrentIndex( -1 )
        self._cboBuchungstext.setCurrentIndex( -1 )
        self._sdRechnungsdatum.clear()
        self._feBetrag.clear()
        self._cboKostenart.setCurrentIndex( -1 )
        self._cbUmlegbar.setChecked( False )
        self._cbWerterhaltend.setChecked( False )
        self._teBemerkung.clear()
        self._justEditing = None
        self._suspendCallbacks = False

    def provideEditFieldsPartly( self, umlegbar:bool, master_id:int, master_name:str,
                                 mobj_id:str, kreditor:str, buchungstext:str ):
        self._cbUmlegbar.setChecked( umlegbar )
        self._cboMasterobjekt.setCurrentText( master_name )
        self._cboMietobjekt.setCurrentText( mobj_id )
        self._cboKreditor.setCurrentText( kreditor )
        self._cboBuchungstext.setCurrentText( buchungstext )
        #todo: weitermachen

    def provideEditFields( self, x:XSonstAus ):
        self.clearEditFields()
        #self._suspendCallbacks = True
        self._justEditing = x
        if x.buchungsdatum:
            y, m, d = getDateParts( x.buchungsdatum )
            self._sdBuchungsdatum.setDate( y, m, d )
        else:
            self._sdBuchungsdatum.clear()
        if x.master_id is not None and x.master_id >= 0:  #master_id kann auch 0 sein! (**alle**)
            self._cboMasterobjekt.setCurrentText( x.master_name )
        if x.mobj_id:
            self._cboMietobjekt.setCurrentText( x.mobj_id )
        if x.kreditor:
            self._cboKreditor.setCurrentText( x.kreditor )
        if x.buchungstext:
            self._cboBuchungstext.setCurrentText( x.buchungstext )
        if x.rgdatum:
            y, m, d = getDateParts( x.rgdatum )
            self._sdRechnungsdatum.setDate( y, m, d )
        self._feBetrag.setText( str( x.betrag * (-1) ) )
        self._cbUmlegbar.setChecked( x.umlegbar )
        self._cbWerterhaltend.setChecked( x.werterhaltend )
        self._teBemerkung.setText( x.rgtext )
        self._suspendCallbacks = False

    def getModel( self ) -> IccTableModel:
        return self._tvAuszahlungen.model()

    def showException( self, title: str, exception: str, moretext: str = None ):
        # todo: show Qt-Errordialog
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle( title )
        msgbox.setIcon( QMessageBox.Critical )
        msgbox.setText( exception )
        if moretext:
            msgbox.setInformativeText( moretext )
        msgbox.exec_()

    ################# SET CALLBACKS  ############################

    def setBuchungsjahrChangedCallback( self, cbfnc ) -> None:
        """
        Die callback-Funktion muss als Argument das neu eingestellte Jahr als integer akzeptieren
        :param cbfnc:
        :return:
        """
        self._buchungsjahrChangedCallback = cbfnc

    def setSaveActionCallback( self, cbfnc ) -> None:
        """
        Die callback-FUnktion braucht keine Parameter empfangen.
        :param cbfnc:
        :return:
        """
        self._saveActionCallback = cbfnc

    def setSearchActionCallback( self, cbfnc ) -> None:
        """
        Die callback-Funktion muss den Searchstring als Parameter empfangen.
        :param cbfnc:
        :return:
        """
        self._searchActionCallback = cbfnc

    def setDbSearchActionCallback( self, cbfnc ) -> None:
        """
       Die callback-Funktion muss den Searchstring als Parameter empfangen.
       :param cbfnc:
       :return:
       """
        self._dbSearchActionCallback = cbfnc

    def setMasterobjektChangedCallback( self, cbfnc ):
        """
        Die callback-Funktion muss einen String als Argument akzeptieren (Name des MAsterobjekts)
        :param cbfnc:
        :return:
        """
        self._masterobjektChangedCallback = cbfnc

    def setMietobjektChangedCallback( self, cbfnc ):
        """
        Die callback-Funktion muss einen String als Argument akzeptieren (mobj_id)
        :param cbfnc:
        :return:
        """
        self._mietobjektChangedCallback = cbfnc

    def setKreditorChangedCallback( self, cbfnc):
        """
        Die callback Funktion muss 3 Argumente entgegennehmen können:
        master_name, mobj_id, neuer kreditor
        :param cbfnc:
        :return:
        """
        self._kreditorChangedCallback = cbfnc

    def setSubmitChangesCallback( self, cbfnc ):
        """
        sets the one and only callback when the user hits the OK button in the
        edit fields area.
        The given callback function has to accept the edited XSonstAus object,
        :param cbfnc:
        :return:
        """
        self._submitChangesCallback = cbfnc




###################################################################
def onChangeBuchungsjahr( jahr:int ):
    print( "neues Buchungsjahr: ", str( jahr ) )


def test():
    import sys
    app = QtWidgets.QApplication( sys.argv )
    v = SonstigeAusgabenView()
    v.setBuchungsjahre( (2020,))
    v.setBuchungsjahr( 2020 )
    v.setMasterobjekte( ("HOM_Remigius", "ILL_Eich", "NK_Ww56"))
    v.setKreditoren( ("Energie SarLorLux", "energis", "KEW", "Kreisstadt Neunkirchen", "Landeshauptstadt Saarbrücken") )

    #sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()