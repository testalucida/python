import numbers
from typing import Any, List, Tuple

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QDate, Qt, QAbstractTableModel, QRect, Signal, QPoint, QModelIndex
from PySide6.QtGui import QDoubleValidator, QIntValidator, QFont, QGuiApplication, QStandardItemModel, QStandardItem, \
    QMouseEvent, QTextDocument, QKeySequence
from PySide6.QtWidgets import QDialog, QCalendarWidget, QVBoxLayout, QBoxLayout, QLineEdit, QGridLayout, QPushButton, \
    QHBoxLayout, QApplication, QListView, QComboBox, QLabel, QTextEdit, QCheckBox, QTableView, QWidget

from datehelper import isValidIsoDatestring, isValidEurDatestring, getRelativeQDate, getQDateFromIsoString


######################  TableView ##################################
class TableView( QTableView ):
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        self._frozen:QTableView = None  # tableview containing only frozen columns
        #self._frozenContextMenu:TableCellActionHandler = None
        self._nFrozen = 0  # number of frozen left columns
        self.clicked.connect( self.onLeftClick )
        # self.setMouseTracking( True )
        # self.setContextMenuPolicy( Qt.CustomContextMenu )
        # self.customContextMenuRequested.connect( self.onRightClick )
        self._copycallback = None

    def setCopyCallback( self, callbackFnc ):
        self._copycallback = callbackFnc

    def keyPressEvent( self, event ):
        if event.matches( QKeySequence.Copy ):
            if self._copycallback:
                self._copycallback()
        if event.matches( QKeySequence.Paste ):
            pass
        QTableView.keyPressEvent( self, event )

    def setModel( self, model:QAbstractTableModel ) -> None:
        super().setModel( model )
        if self._nFrozen > 0:
            self._setupFrozenView()

    def setSortingEnabled( self, on:bool ):
        #self.horizontalHeader().setSortIndicator( -1, Qt.AscendingOrder ) # no effect
        super().setSortingEnabled( on )
        if self._frozen:
            self._frozen.setSortingEnabled( on )

    def onLeftClick( self, index: QModelIndex ):
        # if index.column() == 2:
        #     self.setStyleSheet( "QTableView::item:selected:active { background: #ff0000;}" )
        # else:
        #     self.setStyleSheet( "" )
        #val = self.model().data( index, Qt.DisplayRole )
        #print( "index %d/%d clicked. Value=%s" % (index.row(), index.column(), str( val )) )
        pass

    def onRightClick( self, point: QPoint ):
        print( "TableViewExt: onRightClick" )
        #TEST
        # index = self.indexAt( point )
        # row = index.row()
        # if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
        # addNumbersAction = QAction( "Addiere selektierte Zahlen" )
        # menu = QMenu()
        # menu.addAction( addNumbersAction )
        # action = menu.exec_( self.viewport().mapToGlobal( point ) )

    def setAlternatingRowColors( self, on:bool ):
        super().setAlternatingRowColors( on )
        if self._frozen:
            self._frozen.setAlternatingRowColors( on )

    def setIndexWidget( self, index:QModelIndex, widget:QWidget ):
        super().setIndexWidget( index, widget )
        if index.column() < self._nFrozen:
            wcopy = self.getCopyOfIndexWidget( widget, index )
            self._frozen.setIndexWidget( index, wcopy )


    def _setupFrozenView( self ):
        self._frozen = QTableView( self )
        self._frozen.setModel( self.model() )
        self._copyIndexWidgets()
        self._frozen.verticalHeader().hide()
        self._frozen.setSortingEnabled( self.isSortingEnabled() )
        self._frozen.setAlternatingRowColors( self.alternatingRowColors() )
        #self._frozen.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self._frozen.setSelectionModel( self.selectionModel() )  ##QAbstractItemView.selectionModel( self ) )
        self._frozen.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self._frozen.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self._frozen.setStyleSheet( "border: none; background-color: #fffff6" )
        # make columns to freeze (i.e. columns to be seen in self.frozen)
        # of same width as in the original tableview
        for n in range( self._nFrozen ):
            self._frozen.setColumnWidth( n, self.columnWidth( n ) )
        for col in range( self._nFrozen, self.model().columnCount() ):
            self._frozen.setColumnHidden( col, True )
        self.viewport().stackUnder( self._frozen )
        self._updateFrozenTableGeometry()
        # connect the headers and scrollbars of both tableviews together
        self._frozen.horizontalHeader().sectionResized.connect( self._updateOrigSectionWidth )
        self.horizontalHeader().sectionResized.connect( self._updateFrozenSectionWidth )
        self.verticalHeader().sectionResized.connect( self._updateFrozenSectionHeight )
        self._frozen.verticalScrollBar().valueChanged.connect( self.verticalScrollBar().setValue )
        self.verticalScrollBar().valueChanged.connect( self._frozen.verticalScrollBar().setValue )
        #self._frozenContextMenu = TableCellActionHandler( self )
        # initialize ContextMenu of frozen tableview
        self._frozen.setMouseTracking( True )
        self._frozen.setContextMenuPolicy( Qt.CustomContextMenu )
        self._frozen.customContextMenuRequested.connect( self.onRightClickFrozen )
        self._frozen.show()

    def onRightClickFrozen( self, point:QPoint ):
        # may be overridden in a derived class
        pass

    def resetFrozen( self ):
        if self._frozen:
            self._frozen.hide()
            self._frozen.horizontalHeader().sectionResized.disconnect( self._updateOrigSectionWidth )
            self._frozen.verticalScrollBar().valueChanged.disconnect( self.verticalScrollBar().setValue )
            self.verticalScrollBar().valueChanged.disconnect( self._frozen.verticalScrollBar().setValue )
            self._frozen.reset()
            self._frozen.destroy()
            self._frozen = None
            self._nFrozen = 0
            self.horizontalHeader().sectionResized.disconnect( self._updateFrozenSectionWidth )
            self.verticalHeader().sectionResized.disconnect( self._updateFrozenSectionHeight )

    def _copyIndexWidgets( self ):
        model = self.model()
        rows = model.rowCount()
        cols = model.columnCount()
        for r in range( rows ):
            for c in range( self._nFrozen ):
                idx = model.index( r, c )
                widget = self.indexWidget( idx )
                if widget:
                    w = self._frozen.indexWidget( idx )
                    if not w:
                        w = self.getCopyOfIndexWidget( widget, idx )
                        self._frozen.setIndexWidget( idx, w )

    def getCopyOfIndexWidget( self, oldwidget:QWidget, idx:QModelIndex ) -> None:
        """
        override this method to provide the appropriate widget at index idx.
        Only needed when working with frozen columns where index widgets are placed
        in the frozen area.
        """
        return None

    def setColumnsFrozen( self, nLeftColumns:int ):
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

    def _updateOrigSectionWidth( self, logicalIndex, oldSize, newSize ):
        if logicalIndex < self._nFrozen:
            self.setColumnWidth( logicalIndex, newSize )

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
        if logicalIndex < self._nFrozen:
            self._frozen.setColumnWidth( logicalIndex, newSize )
            self._updateFrozenTableGeometry()

    def _updateFrozenSectionHeight( self, logicalIndex, oldSize, newSize ):
        self._frozen.setRowHeight( logicalIndex, newSize )

    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        if self._frozen:
            self._updateFrozenTableGeometry()

######################  CalendarDialog ##################################
class CalendarDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__(self, parent)
        self.setModal( True )
        self.setTitle( "Datum auswählen" )
        self._calendar:QCalendarWidget = None
        self._buchungsjahrChangedCallback = None

        self._buttonBox:QtWidgets.QDialogButtonBox = None
        self._callback = None
        self.createCalendar()

    def setTitle( self, title:str ) -> None:
        self.setWindowTitle( title )

    def setCallback( self, cbfnc ):
        self._callback = cbfnc

    def setMinimumDate( self, y:int, m:int, d:int ):
        self._calendar.setMinimumDate( QDate( y, m, d ) )

    def setMaximumDate( self, y:int, m:int, d:int ):
        self._calendar.setMaximumDate( QDate( y, m, d ) )

    def createCalendar(self):
        vbox = QVBoxLayout()
        self._calendar = QCalendarWidget()
        self._calendar.setGridVisible( True )
        self._calendar.setFirstDayOfWeek( Qt.Monday )
        vbox.addWidget( self._calendar )
        self.setLayout(vbox)

        self._buttonBox = QtWidgets.QDialogButtonBox( self )
        self._buttonBox.setOrientation( QtCore.Qt.Horizontal )
        self._buttonBox.setStandardButtons( QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel )
        self._buttonBox.layout().setDirection( QBoxLayout.RightToLeft )
        self._buttonBox.button( QtWidgets.QDialogButtonBox.Ok ).clicked.connect( self._onOk )
        self._buttonBox.button( QtWidgets.QDialogButtonBox.Cancel ).clicked.connect( self._onCancel )
        vbox.addWidget( self._buttonBox )

    def setSelectedDate( self, date:QDate ):
        self._calendar.setSelectedDate( date )

    def setSelectedDateFromString( self, datestring:str ):
        """
        datestring needs to be given as "yyyy-mm-dd" or "dd.mm.yyyy"
        day and month may be given one-digit.
        :param datestring:
        :return:
        """
        parts = datestring.split( "-" )
        if len( parts ) == 0:
            parts = datestring.split( "." )
        else: # yyyy-mm-dd
            dt = QDate( int(parts[0]), int(parts[1]), int(parts[2]) )
            self.setSelectedDate( dt )
        if len( parts ) == 0:
            raise Exception( "CalendarDialog.setSelectedDateFromString: wrong date format '%s'"
                             % (datestring) )
        else: # dd.mm.yyyy
            dt = QDate( int( parts[2] ), int( parts[1] ), int( parts[0] ) )
            self.setSelectedDate( dt )

    def _onOk( self ):
        date:QDate =  self._calendar.selectedDate()
        self.hide()
        if self._callback:
            self._callback( date )

    def _onCancel( self ):
        self.hide()

#########################  SmartDateEdit  #####################################
class SmartDateEdit( QLineEdit ):
    def __init__( self, parent=None ):
        QLineEdit.__init__( self, parent )

    def mouseDoubleClickEvent( self, event ):
        #print( "Double Click SmartDateEdit at pos: ", event.pos() )
        self.showCalendar()

    def setDate( self, year:int, month:int, day:int, format:str="yyyy-MM-dd" ):
        dt = QDate( year, month, day )
        ds = dt.toString( format )
        self.setText( ds )

    def setDateFromIsoString( self, isostring:str ):
        self.setText( isostring )

    def getDate( self ) -> str:
        """
        liefert das eingestellte Datum in dem Format, wie es im Feld zu sehen ist.
        Ist der Wert im Feld ungültig, wird ein Leerstring ("") zurückgegeben.
        :param format:
        :return:
        """
        ds = self.text()
        if ds.endswith( "\n" ): ds = ds[:-1]
        if isValidIsoDatestring( ds ) or isValidEurDatestring( ds ):
            return ds
        else:
            return ""

    def isDateValid( self ) -> bool:
        """
        Prüft, ob der String im Edit-Feld ein gültiges Datum darstellt (True) oder nicht (False).
        Ein leeres Feld gilt als "gültig" (True)
        :return:
        """
        ds = self.text()
        if ds.endswith( "\n" ): ds = ds[:-1]
        if ds == "": return True
        return ( isValidIsoDatestring( ds ) or isValidEurDatestring( ds ) )

    def showCalendar( self ):
        cal = CalendarDialog( self )
        text = self.text()
        d:QDate = None
        if text == "":
            d = getRelativeQDate( 0, 0 )
        else:
            if isValidIsoDatestring( text ):
                d = getQDateFromIsoString( text )

            else:
                d =getRelativeQDate( 0, 0 )
        cal.setSelectedDate( d )
        cal.setCallback( self.onDatumSelected )
        cal.show()

    def onDatumSelected( self, date:QDate ):
        self.setText( date.toString( "yyyy-MM-dd" ) )

######################  BaseLabel ##################################
class BaseLabel( QLabel ):
    def __init__( self, parent=None ):
        QLabel.__init__( self, parent )


#######################  BaseEdit  ###################################
class BaseEdit( QLineEdit ):
    def __init__( self, parent=None ):
        QLineEdit.__init__( self, parent )

    def mousePressEvent(self, evt:QMouseEvent):
        self.setSelection( 0, len( self.text() ) )

#########################  FloatEdit  ################################
class FloatEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        floatval = QDoubleValidator()
        self.setValidator( floatval )
        self.setAlignment( Qt.AlignRight )

    def getFloatValue( self ) -> float:
        val = self.text()
        if not val:
            val = "0.0"
        else:
            val = val.replace( ",", "." )
        return float( val )

    def setFloatValue( self, val:float ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def setFloatStringValue( self, val:str ):
        try:
            floatval = float( val )
            self.setFloatValue( floatval )
        except:
            self.setText( "" )

#########################  FloatEdit  ################################
class IntEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()
        self.setValidator( intval )
        self.setAlignment( Qt.AlignRight )

    def getIntValue( self ) -> int:
        val = self.text()
        if not val:
            val = "0"
        return int( val )

    def setIntValue( self, val:int ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def setIntStringValue( self, val:str ):
        try:
            intval = int( val )
            self.setIntValue( intval )
        except:
            self.setText( "" )

######################## Int Display  #############################
class IntDisplay( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()
        self.setValidator( intval )
        font = QFont( "Times New Roman", 12, QFont.Bold )
        self.setFont( font )
        # self.setStyleSheet( "color: red;" )
        self.setAlignment( Qt.AlignRight )

    def setIntValue( self, val:int ):
        self.setText( str( val ) )
        if val < 0:
            self.setStyleSheet( "color: red;" )
        else:
            self.setStyleSheet( "color: green;" )

    def getIntValue( self ) -> int:
        val = self.text()
        if not val: val = "0"
        return int( val )

################ TextDocument #####################
class TextDocument( QTextDocument ):
    def __init__( self, text ):
        QTextDocument.__init__( self, text )

################ LineEdit #########################
class LineEdit( BaseEdit ):
    def __init__( self, parent=None ):
        BaseEdit.__init__( self, parent )
        intval = QIntValidator()

    def setValue( self, value:Any ) -> None:
        self.setText( value )
        if value is None or value == "": return
        if isinstance( value, numbers.Number ):
            self.setAlignment( Qt.AlignRight )
        else:
            self.setAlignment( Qt.AlignLeft )

    def getValue( self ) -> Any:
        return self.text()

################  MultiLineEdit  ##################
class MultiLineEdit( QTextEdit ):
    def __init__( self, parent=None ):
        QTextEdit.__init__( self, parent )

################ TableViewDialog ##################
class TableViewDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self._selectedCallback = None

        self._tv = TableView( self )
        self._btnOk = QPushButton( self, text = "Übernehmen zur Bearbeitung" )
        self._btnOk.clicked.connect( self._onOk )
        self._btnClose = QPushButton( self, text="Schließen" )
        self._btnClose.clicked.connect( self._onClose )

        vlayout = QVBoxLayout( self )
        vlayout.addWidget( self._tv )
        hlayout = QHBoxLayout()
        hlayout.addWidget( self._btnOk )
        hlayout.addWidget( self._btnClose )
        vlayout.addLayout( hlayout )

        self.setLayout( vlayout )

    def getTableView( self ) -> TableView:
        return self._tv

    def setSelectedCallback( self, cbfnc ):
        """
        Callback function must accept a list of QModelIndex representing the selected rows/columns
        :param cbfnc:
        :return:
        """
        self._selectedCallback = cbfnc

    def setTableModel( self, model:QAbstractTableModel ):
        self._tv.setModel( model )
        self._tv.setSizeAdjustPolicy( QtWidgets.QAbstractScrollArea.AdjustToContents )
        self._tv.resizeColumnsToContents()

    def _onOk( self ):
        if self._selectedCallback:
            sel_list = self._tv.selectedIndexes()
            self._selectedCallback( sel_list )
        self._onClose()

    def _onClose( self ):
        self.close()

###############  CheckBox  ########################
class CheckBox( QCheckBox ):
    def __init__( self, parent=None ):
        QCheckBox.__init__( self, parent )

################ SumDialog ########################
class SumDialog( QDialog ):
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setModal( True )
        self.setWindowTitle( "Summe der selektierten Zahlen" )
        layout = QGridLayout( self )
        self.label = QtWidgets.QLabel( self )
        self.label.setText( "Summe:" )
        layout.addWidget( self.label, 0, 0 )

        self._sumLabel = QtWidgets.QLabel( self )
        layout.addWidget( self._sumLabel, 0, 1 )

        self._btnCopyToClipboard = QPushButton( self, text="Kopieren" )
        layout.addWidget( self._btnCopyToClipboard, 1, 0 )
        self._btnCopyToClipboard.clicked.connect( self._copy2clipboard )

        self._btnClose = QPushButton( self, text="Schließen" )
        layout.addWidget( self._btnClose, 1, 1 )
        self._btnClose.clicked.connect( self._onClose )
        self.setLayout( layout )

    def _copy2clipboard( self ):
        """
        kopiert die angezeigte Zahl ins Clipboard
        :return:
        """
        clipboard = QGuiApplication.clipboard()
        clipboard.setText( self._sumLabel.text() )

    def _onClose( self ):
        self.close()

    def setSum( self, sum:int or float ) -> None:
        self._sumLabel.setText( str( sum ) )

####################################################################

class CustomItem( QStandardItem ):
    def __init__( self, text:str, userdata:Any=None ):
        QStandardItem.__init__( self, text )
        self.userdata = userdata

#####################################################################

class AuswahlDialog( QDialog ):
    def __init__( self, title=None,  parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self.listView = QListView()
        self.font = QFont( "Arial", 14 )
        self.okButton = QPushButton( "OK" )
        self.cancelButton = QPushButton( "Abbrechen" )
        self.model = QStandardItemModel()
        self.listView.setModel( self.model )
        self._selectedIndexes = ""
        self._createGui()

    def _createGui( self ):
        hbox = QHBoxLayout()
        hbox.addStretch( 1 )
        hbox.addWidget( self.okButton )
        hbox.addWidget( self.cancelButton )

        vbox = QVBoxLayout( self )
        vbox.addWidget( self.listView, stretch=1 )
        # vbox.addStretch(1)
        vbox.addLayout( hbox )

        self.okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "Auswahl" )

        self.okButton.clicked.connect( self.onAccepted )
        self.cancelButton.clicked.connect( self.reject )

    def appendItemList( self, itemlist:List[str] ):
        for i in itemlist:
            self.appendItem( i, None )

    def appendItem( self, text:str, userdata:Any=None ):
        item = CustomItem( text )
        if userdata:
            item.userdata = userdata
        item.setFont( self.font )
        self.model.appendRow( item )
        if self.model.rowCount() == 1:
            self.listView.setCurrentIndex( self.model.index( 0, 0 ) )

    def onAccepted(self):
        self._selectedIndexes = self.listView.selectedIndexes()
        self.accept()

    def getSelectedIndexes( self ):
        return self._selectedIndexes

    def getSelection( self ) -> List[Tuple]:
        sel = self.getSelectedIndexes()
        l = list()
        for idx in sel:
            item:CustomItem = self.model.item( idx.row(), idx.column() )
            t = ( item.text(), item.userdata )
            l.append( t )

        return l

#####################################################################

class CheckableAuswahlDialog( QDialog ):
    def __init__( self, stringlist:List[str], checked=False, title=None, icon=None, parent=None ):
        QDialog.__init__( self, parent )
        self.title = title
        self.icon = icon
        self.listView = QListView()
        self.okButton = QPushButton( "OK" )
        self.cancelButton = QPushButton( "Abbrechen" )
        self.selectButton = QPushButton( "Alle auswählen" )
        self.unselectButton = QPushButton( "Auswahl aufheben" )
        self.font = QFont( "Arial", 14 )
        self.model = QStandardItemModel()
        self.choices:List[str] = list()
        self._createGui()
        self._createModel( stringlist, checked )

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
        vbox.addLayout( h2box )
        vbox.addWidget(self.listView, stretch=1)
        #vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.okButton.setDefault( True )

        if self.title:
            self.setWindowTitle( self.title )
        else:
            self.setWindowTitle( "Auswahl" )

        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def _createModel( self, masterobjektList:List[str], checked:bool ):
        for obj in masterobjektList:
            item = QStandardItem( obj )
            item.setCheckable(True)
            item.setFont( self.font )
            check = (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)
        self.listView.setModel( self.model )


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




def testAuswahlDialog():
    app = QApplication()
    dlg = AuswahlDialog( title="Eine Auswahl" )
    dlg.appendItem( "dear me", 1 )
    dlg.appendItem( "dear you", 2 )
    if dlg.exec_() == QDialog.Accepted:
        l = dlg.getSelection()
        for t in l:
            print( "selected: ", t[0], t[1] )
        # indexes = dlg.getSelectedIndexes()
        # for i in indexes:
        #     print( "Selected: ", i.row() )

def onClick( l:List[str] ):
    print( l )

def test():
    app = QApplication()
    dlg = CheckableAuswahlDialog( ["SB_Kaiser", "ILL_Eich", "NK_Kleist"], title="Freie Auswahl!", checked=True )
    if dlg.exec_() == QDialog.Accepted:
        print( '\n'.join( [str( s ) for s in dlg.choices] ) )
    #app.exec_()

if __name__ == "__main__":
    #test()
    testAuswahlDialog()