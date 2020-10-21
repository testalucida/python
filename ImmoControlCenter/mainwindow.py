
from PySide2 import Qt

from PySide2.QtCore import *
#from PySide2.QtCore import QAbstractTableModel, SIGNAL
from PySide2.QtGui import QFont, QStandardItemModel, QStandardItem, QBrush, QColor, QIcon
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QTableView, QPushButton
from PySide2 import QtWidgets
import datetime
from typing import List, Dict


monthList = ("Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember")

def createTestModel():
    tm = QStandardItemModel()
    i1 = QStandardItem( "Abazid" )
    i2 = QStandardItem( "550" )
    i3 = QStandardItem( "ok" )
    i4 = QStandardItem( "nok" )
    i5 = QStandardItem( "510" )
    itemlist = [i1, i2, i3, i4, i5]
    tm.appendRow( itemlist )
    i1 = QStandardItem("Zeiger")
    i2 = QStandardItem("1050")
    i3 = QStandardItem("ok")
    i4 = QStandardItem("nok")
    i5 = QStandardItem("1150")
    itemlist = [i1, i2, i3, i4, i5]
    tm.appendRow(itemlist)
    return tm



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
        self._okIcon = QIcon( "./images/greensquare20x20.png" )
        self._nokIcon = QIcon("./images/redsquare20x20.png")
        self._tm:KontrollModel = None

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

    def _monthChanged(self, newindex):
        print( "month changed to %s (index %d)" % (self._cboMonat.itemText( newindex ), newindex ))
        self._tm.setCheckmonat( newindex + 1 )
        top_cell = self._tm.index( 0, 0 )
        bottom_cell = self._tm.index( 0, 2 )
        self._mieteTableView.dataChanged( top_cell, bottom_cell, [Qt.BackgroundRole,] )
        self._mieteTableView.repaint()
        self.repaint()

    def setMieteModel(self, tm:QAbstractTableModel ) -> None:
        self._mieteTableView.setModel( tm )
        c = tm.rowCount(self)
        for r in range( tm.rowCount(self) ):
            btnOk = QPushButton( "" )
            btnOk.setIcon( self._okIcon )
            btnOk.setCheckable( True )
            btnNok = QPushButton( "" )
            btnNok.setIcon( self._nokIcon )
            btnOk.setCheckable( True )
            self._mieteTableView.setIndexWidget( tm.index( r, 5 ), btnOk )
            self._mieteTableView.setIndexWidget( tm.index( r, 6 ), btnNok )
            #self._mieteTableView.setItemDelegateForColumn( 3, self._namecolumnddelegate )
        self._mieteTableView.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._mieteTableView.resizeColumnsToContents()
        self._tm = tm

    def getView(self) -> str:
        return self._cboView.currentText()

    def getKontrollzeitraum(self) -> Dict:
        d = {}
        d["jahr"] = int( self._cboJahr.currentText() )
        d["monat"] = self._cboMonat.currentIndex() + 1
        return d

########### TEST
from PySide2.QtWidgets import QApplication
from models import KontrollModel
from business import BusinessLogic

def main():
    app = QApplication()
    win = MainWindow()
    busi = BusinessLogic()
    busi.prepare()

    mietenDictList = [
        { "Mieter": "Abazid", "Soll": 590, "OK": "ok", "NOK": "nok", "Jan": 580, "Feb": 590 },
        { "Mieter": "Zeiger", "Soll": 590, "OK": "ok", "NOK": "nok", "Jan": 580, "Feb": 590}
    ]

    mm = KontrollModel( win, mietenDictList )
    rc = mm.rowCount( win )
    win.setTableViewModel( mm )

    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
