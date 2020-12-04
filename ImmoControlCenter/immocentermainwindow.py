from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QWidget, QGridLayout, QTextEdit, \
    QMenuBar, QToolBar, QAction, QMessageBox
from PySide2.QtGui import QKeySequence
from enum import Enum

class MainWindowAction( Enum ):
    NEW_WINDOW=2
    SAVE_ACTIVE_VIEW=3
    SAVE_ALL=4
    PRINT_ACTIVE_VIEW=5
    OPEN_MIETE_VIEW=6
    OPEN_HGV_VIEW=7
    EXIT=99


class ImmoCenterMainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self.setWindowTitle( "ImmoControlCenter" )
        self.resize( 940, 800 )
        self._menubar:QMenuBar
        self.mdiArea:QMdiArea
        self._toolbar: QToolBar
        self._actionCallbackFnc = None #callback function for all action callbacks

        self._createUI()

        # self._addMdiChild()
        # self._addMdiChild()

    def _createUI( self ):
        mdiArea = QMdiArea( self )
        self.setCentralWidget( mdiArea )
        self.mdiArea = mdiArea

        self._menubar = QMenuBar( self )
        #self._menubar.setGeometry( QtCore.QRect( 0, 0, 94, 20 ) )
        self._toolBar = QToolBar( self )

        self._createImmoCenterMenu()
        self._createMietobjektMenu()
        self._createViewMenu()
        self._createSqlMenu()

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
        icon = QtGui.QIcon( "./images/save_30.png" )
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

        action = QAction( self, text="Mieterwechsel..." )
        action.triggered.connect( self.onMieterwechsel )
        menu.addAction( action )

        action = QAction( self, text="Verwalterwechsel..." )
        action.triggered.connect( self.onVerwalterwechsel )
        menu.addAction( action )

        menu.addSeparator()

        action = QAction( self, text="Änderung Miete..." )
        action.triggered.connect( self.onChangeSollmiete() )
        menu.addAction( action )

        action = QAction( self, text="Änderung Hausgeld..." )
        action.triggered.connect( self.onChangeSollhausgeld() )
        menu.addAction( action )

    def _createViewMenu( self ):
        menu = QtWidgets.QMenu( self._menubar, title="Sicht" )
        self._menubar.addMenu( menu )

        # Menüpunkt "Mietzahlungen..."
        action = QAction( self, text="Mietzahlungen..." )
        action.triggered.connect( self.onViewMietzahlungen )
        menu.addAction( action )

        # Menüpunkt "HG-Vorauszahlungen..."
        action = QAction( self, text="HG-Vorauszahlungen..." )
        action.triggered.connect( self.onViewHGVorauszahlungen )
        menu.addAction( action )

        # Menüpunkt "Soll-Zahlungen..."
        action = QAction( self, text="Soll-Zahlungen..." )
        action.triggered.connect( self.onViewSollzahlungen )
        menu.addAction( action )

        # Menüpunkt "NK- und HG-Abrechnungen Vorjahr..."
        action = QAction( self, text="NK- und HG-Abrechnungen Vorjahr..." )
        action.triggered.connect( self.onViewAbrechnungen )
        menu.addAction( action )

        # Menüpunkt "Handwerker, Kommunen, Versorger..."
        action = QAction( self, text="Handwerker, Kommunen, Versorger..." )
        action.triggered.connect( self.onViewRechnungen )
        menu.addAction( action )

        # Menüpunkt "Wohnungsstammdaten..."
        action = QAction( self, text="Wohnungsstammdaten..." )
        action.triggered.connect( self.onViewWhgStammdaten )
        menu.addAction( action )

        # Menüpunkt "Mietverhältnisse..."
        action = QAction( self, text="Mietverhältnisse..." )
        action.triggered.connect( self.onViewMietverhaeltnisse )
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

    def onChangeSollmiete( self ):
        pass

    def onChangeSollhausgeld( self ):
        pass

    def onSaveActiveView( self ):
        self.doCallback( MainWindowAction.SAVE_ACTIVE_VIEW )

    def onSaveAll( self ):
        self.doCallback( MainWindowAction.SAVE_ALL )

    def onPrintActiveView( self ):
        self.doCallback( MainWindowAction.PRINT_ACTIVE_VIEW )

    def onExit( self ):
        self.doCallback( MainWindowAction.EXIT )

    def onViewMietzahlungen( self ):
        self.doCallback( MainWindowAction.OPEN_MIETE_VIEW )

    def onViewHGVorauszahlungen( self ):
        self.doCallback( MainWindowAction.OPEN_HGV_VIEW )

    def onViewSollzahlungen( self ):
        pass

    def onViewAbrechnungen( self ):
        pass

    def onViewRechnungen( self ):
        pass

    def onViewWhgStammdaten( self ):
        pass

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