from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSize, Qt, QDate, QPoint
from PySide2.QtGui import QIcon, QDoubleValidator, QFont, QIntValidator
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit, QCheckBox, QPushButton, QCalendarWidget, \
    QVBoxLayout, QDialog, QBoxLayout, QHBoxLayout, QTextEdit, QSpinBox, QLabel, QTableView, QMessageBox, \
    QAbstractItemView, QFrame
from typing import List

from icctablemodel import IccTableModel
from interfaces import XSonstAus, XKontoEintrag
from qtderivates import IntDisplay, SmartDateEdit, FloatEdit
from sonstaustablemodel import SonstAusTableModel
from tableviewext import TableViewExt
from datehelper import *


#########################  AbrechnungenView  ##############################
class AbrechnungenView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        #self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._btnSave = QPushButton( self )

        self._tvAbrechnungen = TableViewExt( self )

        self._buchungsdatumLayout = QHBoxLayout()
        self._sdForderungsdatum = SmartDateEdit( self )
        self._btnAddDayToForderungsdatum = QPushButton( self )
        self._btnClearForderungsdatum = QPushButton( self )

        self._sdBuchungsdatum = SmartDateEdit( self )
        self._btnAddDay = QPushButton( self )
        self._btnClearBuchungsdatum = QPushButton( self )

        self._abrechnungInfoLayout = QHBoxLayout()
        self._name = QLabel( self, text="MeierHuberMüller" )
        self._cboAbrechnungsjahr = QtWidgets.QComboBox( self )
        self._feBetrag: FloatEdit = FloatEdit( self )

        self._teBemerkung = QTextEdit( self )
        self._btnOk = QPushButton( self )
        self._btnClear = QPushButton( self )
        # actions für ContextMenu
        #self._contextMenuActions:List[QAction] = None
        # Callbacks
        self._abrechnungsjahrChangedCallback = None
        self._saveActionCallback = None

        self._submitChangesCallback = None
        self._justEditing:XKontoEintrag = None
        self._suspendCallbacks = False

        self._createGui()

    def _createGui( self ):
        self._assembleToolbar()
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._toolbarLayout.addStretch( 50 )
        ### tableView
        tv = self._tvAbrechnungen
        tv.setSelectionBehavior( QAbstractItemView.SelectRows )
        tv.setAlternatingRowColors( True )
        tv.verticalHeader().setVisible( False )
        tv.horizontalHeader().setMinimumSectionSize( 0 )
        self._mainLayout.addWidget( tv, 1, 0, 1, 1 )
        #Buchungsdatum
        self._assembleBuchungsdatum()
        self._mainLayout.addLayout( self._buchungsdatumLayout, 2, 0, alignment=Qt.AlignLeft )
        # Name, Abrechnungsjahr, Betrag, Bemerkung, Buttons
        self._assembleAbrechnungInfo()
        self._mainLayout.addLayout( self._abrechnungInfoLayout, 3, 0, alignment=Qt.AlignLeft )
        # self._assembleRechnungsdaten()
        # self._mainLayout.addLayout( self._editRechnungLineLayout, 4, 0, alignment=Qt.AlignLeft )

    def _assembleToolbar( self ):
        #### Combobox Buchungsjahr
        font = QFont( "Arial", 14, weight=QFont.Bold )
        self._cboAbrechnungsjahr.setFont( font )
        self._cboAbrechnungsjahr.setToolTip(
            "Das hier eingestellte Jahr bestimmt die NK-Abrechnungen, die in der Tabelle angezeigt werden." )
        self._cboAbrechnungsjahr.currentIndexChanged.connect( self.onAbrechnungsjahrChanged )
        self._toolbarLayout.addWidget( self._cboAbrechnungsjahr, stretch=0, alignment=Qt.AlignLeft )

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

    def _assembleBuchungsdatum( self ):
        lbl = QLabel( self, text="Forderungsdatum: " )
        lbl.setFixedWidth( 130 )
        self._buchungsdatumLayout.addWidget( lbl )
        self._sdForderungsdatum.setFixedWidth( 85 )
        self._sdForderungsdatum.setToolTip( "Datum der Forderung. Mussfeld." )
        self._buchungsdatumLayout.addWidget( self._sdForderungsdatum )
        size = QSize( 25, 25 )
        self._btnAddDayToForderungsdatum.setIcon( QIcon( "./images/plus.png" ) )
        self._btnAddDayToForderungsdatum.setFixedSize( size )
        self._btnAddDayToForderungsdatum.setToolTip( "Forderungsdatum um 1 Tag erhöhen" )
        self._btnAddDayToForderungsdatum.clicked.connect( self.onAddDayToForderungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnAddDayToForderungsdatum )
        self._btnClearForderungsdatum.setIcon( QIcon( "./images/cancel.png" ) )
        self._btnClearForderungsdatum.setFixedSize( size )
        self._btnClearForderungsdatum.setToolTip( "Forderungsdatum löschen" )
        self._btnClearForderungsdatum.clicked.connect( self.onClearForderungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnClearForderungsdatum )

        lbl = QLabel( self, text="Buchungsdatum: " )
        lbl.setFixedWidth( 120 )
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

    def _assembleAbrechnungInfo( self ):
        lbl = QLabel( self, text="Mieter/Verwalter: " )
        lbl.setFixedWidth( 130 )
        self._abrechnungInfoLayout.addWidget( lbl )

        self._name.setFrameShape( QFrame.Panel )
        self._name.setFrameShadow( QFrame.Sunken )
        self._name.setFixedWidth( 150 )
        self._name.setFixedHeight( 25 )
        self._abrechnungInfoLayout.addWidget( self._name )

        # Gutschrift/Nachzahlung
        lbl = QLabel( self, text="Betrag: " )
        self._abrechnungInfoLayout.addWidget( lbl )
        self._feBetrag.setToolTip( "'+' für Einzahlung, '-' für Auszahlung")
        self._feBetrag.setFixedWidth( 60 )
        self._abrechnungInfoLayout.addWidget( self._feBetrag )

        self._teBemerkung.setPlaceholderText( "Bemerkung zur Auszahlung" )
        self._teBemerkung.setMaximumSize( QtCore.QSize( 16777215, 50 ) )
        self._abrechnungInfoLayout.addWidget( self._teBemerkung, stretch=1 )

        # Buttons
        vbox = QVBoxLayout()
        self._btnOk.setIcon( QIcon( "./images/checked.png" ) )
        self._btnOk.setDefault( True )
        self._btnOk.setToolTip( "Daten in Tabelle übernehmen (kein Speichern)" )
        self._btnOk.clicked.connect( self.onOkEditFields )
        vbox.addWidget( self._btnOk )
        self._btnClear.setIcon( QIcon( "./images/cancel.png" ) )
        self._btnClear.setToolTip( "Änderungen verwerfen und Felder leeren" )
        self._btnClear.clicked.connect( self.onClearEditFields )
        vbox.addWidget( self._btnClear )
        self._abrechnungInfoLayout.addLayout( vbox )

    def onAbrechnungsjahrChanged( self, newindex ):
        """
        Slot für die Änderung des Buchungsjahrs.
        :param newindex:
        :return:
        """
        if self._abrechnungsjahrChangedCallback and not self._suspendCallbacks:
            jahr = int( self._cboBuchungsjahr.currentText() )
            self._abrechnungsjahrChangedCallback( jahr )

    def onAddDayToBuchungsdatum( self ):
        val = self._sdBuchungsdatum.getDate()
        if val:
            dt = getQDateFromIsoString( val )
            dt = dt.addDays( 1 )
            self._sdBuchungsdatum.setDate( dt.year(), dt.month(), dt.day() )

    def onClearBuchungsdatum( self ):
        self._sdBuchungsdatum.clear()

    def onAddDayToForderungsdatum( self ):
        val = self._sdForderungsdatum.getDate()
        if val:
            dt = getQDateFromIsoString( val )
            dt = dt.addDays( 1 )
            self._sdForderungsdatum.setDate( dt.year(), dt.month(), dt.day() )

    def onClearForderungsdatum( self ):
        self._sdForderungsdatum.clear()

    def setSaveButtonEnabled( self, enable:bool=True ):
        self._btnSave.setEnabled( enable )

    def onSave( self ):
        if self._saveActionCallback:
            self._saveActionCallback()

    def onOkEditFields( self, arg ):
        """
        OK gedrückt. Änderungen an Callback-Funktion melden.
        :param arg:
        :return:
        """
        if self._submitChangesCallback:
            x:XKontoEintrag = self._getEditedXKontoEintrag()
            ok:bool = self._submitChangesCallback( x )
            if ok:
                self._tvAbrechnungen.clearSelection()

    def _getEditedXKontoEintrag( self ) -> XKontoEintrag:
        if self._justEditing is None:
            self.showException( "Interner Fehler", "AbrechnungenView._getEditedXKontoEintrag()", "XKontoEintrag ist leer" )
        x:XKontoEintrag = self._justEditing
        x.forderungsdatum = self._sdForderungsdatum.getDate()
        x.buchungsdatum = self._sdBuchungsdatum.getDate()
        x.jahr = int( self._cboAbrechnungsjahr.currentText() )
        x.betrag = self._feBetrag.getFloatValue()
        x.bemerkung = self._teBemerkung.toPlainText()
        return x

    def onClearEditFields( self, arg ):
        self.clearEditFields()
        self._tvAbrechnungen.clearSelection()

    def getAbrechnungenTableView( self ) -> QTableView:
        return self._tvAbrechnungen

    def setAbrechnungenTableModel( self, tm:SonstAusTableModel ):
        self._tvAbrechnungen.setModel( tm )
        self._tvAbrechnungen.resizeColumnsToContents()
        #self._tvAuszahlungen.setColumnWidth( 0, 10 )
        #self._tvAuszahlungen.setColumnWidth( 1, 10 )

    def setAbrechnungsjahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr-Combobox
        :param jahre:
        :return:
        """
        self._suspendCallbacks = True
        for jahr in jahre:
            self._cboAbrechnungsjahr.addItem( str( jahr ) )
        self._suspendCallbacks = False

    def clearEditFields( self ):
        self._suspendCallbacks = True
        self._sdForderungsdatum.clear()
        self._sdBuchungsdatum.clear()
        self._name.clear()
        self._cboAbrechnungsjahr.setCurrentIndex( -1 )
        self._feBetrag.clear()
        self._teBemerkung.clear()
        self._justEditing = None
        self._suspendCallbacks = False

    def provideEditFields( self, x:XKontoEintrag ):
        self.clearEditFields()
        #self._suspendCallbacks = True
        self._justEditing = x
        if x.forderungsdatum:
            y, m, d = getDateParts( x.forderungsdatum )
            self._sdForderungsdatum.setDate( y, m, d )
        if x.buchungsdatum:
            y, m, d = getDateParts( x.buchungsdatum )
            self._sdBuchungsdatum.setDate( y, m, d )
        self._name.setText( x.name )
        self._cboAbrechnungsjahr.setCurrentText( x.jahr )
        self._feBetrag.setText( str( x.betrag * (-1) ) )
        self._teBemerkung.setText( x.bemerkung )
        self._suspendCallbacks = False

    def getModel( self ) -> IccTableModel:
        return self._tvAbrechnungen.model()

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

    def setAbrechnungsjahrChangedCallback( self, cbfnc ) -> None:
        """
        Die callback-Funktion muss als Argument das neu eingestellte Jahr als integer akzeptieren
        :param cbfnc:
        :return:
        """
        self._abrechnungsjahrChangedCallback = cbfnc


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

def test():
    import sys
    app = QtWidgets.QApplication( sys.argv )
    v = AbrechnungenView()
    v.setAbrechnungsjahre( (2019, 2020) )

    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()