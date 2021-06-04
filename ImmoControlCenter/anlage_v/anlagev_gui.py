from typing import List

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt, QSize, QModelIndex, Signal
from PySide2.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QPushButton, QWidget, QHBoxLayout, QApplication, QTableView, QTabWidget, QDialog, \
    QComboBox, QListView, QVBoxLayout

from anlage_v.anlagev_tablemodel import AnlageVTableModel
from imagefactory import ImageFactory


class AnlageVAuswahlDialog( QDialog ):
    def __init__( self, masterobjektlist:List[str], jahre:List[int], checked=False, icon=None, parent=None ):
        QDialog.__init__( self, parent )
        self.icon = icon
        self._jahre = jahre
        self.cboJahr = QComboBox()
        self.listView = QListView()
        self.okButton = QPushButton( "OK" )
        self.cancelButton = QPushButton( "Abbrechen" )
        self.selectButton = QPushButton( "Alle auswählen" )
        self.unselectButton = QPushButton( "Auswahl aufheben" )
        self.font = QFont( "Arial", 14 )
        self.model = QStandardItemModel()
        self.choices:List[str] = list()
        self._createGui()
        self._setJahrItems()
        self._createModel( masterobjektlist, checked )

    def _createGui( self ):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        h2box = QHBoxLayout()
        h2box.addStretch( 1 )
        h2box.addWidget(self.selectButton)
        h2box.addWidget(self.unselectButton)

        vbox = QVBoxLayout(self)
        self.cboJahr.setMaximumWidth( 100 )
        vbox.addWidget( self.cboJahr )
        vbox.addLayout( h2box )
        vbox.addWidget(self.listView, stretch=1)
        #vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.okButton.setDefault( True )

        self.setWindowTitle( "Auswahl von Objekten" )
        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def _setJahrItems( self ):
        jahre = [str( x ) for x in self._jahre]
        if len( jahre ) > 0:
            self.cboJahr.addItems( jahre )
            self.cboJahr.setCurrentText( jahre[0] )

    def _createModel( self, masterobjektList:List[str], checked:bool ):
        for obj in masterobjektList:
            item = QStandardItem( obj )
            item.setCheckable(True)
            item.setFont( self.font )
            check = (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)
        self.listView.setModel( self.model )

    def setCurrentJahr( self, jahr:int ) -> None:
        sjahr = str( jahr )
        self.cboJahr.setCurrentText( sjahr )

    def getAuswahl( self ) -> (int, List[str]):
        """
        liefert das eingestellte Jahr und die Liste der ausgewählten Objekte
        :return:
        """
        return int( self.cboJahr.currentText() ), self.choices

    def onAccepted(self):
        self.choices = [self.model.item(i).text() for i in  range(self.model.rowCount() )
                        if self.model.item(i).checkState() == QtCore.Qt.Checked]
        self.accept()

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)


###################################################################

class AnlageVTabs( QTabWidget ):
    def __init__( self, parent=None ):
        QTabWidget.__init__( self, parent )

###################################################################

class AnlageVTableView( QTableView ):
    cell_clicked = Signal( str, int, int, int )
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        self.clicked.connect( self._onLeftClick )

    def _onLeftClick( self, item:QModelIndex ):
        tm:AnlageVTableModel = self.model()
        self.cell_clicked.emit( tm.getMasterName(), tm.getJahr(), item.row(), item.column() )

###################################################################

class ToolbarButton( QPushButton ):
    # def __init__( self, parent, size:QSize, pathToIcon:str, tooltip:str ):
    def __init__( self, parent, size: QSize, icon: QIcon, tooltip: str ):
        QPushButton.__init__( self, parent )
        self._icon = icon
        self.setFlat( True )
        self.setFixedSize( size )
        #icon = QIcon( pathToIcon )
        self.setIcon( icon )
        self.setIconSize( size )
        self.setToolTip( tooltip )

###################################################################

class AnlageVView( QWidget ):
    openAnlageV = Signal()
    printAnlageV = Signal()
    printAllAnlageV = Signal()
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self.setWindowTitle( "Anlage V" )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._btnOpenAnlageV = ToolbarButton( self, QSize( 30, 30 ),
                                        ImageFactory.inst().getOpenIcon(), "Anlage V öffnen" )
        self._btnPrint = ToolbarButton( self, QSize( 30, 30 ),
                                        ImageFactory.inst().getPrintIcon(), "Aktive Anlage V drucken" )
        self._btnPrintAll = ToolbarButton( self, QSize( 30, 30 ),
                                           ImageFactory.inst().getPrintAllIcon(), "Alle geöffneten Anlagen V drucken" )
        self._btnClose = QPushButton( text="Schließen" )
        self._tabs:AnlageVTabs() = AnlageVTabs()
        self._tvList:List[AnlageVTableView] = list()
        self._createGui()

    def _createGui( self ):
        self._createToolbar()
        self._toolbarLayout.setStretch( 2, 1 )
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._mainLayout.addWidget( self._tabs, 1, 0 )
        self.setLayout( self._mainLayout )

    def _createToolbar( self ):
        self._btnOpenAnlageV.clicked.connect( self._onOpen )
        self._toolbarLayout.addWidget( self._btnOpenAnlageV, alignment=Qt.AlignLeft )
        self._btnPrint.clicked.connect( self._onPrint )
        self._toolbarLayout.addWidget( self._btnPrint, alignment=Qt.AlignLeft )
        self._btnPrintAll.clicked.connect( self._onPrintAll )
        self._toolbarLayout.addWidget( self._btnPrintAll, alignment=Qt.AlignLeft )
        self._btnClose.clicked.connect( self._onClose )
        self._toolbarLayout.addWidget( self._btnClose, alignment=Qt.AlignRight )


    def addAnlageV( self, tm:AnlageVTableModel ) -> AnlageVTableView:
        tv = AnlageVTableView()
        tv.setModel( tm )
        tv.resizeColumnsToContents()
        self._tabs.addTab( tv, tm.getMasterName() )
        self._tvList.append( tv )
        return tv

    def _onOpen( self ):
        #print( "AnlageVView._onOpen")
        self.openAnlageV.emit()

    def _onPrint( self ):
        print( "AnlageVView._onPrint" )

    def _onPrintAll( self ):
        print( "AnlageVView._onPrintAll" )

    def _onClose( self ):
        self.close()


# class AnlageVDialog( QDialog ):
#     def __init__( self, parent=None ):
#         QDialog.__init__( self, parent )
#         self._layout = QVBoxLayout()
#         #self._btnPrint = ToolbarButton( self, QSize( 30, 30 ), "../images/print_30.png", "Anlagen V drucken" )
#         #self._btnDummy = QPushButton( text="PUSH")
#         self._view = AnlageVView()
#         self._createGui()
#
#     def _createGui( self ):
#         self.setWindowTitle( "Anlagen V ausgewählter Objekte" )
#         #self._layout.addWidget( self._btnDummy )
#         self._layout.addWidget( self._view, stretch=1 )
#         self.setLayout( self._layout )

def test():
    app = QApplication()
    # dlg = AnlageVAuswahlDialog( ["SB_Kaiser", "ILL_Eich", "NK_Kleist"], [2020, 2021], checked=True )
    # dlg.setCurrentJahr( 2021 )
    # if dlg.exec_() == QDialog.Accepted:
    #     print( '\n'.join( [str( s ) for s in dlg.getAuswahl()] ) )

    v = AnlageVView()
    v.show()

    #d = AnlageVDialog()
    #d.exec_()

    app.exec_()

if __name__ == "__main__":
    test()