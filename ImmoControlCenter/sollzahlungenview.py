from typing import List

from PySide2 import QtCore
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QApplication, QHBoxLayout, QPushButton, QComboBox, \
    QAbstractItemView, QTextEdit, QVBoxLayout

from constants import SollType
from datehelper import getDateParts
from interfaces import XSollzahlung, XSollHausgeld, XSollMiete
from sollzahlungentablemodel import SollzahlungenTableModel
from tableviewext import TableViewExt
from qtderivates import CalendarDialog, SmartDateEdit, FloatEdit

class SollzahlungenView( QWidget ):
    """
    Ein View, der zweifach verwendet wird:
    - um die Soll-Mieten anzuzeigen
    - um die Soll-HGV anzuzeigen
    """
    def __init__( self, soll_type:SollType, parent=None ):
        QWidget.__init__( self, parent )
        self._sollType = soll_type
        #self.setWindowTitle( "Sonstige Ausgaben: Rechnungen, Abgaben, Gebühren etc." )
        self._mainLayout = QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._btnFilter = QPushButton( self )
        self._btnSave = QPushButton( self )
        self._tvSoll = TableViewExt( self )
        self._editFieldsLayout = QHBoxLayout()
        #self._cboMietverhaeltnisse = QComboBox( self )
        self._sdVon = SmartDateEdit( self )
        self._sdBis = SmartDateEdit( self )
        self._feNetto = FloatEdit( self )
        self._feZusatz = FloatEdit( self )
        self._teBemerkung = QTextEdit( self )
        self._btnOk = QPushButton( self )
        self._btnClear = QPushButton( self )

        #callbacks
        self._submitChangesCallback = None
        self._saveActionCallback = None

        #TableModel für die anzuzeigenden Zahlungen
        self._tmSoll:SollzahlungenTableModel = None
        self._sollEdit:XSollzahlung = None

        self._createGui()

    def _createGui( self ):
        self._assembleToolbar()
        self._toolbarLayout.addStretch( 50 )
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        ### tableView
        tv = self._tvSoll
        tv.setSelectionBehavior( QAbstractItemView.SelectRows )
        tv.setAlternatingRowColors( True )
        tv.verticalHeader().setVisible( False )
        tv.horizontalHeader().setMinimumSectionSize( 0 )
        self._mainLayout.addWidget( tv, 1, 0, 1, 1 )
        self._assembleEditFields()
        self._mainLayout.addLayout( self._editFieldsLayout, 2, 0, alignment=Qt.AlignLeft )

    def _assembleToolbar( self ):
        btn = self._btnFilter
        btn.setFlat( True )
        btn.setEnabled( True )
        btn.setToolTip( "Alle Sollzahlungen anzeigen (nicht nur aktive)" )
        icon = QIcon( "./images/filter_20x28.png" )
        btn.setIcon( icon )
        size = QSize( 30, 30 )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        self._toolbarLayout.addWidget( btn, stretch=0, alignment=Qt.AlignLeft )

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
        self._toolbarLayout.addWidget( btn, stretch=0, alignment=Qt.AlignLeft )

    def _assembleEditFields( self ):
        # cbo = self._cboMietverhaeltnisse
        # cbo.setPlaceholderText( "Mieter auswählen" if self._sollType == SollType.MIETE_SOLL else "Verwaltung auswählen" )
        # self._editFieldsLayout.addWidget( cbo )
        self._sdVon.setPlaceholderText( "von" )
        self._editFieldsLayout.addWidget( self._sdVon )
        self._sdBis.setPlaceholderText( "bis" )
        self._editFieldsLayout.addWidget( self._sdBis )
        self._feNetto.setPlaceholderText( "Netto" )
        self._editFieldsLayout.addWidget( self._feNetto )
        self._feZusatz.setPlaceholderText( "RüZuFü" if self._sollType == SollType.HAUSGELD_SOLL else "NKV" )
        self._editFieldsLayout.addWidget( self._feZusatz )
        self._teBemerkung.setPlaceholderText( "Bemerkung" )
        self._teBemerkung.setMaximumSize( QtCore.QSize( 16777215, 50 ) )
        self._editFieldsLayout.addWidget( self._teBemerkung, stretch=1 )
        ### buttons
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
        self._editFieldsLayout.addLayout( vbox )

    def provideEditFields( self, x:XSollzahlung ):
        self._sollEdit = x
        y, m, d = getDateParts( x.von )
        self._sdVon.setDate( y, m, d )
        if x.bis:
            self._sdBis.setDate( getDateParts( x.bis ) )
        self._feNetto.setText( str( x.netto ) )
        self._teBemerkung.setText( x.bemerkung )
        if self._sollType == SollType.HAUSGELD_SOLL:
            x:XSollHausgeld = x
            self._feZusatz.setText( str( x.ruezufue ) )

    def setSollzahlungenTableModel( self, tm:SollzahlungenTableModel ):
        self._tmSoll = tm
        self._tvSoll.setModel( tm )
        self._tvSoll.resizeColumnsToContents()

    def getModel( self ) -> SollzahlungenTableModel:
        return self._tmSoll

    def getTableView( self ) -> TableViewExt:
        return self._tvSoll

    def onOkEditFields( self, arg ):
        """
        OK gedrückt. Änderungen an Callback-Funktion melden.
        :param arg:
        :return:
        """
        if self._submitChangesCallback:
            self._submitChangesCallback( self._getEditedSoll() )

    def _getEditedSoll( self ) -> XSollzahlung:
        x:XSollzahlung = self._sollEdit
        x.von = self._sdVon.getDate()
        x.bis = self._sdBis.getDate()
        x.netto = self._feNetto.getFloatValue()
        x.bemerkung = self._teBemerkung.toPlainText()
        if self._sollType == SollType.HAUSGELD_SOLL:
            x:XSollHausgeld = x
            x.ruezufue = self._feZusatz.getFloatValue()
        else:
            x:XSollMiete = x
            x.nkv = self._feZusatz.getFloatValue()
        return x

    def onClearEditFields( self, arg ):
        self.clearEditFields()

    def clearEditFields( self ):
        self._sdVon.clear()
        self._sdBis.clear()
        self._feNetto.clear()
        self._feZusatz.clear()
        self._teBemerkung.clear()

    def onSave( self ):
        if self._saveActionCallback:
            self._saveActionCallback()

    def setSaveActionCallback( self, cbfnc ) -> None:
        """
        Die callback-FUnktion braucht keine Parameter empfangen.
        :param cbfnc:
        :return:
        """
        self._saveActionCallback = cbfnc

    def setSaveButtonEnabled( self, enable:bool=True ):
        self._btnSave.setEnabled( enable )

    ################ SET CALLBACKS  ########################

    def setSubmitChangesCallback( self, cbfnc ):
        """
        sets the one and only callback when the user hits the OK button in the
        edit fields area.
        The given callback function has to accept two XSollzahlung objects:
        - in case of only editing the second one will not be provided
        - in case of a new intervall the first one will be the new one, the second will be the one to terminate.
        :param cbfnc:
        :return:
        """
        self._submitChangesCallback = cbfnc

def test():
    import sys
    app = QApplication( sys.argv )
    v = SollzahlungenView()

    #sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()