

from customtable_stuff.customtableview import CustomTableView
from qt_imports import *

class CustomTableViewDialog( QDialog ):
    """
    Dialog für eine CustomTableView.
    Wenn die TableView editierbar sein soll (isEditable=True), werden unterhalb der View
    3 Buttons zur Neunanlage, Bearbeitung bzw. Löschung einer Tabellenzeile angeboten.
    Bei Drücken von OK oder Cancel wird ein entsprechendes Signal gesendet.
    Die Methoden accept() und reject() müssen nach der Signalbehandlung explizit aufgerufen werden.
    """
    createItem = Signal()
    editItem = Signal( QModelIndex )
    deleteItem = Signal( QModelIndex )
    okPressed = Signal()
    cancelPressed = Signal()

    def __init__( self, model:QAbstractTableModel=None, isEditable:bool=False, parent=None ):
        QDialog.__init__( self, parent )
        self._isEditable = isEditable
        self._layout = QGridLayout( self )
        #self._imagePath =
        self._okButton = QPushButton( "OK" )
        self._cancelButton = QPushButton( "Abbrechen" )
        if isEditable:
            #path = ROOT_DIR
            iconpath = os.getcwd() + "/images/"
            iconfactory = IconFactory()
            self._newButton = QPushButton()
            icon = iconfactory.getIcon( iconpath + "plus_30x30.png" )
            self._newButton.setIcon( icon )
            self._newButton.setToolTip( "Neuen Tabelleneintrag anlegen" )

            self._editButton = QPushButton()
            icon = iconfactory.getIcon( iconpath + "edit.png" )
            self._editButton.setIcon( icon )
            self._editButton.setToolTip( "Ausgewählten Tabelleneintrag bearbeiten" )

            self._deleteButton = QPushButton()
            icon = iconfactory.getIcon( iconpath + "cancel.png" )
            self._deleteButton.setIcon( icon )
            self._deleteButton.setToolTip( "Ausgewählten Tabelleneintrag löschen" )

        self._tv = CustomTableView( self )
        self._createGui()
        self.setModal( True )
        if model:
            self.setTableModel( model )

    def _createGui( self ):
        if self._isEditable:
            self._createEditButtons()
        self._okButton.clicked.connect( self.okPressed.emit )
        self._cancelButton.clicked.connect( self.cancelPressed.emit )
        hbox = QHBoxLayout()
        hbox.addWidget( self._okButton )
        hbox.addWidget( self._cancelButton )

        self._tv.horizontalHeader().setStretchLastSection( True )
        self._layout.addWidget( self._tv, 1, 0)
        self._layout.addLayout( hbox, 3, 0, alignment=Qt.AlignLeft )
        self.setLayout( self._layout )

    def _createEditButtons( self ):
        self._newButton.clicked.connect( self._onNew )
        self._editButton.clicked.connect( self._onEdit )
        self._deleteButton.clicked.connect( self._onDelete )
        hbox = QHBoxLayout()
        hbox.addWidget( self._newButton )
        hbox.addWidget( self._editButton )
        hbox.addWidget( self._deleteButton )
        self._layout.addLayout( hbox, 2, 0, alignment=Qt.AlignLeft )

    def setCancelButtonVisible( self, visible:bool=True ):
        self._cancelButton.setVisible( False )

    def setOkButtonText( self, text:str ):
        self._okButton.setText( text )

    def setTableModel( self, model:QAbstractTableModel, selectRows:bool=True, singleSelection:bool=True ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()
        self._tv.setSelectionBehavior( QTableView.SelectRows )
        self._tv.setSelectionMode( QAbstractItemView.SingleSelection )
        if self._isEditable:
            self._newButton.setFocus()
        else:
            self._okButton.setFocus()

    def _onNew( self ):
        self.createItem.emit()

    def _onEdit( self ):
        indexlist = self._tv.getSelectedIndexes()
        if len( indexlist ) > 0:
            self.editItem.emit( indexlist[0] )

    def _onDelete( self ):
        indexlist = self._tv.getSelectedIndexes()
        if len( indexlist ) > 0:
            self.deleteItem.emit( indexlist[0] )

    def getTableView( self ) -> CustomTableView:
        return self._tv