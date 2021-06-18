from typing import Dict

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt, QObject, Signal
from PySide2.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QWidget, QTextEdit, \
    QMenuBar, QToolBar, QAction, QMessageBox, QLineEdit, QLabel, QSizePolicy
from PySide2.QtGui import QKeySequence, QFont
from enum import Enum

from datehelper import getDateParts
from imagefactory import ImageFactory
from qtderivates import SmartDateEdit, IntDisplay
from sumfieldsprovider import SumFieldsProvider


class MainWindowAction( Enum ):
    NEW_WINDOW=2,
    SAVE_ACTIVE_VIEW=3,
    SAVE_ALL=4,
    PRINT_ACTIVE_VIEW=5,
    OPEN_MIETE_VIEW=6,
    OPEN_HGV_VIEW=7,
    FOLGEJAHR=8,
    OPEN_SOLL_MIETE_VIEW = 9,
    OPEN_SOLL_HG_VIEW = 10,
    OPEN_NKA_VIEW = 11,
    OPEN_HGA_VIEW = 12,
    RESIZE_MAIN_WINDOW = 13,
    EXPORT_CSV = 14,
    OPEN_ANLAGEV_VIEW = 15,
    OPEN_OFFENE_POSTEN_VIEW = 16,
    EXIT=99

class DummySignal(QObject):
    signal = Signal()
    def emitSignal( self ):
        self.signal.emit()

class ImmoCenterMainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self.setWindowTitle( "ImmoControlCenter" )
        #self.resize( 2500, 1500 )
        self._menubar:QMenuBar
        self.mdiArea:QMdiArea
        self._toolbar: QToolBar
        self._sdLetzteBuchung: SmartDateEdit = SmartDateEdit( self )
        self._leLetzteBuchung: QLineEdit = QLineEdit( self )

        # Summen
        self._idSumMiete = self._createSumDisplay( "Summe aller Bruttomieten" )
        self._idSummeSonstAus = self._createSumDisplay( "Summe aller sonstigen Ausgaben" )
        self._idSummeHGV = self._createSumDisplay( "Summe aller Hausgeld-Vorauszahlungen" )
        self._idSaldo = self._createSumDisplay( "Bruttomieten minus Ausgaben minus HG-Vorauszahlungen" )
        self._summenfont = QFont( "Times New Roman", 16, weight=QFont.Bold )
        self._summenartfont = QFont( "Times New Roman", 9 )
        # give others access to sum fields via Singleton SumFieldsAccess:
        self._sumfieldsAccess = SumFieldsProvider( self._idSumMiete, self._idSummeSonstAus, self._idSummeHGV, self._idSaldo,
                                                   self.onSumFieldsProvidingFailed )

        # self.dummySignal = DummySignal()
        # self.dummySignal.signal.connect( self.onSumFieldsProvidingFailed )
        self._actionCallbackFnc = None #callback function for all action callbacks
        self._shutdownCallback = None  # callback function for shutdown action
        self._createUI()

    def onSumFieldsProvidingFailed( self, msg:str ):
        self.showException( msg )

    def resizeEvent( self, event ):
        QMainWindow.resizeEvent( self, event )
        self.doCallback( MainWindowAction.RESIZE_MAIN_WINDOW )

    def _createUI( self ):
        mdiArea = QMdiArea( self )
        self.setCentralWidget( mdiArea )
        self.mdiArea = mdiArea

        self._menubar = QMenuBar( self )
        #self._menubar.setGeometry( QtCore.QRect( 0, 0, 94, 20 ) )
        self._toolBar = QToolBar( self )

        self._createImmoCenterMenu()
        self._createMietobjektMenu()
        self._createZahlungenMenu()
        self._createAbrechnungenMenu()
        self._createAnlageVMenu()
        self._createExtrasMenu()
        self._createSqlMenu()

        self._toolBar.addSeparator()
        lbl = QLabel( self, text="Letzte verarbeitete Buchung: " )
        self._toolBar.addWidget( lbl )
        self._sdLetzteBuchung.setToolTip( "Freier Eintrag der Kenndaten der letzten Buchung,\n "
                                          "um beim nächsten Anwendungsstart gezielt weiterarbeiten zu können." )
        self._sdLetzteBuchung.setMaximumWidth( 90 )
        self._toolBar.addWidget( self._sdLetzteBuchung )
        self._leLetzteBuchung.setToolTip( "Freier Eintrag der Kenndaten der letzten Buchung,\n "
                                          "um beim nächsten Anwendungsstart gezielt weiterarbeiten zu können." )
        self._leLetzteBuchung.setMaximumWidth( 300 )
        self._toolBar.addWidget( self._leLetzteBuchung )

        dummy = QWidget()
        dummy.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
        self._toolBar.addWidget( dummy )

        self._addSumFields()

        self.setMenuBar( self._menubar )
        self.addToolBar( QtCore.Qt.TopToolBarArea, self._toolBar )

    def _createImmoCenterMenu( self ):
        # Menü "ImmoCenter"
        menu = QtWidgets.QMenu( self._menubar, title="ImmoCenter" )
        self._menubar.addMenu( menu )

        #Menüpunkt "Neues Fenster..."
        action = QAction( self, text="Neues Fenster..." )
        action.triggered.connect( self.onNewWindow )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Änderungen an der aktiven Sicht speichern"
        action = QAction( self, text="Alle Änderungen speichern" )
        action.setShortcut( QKeySequence( "Ctrl+Shift+s" ) )
        #icon = QtGui.QIcon( "./images/save_30.png" )
        icon = ImageFactory.inst().getSaveIcon()
        action.setIcon( icon )
        action.triggered.connect( self.onSaveAll )
        menu.addAction( action )
        self._toolBar.addAction( action )

        # Menüpunkt "Alle Änderungen speichern"
        action = QAction( self, text="Alle Änderungen speichern" )
        action.setShortcut( QKeySequence( "Ctrl+Shift+s" ) )
        action.triggered.connect( self.onSaveAll )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Folgejahr einrichten"
        action = QAction( self, text="Folgejahr einrichten" )
        action.triggered.connect( self.onFolgejahrEinrichten )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Aktive Sicht drucken"
        action = QAction( self, text="Aktive Sicht drucken" )
        action.triggered.connect( self.onPrintActiveView )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Ende"
        action = QAction( self, text="Ende" )
        action.triggered.connect( self.onExit )
        action.setShortcut( "Alt+F4")
        menu.addAction( action )

    def _createMietobjektMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Mietobjekt" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Wohnungsstammdaten..."
        action = QAction( self, text="Wohnungsstammdaten..." )
        action.triggered.connect( self.onViewWhgStammdaten )
        menu.addAction( action )

        # Menüpunkt "Mietverhältnisse..."
        action = QAction( self, text="Mietverhältnisse..." )
        action.triggered.connect( self.onViewMietverhaeltnisse )
        menu.addAction( action )

        menu.addSeparator()

        action = QAction( self, text="Mieterwechsel..." )
        action.triggered.connect( self.onMieterwechsel )
        menu.addAction( action )

        action = QAction( self, text="Verwalterwechsel..." )
        action.triggered.connect( self.onVerwalterwechsel )
        menu.addAction( action )

    def _createZahlungenMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Ist- und Sollzahlungen" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Mietzahlungen..."
        action = QAction( self, text="Mietzahlungen..." )
        action.triggered.connect( self.onViewMietzahlungen )
        menu.addAction( action )

        # Menüpunkt "HG-Vorauszahlungen..."
        action = QAction( self, text="HG-Vorauszahlungen..." )
        action.triggered.connect( self.onViewHGVorauszahlungen )
        menu.addAction( action )

        # Menüpunkt "Rechnungen, Abgaben, Gebühren..."
        action = QAction( self, text="Rechnungen, Abgaben, Gebühren..." )
        action.triggered.connect( self.onViewRechnungen )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Offene Posten"
        action = QAction( self, text="Geforderte, aber noch nicht beglichene Ein- und Auszahlungen" )
        action.triggered.connect( self.onViewOffenePosten )
        menu.addAction( action )

        menu.addSeparator()

        # Menüpunkt "Soll-Miete..."
        action = QAction( self, text="Soll-Miete..." )
        action.triggered.connect( self.onViewSollMiete )
        menu.addAction( action )

        # Menüpunkt "Soll-Hausgeld..."
        action = QAction( self, text="Soll-Hausgeld..." )
        action.triggered.connect( self.onViewSollHausgeld )
        menu.addAction( action )

        menu.addSeparator()

    def _createAbrechnungenMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Abrechnungen" )
        self._menubar.addMenu( menu )
        action = QAction( self, text="Nebenkostenabrechnung..." )
        action.triggered.connect( self.onViewNebenkostenabrechnung )
        menu.addAction( action )

        action = QAction( self, text="Hausgeldabrechnung..." )
        action.triggered.connect( self.onViewHausgeldabrechnung )
        menu.addAction( action )

    def _createAnlageVMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="AnlageV" )
        self._menubar.addMenu( menu )
        action = QAction( self, text="Anlagen V: Objektauswahl, Vorschau, Druck..." )
        action.triggered.connect( self.onViewAnlageV )
        menu.addAction( action )

        # action = QAction( self, text="Anlagen V drucken..." )
        # action.triggered.connect( self.onViewHausgeldabrechnung )
        # menu.addAction( action )

    def _createExtrasMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Extras" )
        self._menubar.addMenu( menu )
        action = QAction( self, text="Exportiere aktive Tabelle in Calc" )
        action.triggered.connect( self.onExportActiveTableView )
        menu.addAction( action )

    def _createSqlMenu( self ):
        # Menü "ImmoCenter"
        menu = QtWidgets.QMenu( self._menubar, title="SQL" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Neue Abfrage
        action = QAction( self, text="Neue Datenbankabfrage" )
        action.setShortcut( QKeySequence( "Ctrl+n" ) )
        icon = QtGui.QIcon( "./images/sql.xpm" )
        action.setIcon( icon )
        action.triggered.connect( self.onNewSql )
        menu.addAction( action )
        self._toolBar.addAction( action )

        #Menüpunkt "Ganze Tabelle anzeigen"
        submenu = QtWidgets.QMenu( menu, title="Ganze Tabelle anzeigen" )

        action = QAction( submenu, text="masterobjekt" )
        submenu.addAction( action )

        action = QAction( submenu, text="mietobjekt" )
        submenu.addAction( action )

        action = QAction( submenu, text="mietverhaeltnis" )
        submenu.addAction( action )

        action = QAction( submenu, text="sollhausgeld" )
        submenu.addAction( action )

        action = QAction( submenu, text="sollmiete" )
        submenu.addAction( action )

        action = QAction( submenu, text="verwalter" )
        submenu.addAction( action )

        action = QAction( submenu, text="verwaltung" )
        submenu.addAction( action )

        menu.addMenu( submenu )

    def _addSumFields( self ):
        self._toolBar.addWidget( self._createSumLabel() )
        self._toolBar.addWidget( self._createSumArtLabel( "Miete", 30 ) )
        self._toolBar.addWidget( self._idSumMiete )

        self._toolBar.addWidget( self._createLabel( "-", 20 ) )

        self._toolBar.addWidget( self._createSumLabel() )
        self._toolBar.addWidget( self._createSumArtLabel( "Ausgaben", 50 ) )
        self._toolBar.addWidget( self._idSummeSonstAus )

        self._toolBar.addWidget( self._createLabel( "-", 20 ) )

        self._toolBar.addWidget( self._createSumLabel() )
        self._toolBar.addWidget( self._createSumArtLabel( "HGV", 40 ) )
        self._toolBar.addWidget( self._idSummeHGV )

        self._toolBar.addWidget( self._createLabel( "=", 20 ) )

        self._toolBar.addWidget( self._idSaldo )

        self._toolBar.addWidget( self._createSpacer( 20 ) )


    def _createSumDisplay( self, tooltip:str ) -> IntDisplay:
        display = IntDisplay( self )
        display.setMaximumWidth( 70 )
        display.setEnabled( False )
        display.setToolTip( tooltip )
        return display

    def _createSumLabel( self ) -> QLabel:
        lbl = QLabel( self, text = "∑" )
        lbl.setFont( self._summenfont )
        lbl.setMaximumWidth( 15 )
        return lbl

    def _createSumArtLabel( self, sumart:str, width:int ) -> QLabel:
        lbl = QLabel( self, text=sumart )
        lbl.setFont( self._summenartfont )
        lbl.setMaximumWidth( width )
        return lbl

    def _createLabel( self, text:str, width:int ) -> QLabel:
        lbl = QLabel( self, text=text )
        lbl.setMinimumWidth( width )
        lbl.setMaximumWidth( width )
        lbl.setAlignment( Qt.AlignCenter )
        return lbl

    def _createSpacer( self, width:int ) -> QWidget:
        spacer = QWidget( self )
        spacer.setMinimumWidth( width )
        spacer.setMaximumWidth( width )
        return spacer

    def canShutdown( self ) -> bool:
        if self._shutdownCallback:
            return self._shutdownCallback()

    def setLetzteBuchung( self, datum:str, text:str ) -> None:
        try:
            y, m, d = getDateParts( datum )
            self._sdLetzteBuchung.setDate( y, m, d )
        except:
            pass
        self._leLetzteBuchung.setText( text )

    def getLetzteBuchung( self ) -> Dict:
        """
        :return: dictionary with keys "date" and "text"
        """
        d = dict()
        d["datum"] = self._sdLetzteBuchung.getDate()
        d["text"] = self._leLetzteBuchung.text()
        return d

    def setShutdownCallback( self, callbackFnc ) -> None:
        self._shutdownCallback = callbackFnc

    def setActionCallback( self, callbackFnc ) -> None:
        self._actionCallbackFnc = callbackFnc

    def doCallback( self, action:MainWindowAction ):
        if self._actionCallbackFnc:
            self._actionCallbackFnc( action )

    def onNewWindow( self ):
        self.doCallback( MainWindowAction.NEW_WINDOW )

    def onMieterwechsel( self ):
        pass

    def onVerwalterwechsel( self ):
        pass

    # def onChangeSollmiete( self ):
    #     pass
    #
    # def onChangeSollhausgeld( self ):
    #     pass

    def onSaveActiveView( self ):
        self.doCallback( MainWindowAction.SAVE_ACTIVE_VIEW )

    def onSaveAll( self ):
        self.doCallback( MainWindowAction.SAVE_ALL )

    def onFolgejahrEinrichten( self ):
        self.doCallback( MainWindowAction.FOLGEJAHR )

    def onPrintActiveView( self ):
        self.doCallback( MainWindowAction.PRINT_ACTIVE_VIEW )

    def onExit( self ):
        self.doCallback( MainWindowAction.EXIT )

    def onViewMietzahlungen( self ):
        self.doCallback( MainWindowAction.OPEN_MIETE_VIEW )

    def onViewHGVorauszahlungen( self ):
        self.doCallback( MainWindowAction.OPEN_HGV_VIEW )

    def onViewSollMiete( self ):
        self.doCallback( MainWindowAction.OPEN_SOLL_MIETE_VIEW )

    def onViewSollHausgeld( self ):
        self.doCallback( MainWindowAction.OPEN_SOLL_HG_VIEW )

    def onViewNebenkostenabrechnung( self ):
        self.doCallback( MainWindowAction.OPEN_NKA_VIEW )

    def onViewHausgeldabrechnung( self ):
        self.doCallback( MainWindowAction.OPEN_HGA_VIEW )

    def onViewAnlageV( self ):
        self.doCallback( MainWindowAction.OPEN_ANLAGEV_VIEW )

    def onExportActiveTableView( self ):
        self.doCallback( MainWindowAction.EXPORT_CSV )

    def onViewRechnungen( self ):
        pass

    def onViewOffenePosten( self ):
        pass

    def onViewWhgStammdaten( self ):
        self.doCallback( MainWindowAction.OPEN_OFFENE_POSTEN_VIEW )

    def onViewMietverhaeltnisse( self ):
        pass

    def onNewSql( self ):
        pass

    def showException( self, exception: str, moretext: str = None ):
        # todo: show Qt-Errordialog
        print( exception )
        msg = QtWidgets.QMessageBox()
        msg.setIcon( QMessageBox.Critical )
        msg.setText( exception )
        if moretext:
            msg.setInformativeText( moretext )
        msg.setWindowTitle( "Error" )
        msg.exec_()

    def addMdiChild( self, subwin:QMdiSubWindow ) -> None:
        self.mdiArea.addSubWindow( subwin )
        subwin.widget().setAttribute( Qt.WA_DeleteOnClose )

    def _addMdiChild( self ):
        te = QTextEdit( self )
        subwin = self.mdiArea.addSubWindow( te )
        subwin.setWindowTitle( "Mein Subwin" )
        te.setAttribute( Qt.WA_DeleteOnClose )


def test():
    import sys
    app = QApplication()
    win = ImmoCenterMainWindow()
    win.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()