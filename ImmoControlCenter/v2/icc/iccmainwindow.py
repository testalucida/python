from functools import partial
from typing import Dict, Any, List

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar, QToolBar, QAction, QMessageBox, QLineEdit, \
    QLabel, \
    QMenu, QTabWidget
from PySide2.QtGui import QKeySequence, QFont
from enum import Enum

from base.baseqtderivates import SmartDateEdit, IntDisplay, BaseTabWidget
from base.messagebox import InfoBox
from datehelper import getDateParts
from v2.einaus.einausview import EinAusTableViewFrame
from v2.mtleinaus.mtleinauslogic import MieteTableModel, HausgeldTableModel
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, HausgeldTableView, HausgeldTableViewFrame


class MainWindowAction( Enum ):
    OPEN_OBJEKT_STAMMDATEN_VIEW = 1,
    OPEN_MIETVERH_VIEW = 2,
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
    EXPORT_CSV = 14,
    OPEN_ANLAGEV_VIEW = 15,
    OPEN_OFFENE_POSTEN_VIEW = 16,
    OPEN_SONST_EIN_AUS_VIEW = 17,
    NOTIZEN = 18,
    RENDITE_VIEW = 19,
    MIETERWECHSEL = 20,
    SHOW_VIEWS = 21,
    BRING_DIALOG_TO_FRONT = 22,
    SHOW_TABLE_CONTENT = 23,
    OPEN_GESCHAEFTSREISE_VIEW = 24,
    SAMMELABGABE_DETAIL = 25,
    EXPORT_DB_TO_SERVER = 26,
    IMPORT_DB_FROM_SERVER = 27,
    OPEN_ERTRAG_VIEW = 28,
    EXIT=99


class MtlZahlungenTabWidget( BaseTabWidget ):
    def __init__( self, parent=None ):
        BaseTabWidget.__init__( self, parent )

class AlleZahlungenTabWidget( BaseTabWidget ):
    def __init__( self, parent=None ):
        BaseTabWidget.__init__( self, parent )

class MainTabWidget( BaseTabWidget ):
    def __init__( self, parent=None ):
        BaseTabWidget.__init__( self, parent )
        self._mtlZahlungenTab = MtlZahlungenTabWidget()
        #self._alleZahlungenTab = AlleZahlungenTabWidget()
        self.addTab( self._mtlZahlungenTab, "Monatliche Zahlungen" )
        #self.addTab( self._alleZahlungenTab, "Alle Zahlungen" )

    def getMtlZahlungenTab( self ) -> MtlZahlungenTabWidget:
        return self._mtlZahlungenTab

    def getAlleZahlungenTab( self ) -> AlleZahlungenTabWidget:
        return self._alleZahlungenTab

class IccMainWindow( QMainWindow ):
    def __init__( self, environment ):
        QMainWindow.__init__( self )
        self.setWindowTitle( "ImmoControlCenter   " + environment )
        self._menubar:QMenuBar = None
        self._mainTab = MainTabWidget()
        self._toolbar: QToolBar = None
        self._sdLetzteBuchung: SmartDateEdit = SmartDateEdit( self )
        self._leLetzteBuchung: QLineEdit = QLineEdit( self )

        # Summen
        self._idSumMiete = self._createSumDisplay( "Summe aller Bruttomieten" )
        self._idSummeSonstAus = self._createSumDisplay( "Summe aller sonstigen Ausgaben" )
        self._idSummeHGV = self._createSumDisplay( "Summe aller Hausgeld-Vorauszahlungen" )
        self._idSaldo = self._createSumDisplay( "Bruttomieten minus Ausgaben minus HG-Vorauszahlungen" )
        self._summenfont = QFont( "Times New Roman", 16, weight=QFont.Bold )
        self._summenartfont = QFont( "Times New Roman", 9 )

        self._actionCallbackFnc = None #callback function for all action callbacks
        self._shutdownCallback = None  # callback function for shutdown action
        self._createUI()

    def setMieteTableViewFrame( self, tvf:MieteTableViewFrame ):
        self._mainTab.getMtlZahlungenTab().addTab( tvf, "Mieten" )

    def setHausgeldTableViewFrame( self, tvf:HausgeldTableViewFrame ):
        self._mainTab.getMtlZahlungenTab().addTab( tvf, "Hausgelder" )

    def setAlleZahlungenTableViewFrame( self, tvf:EinAusTableViewFrame ):
        self._mainTab.addTab( tvf, "Alle Zahlungen" )

    def setMieteModel( self, tm:MieteTableModel ):
        self._mainTab.getMtlZahlungenTab().setMieteModel( tm )

    def setHausgeldModel( self, tm:HausgeldTableModel ):
        self._mainTab.getMtlZahlungenTab().setHausgeldModel( tm )

    def onSumFieldsProvidingFailed( self, msg:str ):
        self.showException( msg )

    def _createUI( self ):
        self._createMenusAndTools()
        self.setCentralWidget( self._mainTab )

    def _createMenusAndTools( self ):
        self._menubar = QMenuBar( self )
        self._toolBar = QToolBar( self )

        # menu = QtWidgets.QMenu( title="ImmoCenter" )
        # self._menubar.addMenu( menu )

        # self._createMietobjektMenu()
        # self._createMietverhaeltnisMenu()
        # self._createZahlungenMenu()
        # self._createAbrechnungenMenu()
        # self._createAnlageVMenu()
        # self._createExtrasMenu()
        # self._createSqlMenu()
        # self._createShowViewsMenu()

        self._toolBar.addSeparator()
        lbl = QLabel( self, text="Letzte verarbeitete Buchung: " )
        self._toolBar.addWidget( lbl )
        self._sdLetzteBuchung.setToolTip( "Freier Eintrag der Kenndaten der letzten Buchung,\n "
                                          "um beim nächsten Anwendungsstart gezielt weiterarbeiten zu können." )
        self._sdLetzteBuchung.setMaximumWidth( 90 )
        self._toolBar.addWidget( self._sdLetzteBuchung )
        dummy = QWidget()
        dummy.setFixedWidth( 5 )
        self._toolBar.addWidget( dummy )
        self._leLetzteBuchung.setToolTip( "Freier Eintrag der Kenndaten der letzten Buchung,\n "
                                          "um beim nächsten Anwendungsstart gezielt weiterarbeiten zu können." )
        # self._leLetzteBuchung.setMaximumWidth( 300 )
        self._toolBar.addWidget( self._leLetzteBuchung )

        dummy = QWidget()
        dummy.setFixedWidth( 30 )
        #dummy.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred )
        self._toolBar.addWidget( dummy )

        self._addSumFields()

        self.setMenuBar( self._menubar )
        self.addToolBar( QtCore.Qt.TopToolBarArea, self._toolBar )

    def addMenu( self, menu:QMenu ):
        self._menubar.addMenu( menu )
        # for child in menu.children():
        #     print( str(child) )

    def _createMietobjektMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Mietobjekt" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Wohnungsstammdaten..."
        action = QAction( self, text="Objektstammdaten..." )
        action.triggered.connect( self.onViewObjektStammdaten )
        menu.addAction( action )

        # # Menüpunkt "Mietverhältnis..."
        # action = QAction( self, text="Mietverhältnis..." )
        # action.triggered.connect( self.onViewMietverhaeltnis )
        # menu.addAction( action )

        menu.addSeparator()

        # action = QAction( self, text="Mieterwechsel..." )
        # action.triggered.connect( self.onMieterwechsel )
        # menu.addAction( action )

        action = QAction( self, text="Verwalterwechsel..." )
        action.triggered.connect( self.onVerwalterwechsel )
        menu.addAction( action )

    def _createMietverhaeltnisMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Mietverhältnis" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Mietverhältnis..."
        action = QAction( self, text="Mietverhältnis anschauen und ändern..." )
        action.triggered.connect( self.onViewMietverhaeltnis )
        menu.addAction( action )

        menu.addSeparator()

        action = QAction( self, text="Mieterwechsel..." )
        action.triggered.connect( self.onMieterwechsel )
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
        action = QAction( self, text="Offene Posten" )
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
        action = QAction( self, text="Geschäftsreise..." )
        action.triggered.connect( self.onGeschaeftsreise )
        menu.addAction( action )
        action = QAction( self, text="Notizen..." )
        action.triggered.connect( self.onNotizen )
        menu.addAction( action )
        menu.addSeparator()
        action = QAction( self, text="Sammelabgabenbescheid aufsplitten..." )
        action.triggered.connect( self.onSammelabgabe )
        menu.addAction( action )
        menu.addSeparator()
        # action = QAction( self, text="Renditevergleich..." )
        # action.triggered.connect( self.onRenditeVergleich )
        # menu.addAction( action )
        action = QAction( self, text="Ertragsübersicht..." )
        action.triggered.connect( self.onErtragUebersicht )
        menu.addAction( action )
        menu.addSeparator()
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
        icon = QtGui.QIcon( "../images/sql.xpm" )
        action.setIcon( icon )
        action.triggered.connect( self.onNewSql )
        menu.addAction( action )
        #self._toolBar.addAction( action )

        #Menüpunkt "Ganze Tabelle anzeigen"
        self._submenuShowTableContent = QtWidgets.QMenu( menu, title="Ganze Tabelle anzeigen" )
        menu.addMenu( self._submenuShowTableContent )

    def _createShowViewsMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Views" )
        self._menubar.addMenu( menu )
        self._viewsMenu = menu

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

    def setTabellenAuswahl( self, tables:List[str] ) -> None:
        """
        Fügt dem SubMenu "Ganze Tabelle anzeigen" soviele Tabellen-Namen hinzu wie in <tables> enthalten.
        :param tables:
        :return:
        """
        n = len( tables )
        actions = [QAction( self._submenuShowTableContent ) for i in range(n)]
        for i in range( n ):
            act = actions[i]
            act.setText( tables[i] )
            #act.triggered.connect( lambda action=act: self.onShowTableContent(action) ) --> funktioniert nicht
            act.triggered.connect( partial( self.onShowTableContent, act ) )
            #txt = act.text()
            #act.triggered.connect( lambda table=txt: self.showTableContent.emit( txt ) ) --> funktioniert nicht
            self._submenuShowTableContent.addAction( act )

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

    def addOpenedDialog( self, name:str, data:Any ):
        """
        Fügt dem Views-Menü eine gerade geöffnete View hinzu
        :param name:
        :param data:
        :return:
        """
        action = QAction( self._viewsMenu, text=name )
        action.setData( data )
        self._viewsMenu.addAction( action )
        #action.triggered.connect( lambda name=name, data=data: self.bringDialogToFront.emit( name, data ) )
        action.triggered.connect( partial( self.onShowDialog, action ) )

    def removeClosedDialog( self, name:str, data:Any ):
        """
        Entfernt den Eintrag <name> aus dem Views-Menü.
        :param name:  Name der zu entfernenden  View (entspricht dem Text des Menüpunktes)
        :param data: Wird zur Identifikation der View verwendet.
        :return:
        """
        for a in self._viewsMenu.actions():
            if a.data() == data:
                self._viewsMenu.removeAction( a )
                break
        return

    def doCallback( self, action:MainWindowAction, arg=None ):
        if self._actionCallbackFnc:
            if arg:
                self._actionCallbackFnc( action, arg )
            else:
                self._actionCallbackFnc( action )

    def onNewWindow( self ):
        self.doCallback( MainWindowAction.NEW_WINDOW )

    def onMieterwechsel( self ):
        self.doCallback( MainWindowAction.MIETERWECHSEL )

    def onVerwalterwechsel( self ):
        pass

    # def onChangeSollmiete( self ):
    #     pass
    #
    # def onChangeSollhausgeld( self ):
    #     pass

    # def onSaveActiveView( self ):
    #     self.doCallback( MainWindowAction.SAVE_ACTIVE_VIEW )

    def onSaveAll( self ):
        self.doCallback( MainWindowAction.SAVE_ALL )

    def onExportDatabaseToServer( self ):
        self.doCallback( MainWindowAction.EXPORT_DB_TO_SERVER )

    def onImportDatabaseFromServer( self ):
        self.doCallback( MainWindowAction.IMPORT_DB_FROM_SERVER )

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

    def onNotizen( self ):
        self.doCallback( MainWindowAction.NOTIZEN )

    def onSammelabgabe( self ):
        self.doCallback( MainWindowAction.SAMMELABGABE_DETAIL )

    def onGeschaeftsreise( self ):
        self.doCallback( MainWindowAction.OPEN_GESCHAEFTSREISE_VIEW )

    def onRenditeVergleich( self ):
        self.doCallback( MainWindowAction.RENDITE_VIEW )

    def onErtragUebersicht( self ):
        self.doCallback( MainWindowAction.OPEN_ERTRAG_VIEW )

    def onViewRechnungen( self ):
        self.doCallback( MainWindowAction.OPEN_SONST_EIN_AUS_VIEW )

    def onViewOffenePosten( self ):
        self.doCallback( MainWindowAction.OPEN_OFFENE_POSTEN_VIEW )

    def onViewObjektStammdaten( self ):
        self.doCallback( MainWindowAction.OPEN_OBJEKT_STAMMDATEN_VIEW )

    def onViewMietverhaeltnis( self ):
        self.doCallback( MainWindowAction.OPEN_MIETVERH_VIEW )

    def onNewSql( self ):
        pass

    def onShowTableContent( self, action ):
        self.doCallback( MainWindowAction.SHOW_TABLE_CONTENT, action.text() )

    def onShowDialog( self, action ):
        self.doCallback( MainWindowAction.BRING_DIALOG_TO_FRONT, action.data() )

    def showException( self, exception: str, moretext: str = None ):
        print( exception )
        msg = QtWidgets.QMessageBox()
        msg.setIcon( QMessageBox.Critical )
        msg.setText( exception )
        if moretext:
            msg.setInformativeText( moretext )
        msg.setWindowTitle( "Error" )
        msg.exec_()

    def showInfo( self, title, msg ):
        box = InfoBox( title, msg, "", "OK" )
        box.exec_()

    # def addMdiChild( self, subwin:QMdiSubWindow ) -> None:
    #     self.mdiArea.addSubWindow( subwin )
    #     subwin.widget().setAttribute( Qt.WA_DeleteOnClose )

    # def _addMdiChild( self ):
    #     te = QTextEdit( self )
    #     subwin = self.mdiArea.addSubWindow( te )
    #     subwin.setWindowTitle( "Mein Subwin" )
    #     te.setAttribute( Qt.WA_DeleteOnClose )




def testMainTabWidget():
    app = QApplication()
    tab = MainTabWidget()
    tab.show()
    app.exec_()

def testMtlZahlungenTab():
    app = QApplication()
    tab = MtlZahlungenTabWidget()
    tab.show()
    app.exec_()


def test():
    import sys
    app = QApplication()
    win = IccMainWindow( "DEVELOP" )
    win.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()