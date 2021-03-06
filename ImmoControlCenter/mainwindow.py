
from PySide2 import Qt
from PySide2.QtCore import *
#from PySide2.QtCore import QAbstractTableModel, SIGNAL
from PySide2.QtGui import QFont, QStandardItemModel, QStandardItem, QBrush, QColor, QIcon, QDoubleValidator
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QTableView, QPushButton, QDialog, QMessageBox
from PySide2 import QtWidgets
import datetime
from typing import List, Dict, Any
from models import KontrollModel
from monthlist import monthList

# monthList = ("Januar", "Februar", "März", "April", "Mai", "Juni",
#              "Juli", "August", "September", "Oktober", "November", "Dezember")

# def createTestModel():
#     tm = QStandardItemModel()
#     i1 = QStandardItem( "Abazid" )
#     i2 = QStandardItem( "550" )
#     i3 = QStandardItem( "ok" )
#     i4 = QStandardItem( "nok" )
#     i5 = QStandardItem( "510" )
#     itemlist = [i1, i2, i3, i4, i5]
#     tm.appendRow( itemlist )
#     i1 = QStandardItem("Zeiger")
#     i2 = QStandardItem("1050")
#     i3 = QStandardItem("ok")
#     i4 = QStandardItem("nok")
#     i5 = QStandardItem("1150")
#     itemlist = [i1, i2, i3, i4, i5]
#     tm.appendRow(itemlist)
#     return tm

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

################# ValueDialog ########################
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
    #
    # def reject(self):
    #     print( "reject" )
    #     if self._callback:
    #         self._callback( False, -1 )
    #     QDialog.reject( self )

################# CheckButton ########################
class ControlButton( QPushButton ):
    def __init__(self, parent, isOkButton:bool=True):
        QPushButton.__init__( self, parent )
        self.setText( "" )
        self._isOkButton:bool = isOkButton
        self._userdata:Any
        if isOkButton:
            self.setIcon( ImageFactory.instance().getOkIcon() )
        else:
            self.setIcon( ImageFactory.instance().getNokIcon() )

    def isOkButton(self) -> bool:
        return self._isOkButton

    def setUserData(self, userdata:Any ) -> None:
        self._userdata = userdata

################# MainWindow #########################
class MainWindow( QWidget ):
    def __init__(self):
        QWidget.__init__( self )
        self.setWindowTitle( "Immo Kontrollzentrum" )
        self._gridLayout_main:QtWidgets.QGridLayout = QtWidgets.QGridLayout( self )
        self._gridLayout:QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        self._combofont = QFont( "Arial", 14, weight=QFont.Bold);
        self._cboView:QComboBox #Mieter oder Wohnung
        self._cboJahr:QComboBox
        self._cboMonat:QComboBox
        self._mieteTableView:QTableView
        self._createUI()
        self._provideViewCombo()
        self._provideYearCombo()
        self._provideMonthCombo()
        # self._okIcon = QIcon( "./images/greensquare20x20.png" )
        # self._nokIcon = QIcon("./images/redsquare20x20.png")
        self._tm:KontrollModel = None
        # self._sollColumnIdx = 4
        # self._okColumnIdx = 5
        # self._nokColumnIdx = 6
        self._zeitraumChangedCallback = None
        self.resize(1800, 1280)

    def _createUI(self):
        self._gridLayout.setContentsMargins(3, 3, 3, 3)
        labelrow = 0
        widgetrow = 1
        lbl = QLabel( "Sicht" )
        self._gridLayout.addWidget(lbl, labelrow, 0, 1, 1, Qt.AlignHCenter)

        self._cboView = QComboBox(self)
        self._gridLayout.addWidget(self._cboView, widgetrow, 0, 1, 1, Qt.AlignHCenter)

        lbl = QLabel("Kontrollzeitraum")
        #self.gridLayout.addWidget(lbl, 0, 1, rowSpan=1, columnSpan=2, alignment=Qt.AlignHCenter )
        lbl.setAlignment( Qt.AlignCenter )
        self._gridLayout.addWidget(lbl, labelrow, 1, 1, 2)

        self._cboJahr = QComboBox( self )
        self._gridLayout.addWidget(self._cboJahr, widgetrow, 1, 1, 1)

        self._cboMonat = QComboBox(self)
        self._gridLayout.addWidget(self._cboMonat, widgetrow, 2, 1, 1)

        # add layout with comboboxes to main layout:
        self._gridLayout_main.addLayout( self._gridLayout, 0, 0, 1, 1 )

        # add MieteTableView to main layout
        tv = QTableView(self)
        tv.setAlternatingRowColors( True )
        tv.setStyleSheet( "alternate-background-color: lightgrey;" )
        #tv.setStyleSheet( "QHeaderView::section {background-color: red}" )
        self._gridLayout_main.addWidget( tv, 1, 0, 1, 1)

        # lbl = QLabel( "Summe Nettomieten")
        # self._gridLayout_main.addWidget(lbl, 1, 1, 1, 1)
        # lbl = QLabel( "9999" )
        # self._gridLayout_main.addWidget(lbl, 1, 2, 1, 1)


        self._mieteTableView = tv

    def _provideViewCombo(self):
        cbo = self._cboView
        cbo.setFont( self._combofont )
        cbo.addItem( "Mieten" )
        cbo.addItem( "Zahlungen mit/ohne Werterhaltung" )
        cbo.addItem( "Nebenkosten" )
        cbo.addItem( "Hausgeld" )
        cbo.addItem( "Stammdaten" )
        cbo.setCurrentIndex( 0 )
        cbo.currentIndexChanged.connect( self._viewChanged )

    def _provideYearCombo(self):
        y = datetime.datetime.now().year
        cbo = self._cboJahr
        cbo.setFont(self._combofont)
        for i in range(-2, 2):
            cbo.addItem(str(y + i))
        cbo.setCurrentIndex(2)
        cbo.currentIndexChanged.connect(self._yearChanged)

    def _provideMonthCombo(self):
        m = datetime.datetime.now().month
        cbo = self._cboMonat
        cbo.setFont(self._combofont)
        for mon in monthList:
            cbo.addItem( mon )
        cbo.setCurrentIndex( m-1 )
        cbo.currentIndexChanged.connect(self._monthChanged)

    def _viewChanged(self, newindex):
        print( "view changed to ", self._cboView.itemText( newindex ) )

    def _yearChanged(self, newindex):
        print( "year changed to ", self._cboJahr.itemText( newindex ) )
        self.doZeitraumChangedCallback()

    def _monthChanged(self, newindex):
        print( "month changed to %s (index %d)" % (self._cboMonat.itemText( newindex ), newindex ))
        self._tm.setCheckmonat( newindex + 1 )
        top_cell = self._tm.index( 0, 0 )
        bottom_cell = self._tm.index( 0, 2 )
        self._mieteTableView.dataChanged( top_cell, bottom_cell, [Qt.BackgroundRole,] )
        self._mieteTableView.repaint()
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

    def setZeitraumChangedCallback(self, cb_fnc):
        """
        function to be called on changes of month or year
        function signature: fnc( year, month )
        :param cb_fnc:
        :return:
        """
        self._zeitraumChangedCallback = cb_fnc

    def setMieteModel(self, tm:KontrollModel ) -> None:
        self._mieteTableView.setModel( tm )
        c = tm.rowCount(self)
        okColumnIdx = tm.getOkColumnIdx()
        nokColumnIdx = tm.getNokColumnIdx()
        for r in range( tm.rowCount(self) ):
            btnOk = ControlButton( self )
            btnOk.clicked.connect( self._okButtonClicked )
            btnNok = ControlButton( self, False )
            btnNok.clicked.connect(self._nokButtonClicked)
            self._mieteTableView.setIndexWidget( tm.index( r, okColumnIdx ), btnOk )
            self._mieteTableView.setIndexWidget( tm.index( r, nokColumnIdx ), btnNok )
        self._mieteTableView.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._mieteTableView.resizeColumnsToContents()
        self._tm = tm

    def _okButtonClicked(self, checkstate:bool ):
        app = QApplication.instance()
        button:QPushButton = app.focusWidget()
        # or button = self.sender()
        index = self._mieteTableView.indexAt(button.pos())
        if index.isValid():
            #print(index.row(), index.column())
            self._tm.setOkState( index, button.isChecked() )

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
        index = self._mieteTableView.indexAt(button.pos())
        dlg = ValueDialog( self )
        dlg.setCallback( dlg_callback )
        dlg.show()

    def getSicht(self) -> str:
        return self._cboView.currentText()

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

########### TEST #############################
from PySide2.QtWidgets import QApplication
from models import KontrollModel
from business import BusinessLogic

def main():
    app = QApplication()
    win = MainWindow()
    # busi = BusinessLogic()
    # busi.prepare()
    #
    # mietenDictList = [
    #     { "Mieter": "Abazid", "Soll": 590, "OK": "ok", "NOK": "nok", "Jan": 580, "Feb": 590 },
    #     { "Mieter": "Zeiger", "Soll": 590, "OK": "ok", "NOK": "nok", "Jan": 580, "Feb": 590}
    # ]
    #
    # mm = KontrollModel( win, mietenDictList, 10 )
    # rc = mm.rowCount( win )
    # win.setTableViewModel( mm )

    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
