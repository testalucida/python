from PySide2 import Qt
from PySide2.QtCore import *
#from PySide2.QtCore import QAbstractTableModel, SIGNAL
from PySide2.QtGui import QFont, QIcon, QDoubleValidator
from PySide2.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QPushButton, \
    QDialog, QMessageBox
from PySide2 import QtWidgets
import datetime
from typing import List, Dict, Any

#from models import KontrollModel
from tableview import TableView
from checktablemodel import CheckTableModel
from monthlist import monthList

class ImageFactory:
    __instance = None
    _okIcon:QIcon = None
    _nokIcon:QIcon = None

    @staticmethod
    def instance():
        if ImageFactory.__instance == None:
            ImageFactory()
        return ImageFactory.__instance

    def __init__(self):
        if ImageFactory.__instance != None:
            raise  Exception( "ImageFactory is a singleton!" )
        ImageFactory.__instance = self

    def getOkIcon(self) -> QIcon:
        if self._okIcon == None:
            self._okIcon = QIcon("./images/greensquare20x20.png")
        return self._okIcon

    def getNokIcon(self) -> QIcon:
        if self._nokIcon == None:
            self._nokIcon = QIcon("./images/redsquare20x20.png")
        return self._nokIcon

################ ValueDialog ########################
class ValueDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Abweichender Betrag" )
        self.resize(245, 77)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(150, 10, 81, 241))
        self.buttonBox.setOrientation(Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self._numEntry = QtWidgets.QLineEdit(self)
        self._numEntry.setGeometry(QRect(10, 40, 113, 23))
        self._numEntry.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._numEntry.setValidator( QDoubleValidator( 0, 9999, 2, self ) )
        self._numEntry.setFocus()
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QRect(10, 9, 171, 16))
        self.setLabelText( "Betrag eingeben:" )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self._callback = None

    def setCallback( self, fnc ):
        self._callback = fnc

    def setLabelText( self, text:str ) -> None:
        self.label.setText( text )

    def accept(self):
        print( "accept" )
        if self._callback:
            self._callback( True, self._numEntry.text() )
        QDialog.accept(self)

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
            self.setIcon( ImageFactory.instance().getOkIcon() )
        else:
            self.setIcon( ImageFactory.instance().getNokIcon() )

    def isOkButton(self) -> bool:
        return self._isOkButton

    def setUserData(self, userdata:Any ) -> None:
        self.userdata = userdata


################ CheckTableView ################################
class CheckTableView( TableView ):
    def __init__( self ):
        TableView.__init__( self )

    def getCopyOfIndexWidget( self, oldwidget: QWidget, idx: QModelIndex ) -> None:
        btn:ControlButton = oldwidget
        b2 = ControlButton( btn.parent(), btn.isOkButton(), btn.clicked )
        return b2


################# MonatswerteBaseView #########################
class CheckView( QWidget ):
    def __init__(self):
        QWidget.__init__( self )
        self.setWindowTitle( "Monatswerte" )
        self._gridLayout:QtWidgets.QGridLayout = QtWidgets.QGridLayout( self )
        self._combofont = QFont( "Arial", 14, weight=QFont.Bold);
        self._cboJahr:QComboBox
        self._cboMonat:QComboBox
        self._tableView:CheckTableView
        self._createUI()
        self._provideYearCombo()
        self._provideMonthCombo()
        self._tm:CheckTableModel = None
        self._zeitraumChangedCallback = None
        self.resize(1800, 1280)

    def _createUI(self):
        self._gridLayout.setContentsMargins(3, 3, 3, 3)

        hbox = QHBoxLayout()
        self._cboJahr = QComboBox( self )
        hbox.addWidget( self._cboJahr )
        #self._gridLayout.addWidget( self._cboJahr, 0, 0, alignment=Qt.AlignLeft )

        self._cboMonat = QComboBox(self)
        hbox.addWidget( self._cboMonat )
        self._gridLayout.addLayout( hbox, 0, 0, alignment=Qt.AlignLeft )

        # add TableView to main layout
        tv = CheckTableView()
        tv.setAlternatingRowColors( True )
        tv.setStyleSheet( "alternate-background-color: lightgrey;" )
        #tv.setStyleSheet( "QHeaderView::section {background-color: red}" )
        self._gridLayout.addWidget( tv, 1, 0, 1, 2)

        self._tableView = tv

    def _provideYearCombo(self):
        y = datetime.datetime.now().year
        cbo = self._cboJahr
        cbo.setFont(self._combofont)
        for i in range(-2, 2):
            cbo.addItem(str(y + i))
        #cbo.setCurrentIndex(2)
        cbo.currentIndexChanged.connect(self._yearChanged)

    def _provideMonthCombo(self):
        #m = datetime.datetime.now().month
        cbo = self._cboMonat
        cbo.setFont(self._combofont)
        for mon in monthList:
            cbo.addItem( mon )
        #cbo.setCurrentIndex( m-1 )
        cbo.currentIndexChanged.connect(self._monthChanged)

    def _yearChanged(self, newindex):
        print( "year changed to ", self._cboJahr.itemText( newindex ) )
        self.doZeitraumChangedCallback()

    def _monthChanged(self, newindex):
        print( "month changed to %s (index %d)" % (self._cboMonat.itemText( newindex ), newindex ))
        if( self._tm ):
            self._tm.setCheckmonat( newindex + 1 )
            top_cell = self._tm.index( 0, 0 )
            bottom_cell = self._tm.index( 0, 2 )
            self._tableView.dataChanged( top_cell, bottom_cell, [Qt.BackgroundRole,] )
            self._tableView.repaint()
            self.repaint()
        self.doZeitraumChangedCallback()

    def setZeitraum(self, jahr:int, monat:int ):
        """setzt Monat- und Jahr-Combo. Macht keinen Callback."""
        self._cboMonat.setCurrentIndex( monat-1 )
        self._cboJahr.setCurrentText( str( jahr ) )

    def doZeitraumChangedCallback(self):
        if self._zeitraumChangedCallback:
            d = self.getKontrollzeitraum()
            self._zeitraumChangedCallback( d["jahr"], d["monat"] )

    def setZeitraumChangedCallback( self, cb_fnc ):
        """
        function to be called on changes of month or year
        function signature: fnc( year, month )
        :param cb_fnc:
        :return:
        """
        self._zeitraumChangedCallback = cb_fnc

    def setModel(self, tm:CheckTableModel ) -> None:
        self._tableView.setModel( tm )
        c = tm.rowCount(self)
        okColumnIdx = tm.getOkColumnIdx()
        nokColumnIdx = tm.getNokColumnIdx()
        for r in range( tm.rowCount(self) ):
            btnOk = ControlButton( self, True, self._okButtonClicked )
            # btnOk.clicked.connect( self._okButtonClicked )
            btnNok = ControlButton( self, False, self._nokButtonClicked )
            # btnNok.clicked.connect(self._nokButtonClicked)
            self._tableView.setIndexWidget( tm.index( r, okColumnIdx ), btnOk )
            self._tableView.setIndexWidget( tm.index( r, nokColumnIdx ), btnNok )
        self._tableView.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tableView.resizeColumnsToContents()
        self._tm = tm

    def _okButtonClicked(self, checkstate:bool ):
        app = QApplication.instance()
        button:QPushButton = app.focusWidget()
        # or button = self.sender()
        index = self._tableView.indexAt(button.pos())
        if index.isValid():
            #print(index.row(), index.column())
            self._tm.setOkState( index, button.isChecked() )
        # ## TEST ##
        # idx = self._tm.index( 0, self._tm.columnCount()-1 )
        # self._tableView.scrollTo( idx )
        # idx = self._tm.index( 0, 3 )
        # self._tableView.scrollTo( idx )

    def _nokButtonClicked(self, checkstate: bool):
        def dlg_callback(ok: bool, value: float):
            print("ok: ", ok, " value: ", value)
            # or button = self.sender()
            if index.isValid():
                #print(index.row(), index.column())
                self._tm.setCheckMonatValue( index, value )
            return

        app = QApplication.instance()
        button: QPushButton = app.focusWidget()
        index = self._tableView.indexAt(button.pos())
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

    def getKontrollzeitraum(self) -> Dict:
        d = {}
        d["jahr"] = int( self._cboJahr.currentText() )
        d["monat"] = self._cboMonat.currentIndex() + 1
        return d

def test():
    app = QApplication()
    win = CheckView()

    rows = ({"Col 1": "1/0", "Col 2": 345,    "Col 3": "Ave Maria"},
            {"Col 1": "2/0", "Col 2": -123.45, "Col 3": "Summer in the City"},
            {"Col 1": "3/0", "Col 2": 776.45, "Col 3": "Winter in the Park"}
           )
    tm = CheckTableModel( [], 11 )

    win.setModel( tm )

    win.show()
    app.exec_()

if __name__ == "__main__":
    test()
