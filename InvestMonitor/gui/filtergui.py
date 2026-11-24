from typing import List, Dict
from PySide6.QtCore import Qt, QSize, QEvent, QObject, Signal
from PySide6.QtWidgets import QFrame, QMainWindow, QVBoxLayout, QSpacerItem, QScrollArea, QWidget, QHeaderView
from base.baseqtderivates import BaseGridLayout, BaseCheckBox, BaseWidget, BaseLabel
from base.basetablemodel import SumTableModel
from base.basetableview import BaseTableView
from base.messagebox import ErrorBox, InfoBox
from controller.infopanelcontroller import InfoPanelController
from data.db.investmonitordata import InvestMonitorData
from generictable_stuff.okcanceldialog import OkCancelDialog
from gui.infopanel import InfoPanel
from gui.mainwindow import AllInfoPanelsScrollArea
from imon.enums import AllocTyp
from interface.interfaces import XWpGattung, XDepotPosition, XAllocation, XAllocReport
from logic.imonlogic import ImonLogic


##########################################################################
class AllocTableView(BaseTableView):
    def __init__( self ):
        BaseTableView.__init__(self)

###########################################################################
class AllTableViews(QWidget):
    """
    Ein Widget, das alle AllocTableView-Objekte enthält.
    AllTableViews wird in die AllTableViewsScrollArea platziert.
    """
    def __init__(self):
        QWidget.__init__(self)
        self._layout = BaseGridLayout()
        self.setLayout(self._layout)
        self._tvList:List[AllocTableView] = list()

    def addTableView( self, tv:AllocTableView, row:int, col:int ):
        self._layout.addWidget(tv, row, col)
        self._tvList.append(tv)

##############################################################
class AllTableViewsScrollArea( QScrollArea ):
    def __init__(self):
        QScrollArea.__init__( self )
        self._allTableViews = AllTableViews()
        self.setWidget( self._allTableViews )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarPolicy.ScrollBarAlwaysOn )
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarPolicy.ScrollBarAlwaysOn )
        self.setWidgetResizable( True )

    def addAllocTableView( self, tv:AllocTableView, row:int, col:int ):
        self._allTableViews.addTableView(tv, row, col)

##########################################################################
class AllocReportWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self._scrollArea = AllTableViewsScrollArea()
        self.setCentralWidget( self._scrollArea )
        self._tableViews:List[AllocTableView] = list()

    def getTableViewCount( self ) -> int:
        return len(self._tableViews)

    def resizeToFitTables( self ):
        cnt = len(self._tableViews)
        if cnt < 1: return
        tv = self._tableViews[0]
        vh:QHeaderView = tv.verticalHeader()
        hh:QHeaderView = tv.horizontalHeader()
        # Start with the total length of all columns and all rows.
        size = QSize( hh.length(), vh.length() )
        # The headers overlap in the top-left corner. We need to add the
        # width contributed by the vertical header, and the height
        # contributed by the horizontal header.
        size += QSize( vh.size().width(), hh.size().height() )
        # Add a small margin so scrollbars aren't triggered.
        size += QSize( 50, 50 )
        if cnt > 1: # wir haben 2 Spalten mit TableViews
            size.setWidth(size.width() * 2 + 30) # doppelte Breite plus Zwischenraum zwischen erster und zweiter Spalte
        if cnt > 2: # wir haben mind. 2 Rows mit TableViews
            size.setHeight(500)
        self.resize( size )

    def addAllocTableView( self, tv:AllocTableView, row:int, col:int ):
        self._scrollArea.addAllocTableView(tv, row, col)
        self._tableViews.append(tv)

#########################################################################
class FilterCheckBox(BaseCheckBox):
    # filterStateChanged = Signal( str, bool )

    def __init__( self, label:str, isChecked = False):
        """
        @param label: Text, der auf der GUI neben der CheckBox angezeigt wird
        @param isChecked: ob der Anfangsstatus gecheckt sein soll oder nicht
        Es darf nur ENTWEDER land ODER sektor angegeben werden
        """
        BaseCheckBox.__init__(self)
        self.setChecked(isChecked)
        self.setText(label)
        #self.stateChanged.connect(self.onFilterSpecChanged)

    # def onFilterSpecChanged( self, state ):
    #     #print("onFilterSpecChanged: ", state)
    #     isChecked = state == Qt.CheckState.Checked.value
    #     self.filterStateChanged.emit( self.text(), isChecked )

########################################################################

########################################################################
class FilterGroup( QFrame ):
    """
    Ein Widget, das *eine Spalte (Liste)* auswählbarer Filterkriterien
    einer bestimmten Filtergruppe (FilterSpec) enthält.
    Jedes Kriterium wird durch eine FilterCheckBox dargestellt.
    Außerdem kann eine Überschrift über die Gruppe von Filterkriterien platziert werden.
    Jede Änderung einer FilterCheckBox führt zu einem filterSpecChanged-Signal.
    """
    #filterSpecChanged = Signal(str, str, bool)
    """
        str: Identifikation dieser Gruppe (z.B. "land")
        str: Das Label, das bei der Instanzierung der betätigten FilterCheckBox übergeben wurde (z.B. "Singapur")
        bool: isChecked oder nicht
    """
    def __init__(self, caption:str, ident:str, labellist:List[str]):
        QFrame.__init__( self )
        self._caption = caption
        self._ident = ident
        self._labellist = labellist
        self._layout = QVBoxLayout() #BaseGridLayout()
        self.setLayout(self._layout)
        #self._r = 0
        self._cbList:List[FilterCheckBox] = list()
        self._createGui()
        self._borderthickness = "2px"
        self._bordercolor = "blue"
        self._borderstyle = "FilterGroup {border: " + self._borderthickness + " solid " + self._bordercolor + "; }"
        self.setStyleSheet( self._borderstyle )

    def _createGui( self ):
        l = self._layout
        lbl = BaseLabel(self._caption)
        font = lbl.font()
        font.setBold(True)
        lbl.setFont(font)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setTextAndBackgroundColor( "black", "lightgray")
        lbl.setFixedHeight(22)
        ####l.addWidget(lbl, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop )
        l.addWidget(lbl, stretch=0, alignment=Qt.AlignmentFlag.AlignTop )
        #self._r += 1
        l.addSpacerItem(QSpacerItem(1, 16))

        cb = FilterCheckBox("Alle wählen/abwählen")
        cb.checkStateChanged.connect(self.onCheckAll)
        #####l.addWidget( cb, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop )
        l.addWidget(cb, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        l.addSpacerItem( QSpacerItem( 1, 16 ) )
        #self._r += 1

        for label in self._labellist:
            cb = FilterCheckBox(label)
            self._cbList.append(cb)
            #cb.filterStateChanged.connect( self.onFilterSpecChanged )
            ####l.addWidget(cb, self._r, 0, 1, 1, PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
            l.addWidget(cb, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
            #self._r += 1

        l.addStretch()

    def getIdent( self ) -> str:
        return self._ident

    def setChecked( self, idx:int, val:bool ):
        self._cbList[idx].setChecked(val)

    def setCheckedAll( self, checked=True ):
        for cb in self._cbList:
            cb.setChecked(checked)

    def hasCheckedFilters( self ) -> bool:
        for cb in self._cbList:
            if cb.isChecked():
                return True
        return False

    def getCheckedFilters( self ) -> (str, List[str]):
        checked_items = list()
        for cb in self._cbList:
            if cb.isChecked():
                checked_items.append(cb.text())
        return self._ident, checked_items

    def onCheckAll( self, state ):
        checked = False
        if state == Qt.CheckState.Checked:
            checked = True
        for cb in self._cbList:
            cb.setChecked(checked)

##########################################################################
class FilterPanel(BaseWidget):
    """
    Ein Widget, das ein oder mehrere FilterGroups enthält.
    """
    def __init__( self ):
        BaseWidget.__init__(self)
        #QFrame.__init__(self)
        self._filterGroups:List[FilterGroup] = list()
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )

    def addFilterGroup( self, caption:str, ident:str, labellist:List[str], row:int, col:int ) -> FilterGroup:
        filtergrp = FilterGroup(caption, ident, labellist)
        self._filterGroups.append(filtergrp)
        self._layout.addWidget(filtergrp, row, col)
        return filtergrp

    def getFilterGroup( self, ident:str ) -> FilterGroup:
        for fg in self._filterGroups:
            if fg.getIdent() == ident:
                return fg
        raise Exception("Keine Filtergruppe mit ident " + ident + " gefunden.")

    def getFilterGroups( self ) -> List[FilterGroup]:
        return self._filterGroups

    def getCheckedFilters( self ) -> Dict:
        di = dict()
        for filtergrp in self._filterGroups:
            ident, checked_items = filtergrp.getCheckedFilters()
            di[ident] = checked_items
        return di

##########################################################################
class FilterAuswahlDialog( OkCancelDialog ):
    def __init__(self):
        OkCancelDialog.__init__(self, "Auswahl der Filterkriterien")
        self._filterPanel = None

    def setFilterPanel( self, filterPanel:FilterPanel ):
        self._filterPanel = filterPanel
        self.addWidget(filterPanel, 0)
        self.resize( self.sizeHint() )

##########################################################################
class ShutDownSignalSender( QObject ):
    closingWindow = Signal()
    def __init__( self, win: QWidget ):
        QObject.__init__( self )
        self._win = win
        # self._app = app

    def eventFilter( self, obj, event ) -> bool:
        if obj is self._win and event.type() == QEvent.Type.Close:
            self.sendCloseSignal()
            #event.ignore()
            return True
        return super( ShutDownSignalSender, self ).eventFilter( obj, event )

    def sendCloseSignal(self):
        print("sending Close Signal")
        self._win.removeEventFilter( self )
        self.closingWindow.emit()

##########################################################################
class FilterResultWindow(QMainWindow):
    closingWindow = Signal()
    def __init__(self):
        QMainWindow.__init__(self)
        self._panelsScroll = AllInfoPanelsScrollArea()
        self.setCentralWidget(self._panelsScroll)
        self._shutDownSignalSender = ShutDownSignalSender( self )
        self.installEventFilter(self._shutDownSignalSender)
        self._shutDownSignalSender.closingWindow.connect(self.closingWindow.emit)

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._panelsScroll.addInfoPanel( infopanel )
