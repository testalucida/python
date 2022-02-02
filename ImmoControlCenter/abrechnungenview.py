from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QTableView, QMessageBox, \
    QAbstractItemView, QFrame
from typing import List

from icc.icctablemodel import IccTableModel
from interfaces import  XAbrechnung
from qtderivates import SmartDateEdit, FloatEdit
from sonstaus.sonstaustablemodel import SonstAusTableModel
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
        self._sdAbrechnungsdatum = SmartDateEdit( self )
        self._btnAddDayToAbrechnungsdatum = QPushButton( self )
        self._btnClearAbrechnungsdatum = QPushButton( self )

        self._sdBuchungsdatum = SmartDateEdit( self )
        self._btnAddDay = QPushButton( self )
        self._btnClearBuchungsdatum = QPushButton( self )

        self._abrechnungInfoLayout = QHBoxLayout()
        self._name = QLabel( self, text="" )
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
        self._justEditing:XAbrechnung = None
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
        lbl = QLabel( self, text="Abrechng.datum: " )
        lbl.setFixedWidth( 130 )
        self._buchungsdatumLayout.addWidget( lbl )
        self._sdAbrechnungsdatum.setFixedWidth( 85 )
        self._sdAbrechnungsdatum.setToolTip( "Datum der Forderung. Mussfeld." )
        self._buchungsdatumLayout.addWidget( self._sdAbrechnungsdatum )
        size = QSize( 25, 25 )
        self._btnAddDayToAbrechnungsdatum.setIcon( QIcon( "./images/plus.png" ) )
        self._btnAddDayToAbrechnungsdatum.setFixedSize( size )
        self._btnAddDayToAbrechnungsdatum.setToolTip( "Abrechnungsdatum um 1 Tag erhöhen" )
        self._btnAddDayToAbrechnungsdatum.clicked.connect( self.onAddDayToAbrechnungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnAddDayToAbrechnungsdatum )
        self._btnClearAbrechnungsdatum.setIcon( QIcon( "./images/cancel.png" ) )
        self._btnClearAbrechnungsdatum.setFixedSize( size )
        self._btnClearAbrechnungsdatum.setToolTip( "Forderungsdatum löschen" )
        self._btnClearAbrechnungsdatum.clicked.connect( self.onClearForderungsdatum )
        self._buchungsdatumLayout.addWidget( self._btnClearAbrechnungsdatum )

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
        self._feBetrag.setAlignment( Qt.AlignRight )
        self._feBetrag.setToolTip( "'+' für Einnahme, '-' für Ausgabe")
        self._feBetrag.setFixedWidth( 60 )
        self._abrechnungInfoLayout.addWidget( self._feBetrag )

        self._teBemerkung.setPlaceholderText( "Bemerkung zur Zahlung" )
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
            jahr = int( self._cboAbrechnungsjahr.currentText() )
            self._abrechnungsjahrChangedCallback( jahr )

    def onAddDayToBuchungsdatum( self ):
        val = self._sdBuchungsdatum.getDate()
        if val:
            dt = getQDateFromIsoString( val )
            dt = dt.addDays( 1 )
            self._sdBuchungsdatum.setDate( dt.year(), dt.month(), dt.day() )

    def onClearBuchungsdatum( self ):
        self._sdBuchungsdatum.clear()

    def onAddDayToAbrechnungsdatum( self ):
        val = self._sdAbrechnungsdatum.getDate()
        if val:
            dt = getQDateFromIsoString( val )
            dt = dt.addDays( 1 )
            self._sdAbrechnungsdatum.setDate( dt.year(), dt.month(), dt.day() )

    def onClearForderungsdatum( self ):
        self._sdAbrechnungsdatum.clear()

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
            x:XAbrechnung = self._getEditedXAbrechnung()
            ok:bool = self._submitChangesCallback( x )
            if ok:
                self._tvAbrechnungen.clearSelection()

    def _getEditedXAbrechnung( self ) -> XAbrechnung:
        if self._justEditing is None:
            self.showException( "Interner Fehler", "AbrechnungenView._getXAbrechnung()", "XAbrechnung ist leer" )
            return
        x:XAbrechnung = self._justEditing
        x.ab_datum = self._sdAbrechnungsdatum.getDate()
        x.buchungsdatum = self._sdBuchungsdatum.getDate()
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
        self._sdAbrechnungsdatum.clear()
        self._sdBuchungsdatum.clear()
        self._name.clear()
        self._feBetrag.clear()
        self._teBemerkung.clear()
        self._justEditing = None
        self._suspendCallbacks = False

    def provideEditFields( self, x:XAbrechnung ):
        self.clearEditFields()
        #self._suspendCallbacks = True
        self._justEditing = x
        if x.ab_datum:
            y, m, d = getDateParts( x.ab_datum )
            self._sdAbrechnungsdatum.setDate( y, m, d )
        if x.buchungsdatum:
            y, m, d = getDateParts( x.buchungsdatum )
            self._sdBuchungsdatum.setDate( y, m, d )
        self._name.setText( x.getName() )
        if x.betrag == 0.0:
            self._feBetrag.setText( "0" )
        else:
            self._feBetrag.setText( str( x.betrag ) )
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
        The given callback function has to accept the edited XAbrechnung object,
        :param cbfnc:
        :return:
        """
        self._submitChangesCallback = cbfnc

    def setSaveActionCallback( self, cbfnc ) -> None:
        """
        Die callback-FUnktion braucht keine Parameter empfangen.
        :param cbfnc:
        :return:
        """
        self._saveActionCallback = cbfnc

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