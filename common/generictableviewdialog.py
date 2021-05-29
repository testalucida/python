from PySide2 import QtWidgets
from PySide2.QtCore import QAbstractTableModel, Qt
from PySide2.QtWidgets import QDialog, QPushButton, QTableView, QGridLayout, QApplication, QHBoxLayout


class GenericTableView(QTableView):
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )

class GenericTableViewDialog( QDialog ):
    def __init__( self, model:QAbstractTableModel=None, parent=None ):
        QDialog.__init__( self, parent )
        self._layout = QGridLayout( self )
        self._okButton = QPushButton( "OK" )
        self._cancelButton = QPushButton( "Abbrechen" )
        self._tv = GenericTableView( self )
        self._createGui()
        self.setModal( True )
        if model:
            self.setTableModel( model )

    def _createGui( self ):
        self._okButton.clicked.connect( self.accept )
        self._cancelButton.clicked.connect( self.reject )
        hbox = QHBoxLayout()
        hbox.addWidget( self._okButton )
        hbox.addWidget( self._cancelButton )

        self._layout.addWidget( self._tv, 1, 0)
        self._layout.addLayout( hbox, 2, 0 )
        self.setLayout( self._layout )

    def setCancelButtonVisible( self, visible:bool=True ):
        self._cancelButton.setVisible( False )

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def setTableModel( self, model:QAbstractTableModel ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()

def test():
    class TestModel( QAbstractTableModel ):
        def __init__( self ):
            QAbstractTableModel.__init__( self )
            self._rows = [("00", "01", "02"),
                          ("10", "11", "12"),
                          ("20", "21", "22"),
                          ("30", "31", "32")]

        def rowCount( self, parent=None ):
            return 4

        def columnCount( self, parent=None ):
            return 3

        def data( self, index, role=None ):
            if not index.isValid():
                return None
            if role == Qt.DisplayRole:
                return self._rows[index.row()][index.column()]
            return None

        def headerData( self, col, orientation, role=None ):
            if orientation == Qt.Horizontal:
                if role == Qt.DisplayRole:
                    return "Spalte %d" % col
                if role == Qt.BackgroundRole:
                    pass
                    # if self.headerBrush:
                    #     return self.headerBrush
            return None

    app = QApplication()
    tm = TestModel()
    dlg = GenericTableViewDialog()
    dlg.setTableModel( tm )
    dlg.setCancelButtonVisible( False )
    dlg.setOkButtonText( "Schließen" )
    dlg.show()
    app.exec_()

if __name__ == "__main__":
    test()