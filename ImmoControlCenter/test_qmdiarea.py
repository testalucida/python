#from PyQt5 import QtCore, QtGui, QtWidgets
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QMdiArea, QMdiSubWindow, QWidget, QGridLayout, QTextEdit, \
    QMenuBar, QToolBar, QAction
from PySide2.QtGui import QKeySequence

class MainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self.setWindowTitle( "Test QMdiArea" )
        self.resize( 940, 800 )
        self._menubar:QMenuBar
        self._mdiArea:QMdiArea
        self._toolbar: QToolBar

        self._createUI()

        #self._addMdiChild()

    def _createUI( self ):
        mdiArea = QMdiArea( self )
        self.setCentralWidget( mdiArea )
        self._mdiArea = mdiArea

        self._menubar = QMenuBar( self )
        #self._menubar.setGeometry( QtCore.QRect( 0, 0, 94, 20 ) )
        self._toolBar = QToolBar( self )

        # self.menuFile = QtWidgets.QMenu( self._menubar, title="File" )
        # self._menubar.addMenu( self.menuFile )
        # self.actionOpen = QAction( self, text="Open...", checkable=True ) # geht nur, wenn kein Icon gesetzt wird
        # icon = QtGui.QIcon( "./images/sql.xpm" )
        # #self.actionOpen.setIcon( icon )
        # self.actionOpen.triggered.connect( self.onOpen )
        # self.menuFile.addAction( self.actionOpen )
        # self._toolBar.addAction( self.actionOpen )

        self._createImmoCenterMenu()

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

        # Menüpunkt "Änderungen an der aktiven Sicht speichern
        action = QAction( self, text="Änderungen an der aktiven Sicht speichern" )
        action.setShortcut( QKeySequence( "Ctrl+s" ) )
        icon = QtGui.QIcon( "./images/save_30.png" )
        action.setIcon( icon )
        action.triggered.connect( self.onSaveActiveView )
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

    def onOpen( self ):
        print( "onOpen" )

    def onNewWindow( self ):
        print( "onNewWindow" )

    def onSaveActiveView( self ):
        print( "onSaveActiveView" )

    def onSaveAll( self ):
        print( "onSaveAll" )

    def onPrintActiveView( self ):
        print( "onPrintActiveView" )

    def onExit( self ):
        print( "onExit" )

    def _addMdiChild( self ):
        te = QTextEdit( self )
        subwin = self._mdiArea.addSubWindow( te )
        te.setAttribute( Qt.WA_DeleteOnClose )

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(940, 669)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.mdiArea = QtWidgets.QMdiArea(self.centralwidget)
        self.mdiArea.setObjectName("mdiArea")
        self.gridLayout.addWidget(self.mdiArea, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 940, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName( "statusbar" )
        MainWindow.setStatusBar(self.statusbar)

        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

def test():
    import sys
    app = QApplication()
    win = MainWindow()
    win.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()
    # import sys
    # app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    # sys.exit(app.exec_())