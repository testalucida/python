from abc import abstractmethod, ABC
from typing import List

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QApplication, QHBoxLayout, QPushButton, QComboBox, \
    QAbstractItemView, QTextEdit, QVBoxLayout, QMessageBox

from constants import SollType
from datehelper import getDateParts
from interfaces import XSollzahlung, XSollHausgeld, XSollMiete
from sollzahlungentablemodel import SollzahlungenTableModel
from tableviewext import TableViewExt
from qtderivates import CalendarDialog, SmartDateEdit, FloatEdit

class SollViewMeta( type(QWidget), type(ABC) ):
    pass

class SollzahlungenView( QWidget, ABC, metaclass=SollViewMeta ):
    """
    Ein View, der zweifach verwendet wird:
    - um die Soll-Mieten anzuzeigen (SollmietenView)
    - um die Soll-HGV anzuzeigen (SollHgvView)
    """
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
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
        tv.setSortingEnabled( True )
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
        self._feZusatz.setPlaceholderText( self._getZusatzPlaceholderText() )
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

    @abstractmethod
    def _getZusatzPlaceholderText( self ) -> str:
        pass

    def provideEditFields( self, x:XSollzahlung, editOnlyBemerkung:bool=False ):
        self._sollEdit = x
        y, m, d = getDateParts( x.von )
        self._sdVon.setDate( y, m, d )
        if x.bis:
            y, m, d = getDateParts( x.bis )
            self._sdBis.setDate( y, m, d )
        self._setNettoValue( x )
        self._teBemerkung.setText( x.bemerkung )
        self._setZusatzValue( x )
        if editOnlyBemerkung:
            self._sdVon.setEnabled( False )
            self._sdBis.setEnabled( False )
            self._feNetto.setEnabled( False )
            self._feZusatz.setEnabled( False )

    @abstractmethod
    def _setNettoValue( self, x ) -> None:
        pass

    @abstractmethod
    def _setZusatzValue( self, x ) -> None:
        pass

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
        self._tvSoll.clearSelection()
        if self._submitChangesCallback:
            if self._sollEdit:
                soll = self._getEditedSoll()
                self._submitChangesCallback( self._getEditedSoll() )

    @abstractmethod
    def _getEditedSoll( self ) -> XSollzahlung:
        pass

    def onClearEditFields( self, arg ):
        self.clearEditFields()

    def clearEditFields( self ):
        self._sdVon.clear()
        self._sdBis.clear()
        self._feNetto.clear()
        self._feZusatz.clear()
        self._teBemerkung.clear()
        self._sdVon.setEnabled( True )
        self._sdBis.setEnabled( True )
        self._feNetto.setEnabled( True )
        self._feZusatz.setEnabled( True )
        self._sollEdit = None

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

    def showException( self, title: str, exception: str, moretext: str = None ):
        # todo: show Qt-Errordialog
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle( title )
        msgbox.setIcon( QMessageBox.Critical )
        msgbox.setText( exception )
        if moretext:
            msgbox.setInformativeText( moretext )
        msgbox.exec_()

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

#####################  derived classes  ##########################

class SollmietenView( SollzahlungenView ):
    def __init__( self, parent=None ):
        SollzahlungenView.__init__( self, parent )

    def _getZusatzPlaceholderText( self ) -> str:
        return "NK-Voraus"

    def _setNettoValue( self, x ) -> None:
        self._feNetto.setText( str( x.netto ) )

    def _setZusatzValue( self, x:XSollMiete ) -> None:
        self._feZusatz.setText( str( x.nkv ) )

    def _getEditedSoll( self ) -> XSollMiete:
        x: XSollMiete = self._sollEdit
        x.von = self._sdVon.getDate()
        x.bis = self._sdBis.getDate()
        x.netto = self._feNetto.getFloatValue()
        x.bemerkung = self._teBemerkung.toPlainText()
        x.nkv = self._feZusatz.getFloatValue()
        return x

##################################################################

class SollHgvView( SollzahlungenView ):
    def __init__( self, parent=None ):
        SollzahlungenView.__init__( self, parent )

    def _getZusatzPlaceholderText( self ) -> str:
        return "RüZuFü"

    def _setNettoValue( self, x ) -> None:
        self._feNetto.setText( str( x.netto * -1 ) )

    def _setZusatzValue( self, x:XSollHausgeld ) -> None:
        self._feZusatz.setText( str( x.ruezufue * -1 ) )

    def _getEditedSoll( self ) -> XSollHausgeld:
        x: XSollHausgeld = self._sollEdit
        x.von = self._sdVon.getDate()
        x.bis = self._sdBis.getDate()
        x.netto = self._feNetto.getFloatValue() * -1
        x.bemerkung = self._teBemerkung.toPlainText()
        x.ruezufue = self._feZusatz.getFloatValue() * -1
        return x

######################################################################
def test():
    import sys
    app = QApplication( sys.argv )
    v = SollHgvView()

    #sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()