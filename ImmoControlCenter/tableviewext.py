import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTableView, QHeaderView

class TestWindow( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self.tableView = TableViewExt()
        self.btn = QPushButton( "First Column fix" )
        self.btn.clicked.connect( self.onClick )
        self.btnReset = QPushButton( "Unfix first Column" )
        self.btnReset.clicked.connect( self.onClickReset )
        layout = QVBoxLayout()
        layout.addWidget( self.tableView )
        layout.addWidget( self.btn )
        layout.addWidget( self.btnReset )
        self.setLayout( layout )
        self.resize( 500, 400 )

    def onClick( self ):
        self.tableView.freezeColumns( 1 )

    def onClickReset( self ):
        self.tableView.resetFrozen()

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
class TableViewExt( QTableView ):
    def __init__( self ):
        QTableView.__init__( self )
        self._frozen:QTableView = None  # tableview containing only frozen columns
        self._nFrozen = 0  # number of frozen left columns

    def setModel( self, model:QAbstractTableModel ) -> None:
        super().setModel( model )
        if self._nFrozen > 0:
            self._setupFrozenView()

    def _setupFrozenView( self ):
        self._frozen = QTableView( self )
        self._frozen.setModel( self.model() )
        self._frozen.verticalHeader().hide()
        self._frozen.horizontalHeader().setSectionResizeMode( QHeaderView.Fixed )
        self._frozen.setSelectionModel( self.selectionModel() )  ##QAbstractItemView.selectionModel( self ) )
        self._frozen.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self._frozen.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        #self._frozen.verticalHeader().setDefaultSectionSize( self.verticalHeader().defaultSectionSize() )
        #self._frozen.setStyleSheet( "border: none; background-color: #d1d8d8" )
        # make columns to freeze (i.e. columns to be seen in self.frozen)
        # of same width as in the original tableview
        for n in range( self._nFrozen ):
            self._frozen.setColumnWidth( n, self.columnWidth( n ) )
        for col in range( self._nFrozen, self.model().columnCount() ):
            self._frozen.setColumnHidden( col, True )
        self.viewport().stackUnder( self._frozen )
        self._updateFrozenTableGeometry()
        # connect the headers and scrollbars of both tableviews together
        #self._frozen.horizontalHeader().sectionResized.connect( self._updateSectionWidth )
        self.horizontalHeader().sectionResized.connect( self._updateFrozenSectionWidth )
        self.verticalHeader().sectionResized.connect( self._updateFrozenSectionHeight )
        #self._frozen.verticalScrollBar().valueChanged.connect( self.verticalScrollBar().setValue )
        self.verticalScrollBar().valueChanged.connect( self._frozen.verticalScrollBar().setValue )
        self._frozen.show()

    def resetFrozen( self ):
        if self._frozen:
            self._frozen.hide()
            #self._frozen.verticalScrollBar().valueChanged.disconnect( self.verticalScrollBar().setValue )
            self.verticalScrollBar().valueChanged.disconnect( self._frozen.verticalScrollBar().setValue )
            self._frozen.destroy()
            self._frozen = None
            self._nFrozen = 0
            self.horizontalHeader().sectionResized.disconnect( self._updateFrozenSectionWidth )
            self.verticalHeader().sectionResized.disconnect( self._updateFrozenSectionHeight )

    def freezeColumns( self, nLeftColumns:int ):
        if nLeftColumns == self._nFrozen and self._frozen:
            # nothing to do
            return
        if nLeftColumns != self._nFrozen:
            # before any furter action reset frozen tableview
            self.resetFrozen()
        if nLeftColumns == 0:
            # we're done
            return
        self._nFrozen = nLeftColumns
        if self.model():
            self._setupFrozenView()

    def _updateFrozenTableGeometry(self):
        width = 0
        for n in range( self._nFrozen ):
            width += self.columnWidth( n )
        if self.verticalHeader().isVisible():
            self._frozen.setGeometry( self.verticalHeader().width() + self.frameWidth() - 1,
                                      self.frameWidth() - 1,
                                      width,  #self.columnWidth(0),
                                      self.viewport().height() + self.horizontalHeader().height() )
        else:
            self._frozen.setGeometry( self.frameWidth(),
                                      self.frameWidth() - 1,
                                      width, #self.columnWidth(0),
                                      self.viewport().height() + self.horizontalHeader().height() )

    def _updateFrozenSectionWidth( self, logicalIndex, oldSize, newSize ):
        #print( "updateSectionWidth: logicalIndex=%d, oldsize=%d, newsize=%d" % (logicalIndex, oldSize, newSize) )
        if logicalIndex == 0:
            self._frozen.setColumnWidth( logicalIndex, newSize )
            self._updateFrozenTableGeometry()

    def _updateFrozenSectionHeight( self, logicalIndex, oldSize, newSize ):
        self._frozen.setRowHeight( logicalIndex, newSize )

    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        if self._frozen:
            self._updateFrozenTableGeometry()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TestWindow()
    model = TestModel()
    w.tableView.setModel( model )
    #w.tableView.freezeColumns( 1 )
    w.show()
    sys.exit(app.exec_())