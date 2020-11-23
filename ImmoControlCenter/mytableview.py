import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableView, \
    QAbstractScrollArea, QAbstractItemView

class TestWindow( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self.tableView = MyTableView()
        self.btn = QPushButton( "First Column fix" )
        self.btn.clicked.connect( self.onClick )
        layout = QVBoxLayout()
        layout.addWidget( self.tableView )
        layout.addWidget( self.btn )
        self.setLayout( layout )
        self.resize( 500, 400 )

    def onClick( self ):
        self.tableView.freezeColumns( 1 )

#####################################################
class TestModel( QAbstractTableModel ):
    def __init__(self):
        QAbstractTableModel.__init__( self )

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return 100

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return 20

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            val = str( index.row() ) + " / " + str( index.column() )
            return val

        return None

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return "Column: " + str( section )
            if role == Qt.BackgroundRole:
                return None
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return str( section + 1 )
        return None

    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        """sort table by given column number col"""
        self.emit(SIGNAL(b"layoutAboutToBeChanged()"))
        sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        self._rowlist = sorted(self._rowlist, key=lambda x: x[self._headers[col]], reverse=sort_reverse )
        self.emit(SIGNAL(b"layoutChanged()"))

#######################################################################
class MyTableView( QTableView ):
    def __init__( self ):
        QTableView.__init__( self )
        self.frozen:QTableView = None
        # hh = self.horizontalHeader()
        # hh.setDefaultAlignment( Qt.AlignCenter )
        # hh.setVisible( True )

    def _setupFrozenView( self ):
        self.frozen = QTableView( self )
        self.frozen.setModel( self.model() )
        self.frozen.verticalHeader().hide()
        self.frozen.setSelectionModel( self.selectionModel() )  ##QAbstractItemView.selectionModel( self ) )
        self.frozen.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.frozen.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.frozen.verticalHeader().setDefaultSectionSize( self.verticalHeader().defaultSectionSize() )
        self.frozen.setColumnWidth( 0, self.columnWidth( 0 ) )
        for col in range( 1, self.model().columnCount() ):
            print( "col: ", col )
            self.frozen.setColumnHidden( col, True )
        self.viewport().stackUnder( self.frozen )
        self._updateFrozenTableGeometry()
        self.frozen.show()

    def freezeColumns( self, nLeftColumns:int ):
        self._setupFrozenView()

    def _updateFrozenTableGeometry(self):
        if self.verticalHeader().isVisible():
            self.frozen.setGeometry(self.verticalHeader().width() + self.frameWidth(),
                                    self.frameWidth(), self.columnWidth(0),
                                    self.viewport().height() + self.horizontalHeader().height())
        else:
            self.frozen.setGeometry(self.frameWidth(),
                                    self.frameWidth(), self.columnWidth(0),
                                    self.viewport().height() + self.horizontalHeader().height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWindow()
    model = TestModel()
    w.tableView.setModel( model )
    #w.tableView.freezeColumns( 1 )
    w.show()
    sys.exit(app.exec_())