from PySide2 import Qt
from PySide2.QtCore import *
#from PySide2.QtCore import QAbstractTableModel, SIGNAL
from PySide2.QtGui import QFont, QIcon, QDoubleValidator
from PySide2.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QGridLayout, QPushButton, \
    QDialog, QMessageBox
from PySide2 import QtWidgets
from typing import List, Any

#from models import KontrollModel
from icc.iccview import IccView
from imagefactory import ImageFactory
from tableview import TableView
from checktablemodel import CheckTableModel
from monthlist import monthList

# class ImageFactory:
#     __instance = None
#     _okIcon:QIcon = None
#     _nokIcon:QIcon = None
#
#     @staticmethod
#     def instance():
#         if ImageFactory.__instance == None:
#             ImageFactory()
#         return ImageFactory.__instance
#
#     def __init__(self):
#         if ImageFactory.__instance != None:
#             raise  Exception( "ImageFactory is a singleton!" )
#         ImageFactory.__instance = self
#
#     def getOkIcon(self) -> QIcon:
#         if self._okIcon == None:
#             self._okIcon = QIcon("./images/greensquare20x20.png")
#         return self._okIcon
#
#     def getNokIcon(self) -> QIcon:
#         if self._nokIcon == None:
#             self._nokIcon = QIcon("./images/redsquare20x20.png")
#         return self._nokIcon



################ ValueDialog ########################
class ValueDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Abweichender Betrag" )
        layout = QGridLayout( self )
        self.label = QtWidgets.QLabel( self )
        self.setLabelText( "Betrag eingeben:" )
        layout.addWidget( self.label, 0, 0 )

        self._numEntry = QtWidgets.QLineEdit( self )
        layout.addWidget( self._numEntry, 1, 0 )
        self._numEntry.setAlignment( Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter )
        self._numEntry.setValidator( QDoubleValidator( -9999, 9999, 2, self ) )
        self._numEntry.setFocus()

        self.btnAdd = QPushButton( self, text="+" )
        layout.addWidget( self.btnAdd, 0, 1 )
        self.btnAdd.clicked.connect( self._add )

        self.btnSub = QPushButton( self, text="-" )
        layout.addWidget( self.btnSub, 1, 1 )
        self.btnSub.clicked.connect( self._sub )

        self.btnRepl = QPushButton( self, text="=" )
        layout.addWidget( self.btnRepl, 2, 1 )
        self.btnRepl.clicked.connect( self._replace )

        self.btnCancel = QPushButton( self, text="Cancel" )
        layout.addWidget( self.btnCancel, 2, 0 )
        self.btnCancel.clicked.connect( self._cancel )

        self.setLayout( layout )

    def setCallback( self, fnc ):
        self._callback = fnc

    def setLabelText( self, text:str ) -> None:
        self.label.setText( text )

    def _doCallback( self, command:str ):
        if self._callback:
            num = self._numEntry.text()
            if num is None or num == '': num = "0"
            num = num.replace( ",", "." )
            self._callback( True, float( num ), command )
        self.close()

    def _add(self):
        self._doCallback( "add" )

    def _sub(self):
        self._doCallback( "sub" )

    def _replace(self):
        self._doCallback( "replace" )

    def _cancel( self ):
        self.close()

################# CheckButton ########################
class ControlButton( QPushButton ):
    def __init__(self, parent, isOkButton:bool=True, callbackFnc=None ):
        QPushButton.__init__( self, parent )
        self.setText( "" )
        self._isOkButton:bool = isOkButton
        self.userdata:Any
        self.clicked.connect( callbackFnc )
        fnc = self.clicked
        if isOkButton:
            self.setIcon( ImageFactory.inst().getOkIcon() )
        else:
            self.setIcon( ImageFactory.inst().getNokIcon() )

    def isOkButton(self) -> bool:
        return self._isOkButton

    def setUserData(self, userdata:Any ) -> None:
        self.userdata = userdata

################ CheckTableView ################################
class CheckTableView( TableView ):
    frozenRightClick = Signal( QPoint )
    def __init__( self ):
        TableView.__init__( self )

    def getCopyOfIndexWidget( self, oldwidget: QWidget, idx: QModelIndex ) -> None:
        btn:ControlButton = oldwidget
        b2 = ControlButton( btn.parent(), btn.isOkButton(), btn.clicked )
        return b2

    def onRightClickFrozen( self, point: QPoint ):
        # overrides TableViewExt.onRightClickFrozen
        self.frozenRightClick.emit( point )

    def onRightClick( self, point: QPoint ):
        print( "CheckTableView.onRightClick" )
        # print( "onRightClick" )
        # index = self.indexAt( point )
        # row = index.row()
        # if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
        #
        # selectedIndexes = self.selectedIndexes()
        # if selectedIndexes is None or len( selectedIndexes ) < 2: return
        # valuelist = list()
        # model = self.model()
        # if not model: return
        # for idx in selectedIndexes:
        #     val = self.model().data( idx, Qt.DisplayRole )
        #     if isinstance( val, int ) or isinstance( val, float ):
        #         valuelist.append( val )
        #     else: return
        #
        # addNumbersAction = QAction( "Berechne Summe der selektierten Zahlen" )
        # menu = QMenu( self )
        # menu.addAction( addNumbersAction )
        # menu.showNormal()
        # action = menu.exec_( self.viewport().mapToGlobal( point ) )
        # if action:
        #     sumval = sum( valuelist )
        #     dlg = SumDialog()
        #     dlg.setSum( sumval )
        #     dlg.show()
        # else:
        #     print( "nothing to do" )


################# MonatswerteBaseView #########################
class CheckView( QWidget ): # IccView ):
    def __init__(self):
        QWidget.__init__( self )
        self.setWindowTitle( "Monatswerte" )
        self._gridLayout:QtWidgets.QGridLayout = QtWidgets.QGridLayout( self )
        self._combofont = QFont( "Arial", 14, weight=QFont.Bold);
        self._cboJahr:QComboBox
        self._cboMonat:QComboBox
        self.tableView:CheckTableView
        self._btnSave:QPushButton = None
        self._createUI()
        #self._provideYearCombo()
        self._provideMonthCombo()
        self._tm:CheckTableModel = None
        self._jahrChangedCallback = None
        self._monatChangedCallback = None
        self.saveCallback = None
        self.resize(1800, 1280)

    def _createUI(self):
        self._gridLayout.setContentsMargins(3, 3, 3, 3)

        hbox = QHBoxLayout()
        self._cboJahr = QComboBox( self )
        self._cboJahr.setFont( self._combofont )
        hbox.addWidget( self._cboJahr )
        self._cboJahr.currentIndexChanged.connect( self._yearChanged )

        self._cboMonat = QComboBox(self)
        hbox.addWidget( self._cboMonat )

        #### save button
        btn = QPushButton()
        btn.clicked.connect( self.onSave )
        btn.setFlat( True )
        btn.setEnabled( False )
        btn.setToolTip( "Änderungen dieser View speichern" )
        icon = QIcon( "./images/save_30.png" )
        btn.setIcon( icon )
        size = QSize( self._cboMonat.size().height(), self._cboMonat.size().height() )
        btn.setFixedSize( size )
        iconsize = QSize( 30, 30 )
        btn.setIconSize( iconsize )
        hbox.addWidget( btn )
        self._btnSave = btn

        self._gridLayout.addLayout( hbox, 0, 0, alignment=Qt.AlignLeft )

        # add TableView to main layout
        tv = CheckTableView()
        tv.setAlternatingRowColors( True )
        tv.setStyleSheet( "alternate-background-color: lightgrey;" )
        #tv.setStyleSheet( "QHeaderView::section {background-color: red}" )
        self._gridLayout.addWidget( tv, 1, 0, 1, 2)

        self.tableView = tv

    def onSave( self ):
        if self.saveCallback:
            self.saveCallback()

    def setSaveButtonEnabled( self, enabled:bool=True ):
        self._btnSave.setEnabled( enabled )

    def getTableView( self ):
        return self.tableView

    def setJahre( self, jahre:List[int] ) -> None:
        for  jahr in jahre:
            print( jahr )
            self._cboJahr.addItem( str( jahr ) )

    def addJahr( self, jahr:int ) -> None:
        self._cboJahr.addItem( str( jahr ) )

    def setJahr( self, jahr:int ):
        self._cboJahr.setCurrentText( str( jahr ) )

    def setCheckMonat( self, monat:int ) -> None:
        self._cboMonat.setCurrentIndex( monat - 1 )

    def _provideMonthCombo(self):
        #m = datetime.datetime.now().month
        cbo = self._cboMonat
        cbo.setFont(self._combofont)
        for mon in monthList:
            cbo.addItem( mon )
        cbo.currentIndexChanged.connect(self._monthChanged)

    def _yearChanged(self, newindex):
        self.doJahrChangedCallback()

    def _monthChanged(self, newmonth):
        if( self._tm ):
            tv = self.tableView
            self._tm.setCheckmonat( newmonth + 1 )
            top_cell = self._tm.index( 0, 0 )
            bottom_cell = self._tm.index( 0, 2 )
            tv.dataChanged( top_cell, bottom_cell, [Qt.BackgroundRole, ] )
            index = self._tm.getCheckmonatColumnIndex()
            tv.scrollTo( index )
            tv.repaint()
            self.repaint()
        self.doCheckMonatChangedCallback()

    def doJahrChangedCallback( self ):
        if self._jahrChangedCallback:
            self._jahrChangedCallback( self.getSelectedJahr() )

    def doCheckMonatChangedCallback( self ):
        if self._monatChangedCallback:
            self._monatChangedCallback( self.getSelectedCheckMonat() )

    def isChanged( self ) -> bool:
        return self._tm.isChanged()

    def setJahrChangedCallback( self, cb_fnc ):
        """
        function to be called on changes of year
        function signature: fnc( year )
        :param cb_fnc:
        :return:
        """
        self._jahrChangedCallback = cb_fnc

    def setCheckMonatChangedCallback( self, cb_fnc ):
        """
        function to be called on changes of check month
        function signature: fnc( month )
        :param cb_fnc:
        :return:
        """
        self._monatChangedCallback = cb_fnc

    def getModel( self ) -> CheckTableModel:
        return self._tm

    def setModel(self, tm:CheckTableModel ) -> None:
        self.tableView.setModel( tm )
        c = tm.rowCount(self)
        okColumnIdx = tm.getOkColumnIdx()
        nokColumnIdx = tm.getNokColumnIdx()
        for r in range( tm.rowCount(self) ):
            btnOk = ControlButton( self, True, self._okButtonClicked )
            # btnOk.clicked.connect( self._okButtonClicked )
            btnNok = ControlButton( self, False, self._nokButtonClicked )
            # btnNok.clicked.connect(self._nokButtonClicked)
            self.tableView.setIndexWidget( tm.index( r, okColumnIdx ), btnOk )
            self.tableView.setIndexWidget( tm.index( r, nokColumnIdx ), btnNok )
        self.tableView.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self.tableView.resizeColumnsToContents()
        col = tm.getCheckmonatColumnIndex().column()
        # col im Januar: 8, im Mai: 12
        # ab Juli scrollen wir nach links, damit die Monate Okt bis Dez sichtbar werden.
        # als Scrollwert geben wir Spalte 7 ein; das ist experimentell herausgefunden
        if col > 13: # größer als Juni
            idx = tm.index( 0, 7 )
            self.tableView.scrollTo( idx )

        self._tm = tm

    def _okButtonClicked(self, checkstate:bool ):
        app = QApplication.instance()
        button:QPushButton = app.focusWidget()
        index = self.tableView.indexAt( button.pos() )
        if index.isValid():
            self._tm.setOkState( index, button.isChecked() )

    def _nokButtonClicked(self, checkstate: bool):
        # Soll-Vorgabe nicht erfüllt; manuelle Eingabe über ValueDialog
        def dlg_callback(ok: bool, value: float, command:str ):
            if index.isValid():
                #print(index.row(), index.column())
                oldval = self._tm.getCheckMonatIst( index )
                newval = 0 if oldval is None else oldval
                if command == "add":
                    newval += value
                elif command == "sub":
                    newval -= value
                else:
                    newval = value
                self._tm.setCheckMonatValue( index, newval )
            return

        app = QApplication.instance()
        button: QPushButton = app.focusWidget()
        index = self.tableView.indexAt( button.pos() )
        dlg = ValueDialog( self )
        dlg.setCallback( dlg_callback )
        dlg.show()

    def showException( self, exception:str, moretext:str=None ):
        #todo: show Qt-Errordialog
        print( exception )
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText( exception )
        if moretext:
            msg.setInformativeText( moretext )
        msg.setWindowTitle("Error")
        msg.exec_()

    def getSelectedJahr(self) -> int:
        return int( self._cboJahr.currentText() )

    def getSelectedCheckMonat( self ) -> int:
        return self._cboMonat.currentIndex() + 1

def test():
    app = QApplication()
    win = CheckView()

    rows = ({"Col 1": "1/0", "Col 2": 345,    "Col 3": "Ave Maria"},
            {"Col 1": "2/0", "Col 2": -123.45, "Col 3": "Summer in the City"},
            {"Col 1": "3/0", "Col 2": 776.45, "Col 3": "Winter in the Park"}
           )
    tm = CheckTableModel( [], 11, 21 )

    win.setModel( tm )

    win.show()
    app.exec_()

if __name__ == "__main__":
    test()
