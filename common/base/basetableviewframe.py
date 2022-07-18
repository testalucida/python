from typing import List, Callable

from PySide2 import QtCore
from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget, QGridLayout, QToolBar, QComboBox, QApplication, QAction, QLabel

from base.interfaces import TestItem
from base.baseqtderivates import BaseEdit, BaseWidget, SearchWidget
from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView

from base.constants import monthnames
from base.directories import BASE_IMAGES_DIR
from base.searchhandler import SearchHandler
from base.multisorthandler import MultiSortHandler
from iconfactory import IconFactoryS

####################  SortKeyValue  #########################
class SortKeyValue:
    def __init__(self):
        self.key = ""
        self.value = ""

####################  BaseTableViewToolBar  ###################
class BaseTableViewToolBar( QToolBar ):
    def __init__( self ):
        QToolBar.__init__( self )
        self._yearCombo = None
        self._monthCombo = None
        self._saveEnabledIcon = None
        self._saveDisabledIcon = None
        self._saveActionId = "save"
        self._searchActionId = "search"
        self._sortActionId = "sort"
        self._filterActionId = "filter"
        self._resetFilterActionId = "reset_filter"
        self._actions:List[QAction] = list()
        self._searchWidget = None

    def addYearCombo( self, years:List[int], callback:Callable ) -> None:
        combo = QComboBox()
        for y in years:
            combo.addItem( str( y ) )
        combo.currentIndexChanged.connect( callback )
        self.addWidget( combo )
        self._yearCombo = combo

    def addMonthCombo( self, callback:Callable ) -> None:
        combo = QComboBox()
        combo.addItems( monthnames )
        combo.currentIndexChanged.connect( callback )
        self.addWidget( combo )
        self._monthCombo = combo

    def addSaveAction( self, tooltip:str, callback:Callable, enabled:bool=False, separatorBefore:bool=True ):
        if separatorBefore:
            self.addSeparator()
        self._saveEnabledIcon = IconFactoryS.inst().getIcon( BASE_IMAGES_DIR + "save.png" )
        self._saveDisabledIcon = IconFactoryS.inst().getIcon( BASE_IMAGES_DIR + "save_disabled.png" )
        icon = self._saveEnabledIcon if enabled else self._saveDisabledIcon
        action = self.addAction( icon, tooltip, callback )
        action.setData( self._saveActionId )
        action.setEnabled( enabled )
        self._actions.append( action )

    def findAction( self, id:str ) -> QAction:
        for a in self._actions:
            if a.data() == id:
                return a
        raise Exception( "Action with id ", id, " not found." )

    def getSearchWidget( self ) -> SearchWidget:
        return self._searchWidget

    def setSaveActionEnabled( self, enable:bool=True ) -> None:
        action = self.findAction( self._saveActionId )
        if not action:
            raise Exception( "Save Action not found. Did you call BaseTableViewToolBar.addSaveAction before?" )
        if enable and not action.isEnabled():
            action.setIcon( self._saveEnabledIcon )
        elif not enable and action.isEnabled():
            action.setIcon( self._saveDisabledIcon )
        action.setEnabled( enable )

    def addSortAction( self, tooltip:str, callback:Callable, enabled:bool = True, separatorBefore:bool=True ) -> None:
        if separatorBefore:
            self.addSeparator()
        icon = IconFactoryS.inst().getIcon( BASE_IMAGES_DIR + "sort.png" )
        action = self.addAction( icon, tooltip, callback )
        action.setData( self._sortActionId )
        action.setEnabled( enabled )
        self._actions.append( action )

    def addFilterAction( self, tooltip:str, filter:Callable, resetFilter:Callable,
                         enabled:bool=True, separatorBefore:bool=True ) -> None:
        if separatorBefore:
            self.addSeparator()
        icon = IconFactoryS.inst().getIcon( BASE_IMAGES_DIR + "filter.png" )
        action = self.addAction( icon, tooltip, filter )
        action.setData( self._filterActionId )
        action.setEnabled( enabled )
        self._actions.append( action )
        # reset filter
        icon = IconFactoryS.inst().getIcon( BASE_IMAGES_DIR + "reset_filter.png" )
        action = self.addAction( icon, "Alle Filter aufheben", resetFilter )
        action.setData( self._resetFilterActionId )
        action.setEnabled( enabled )
        self._actions.append( action )

    def addSearchWidget( self, separatorBefore:bool=True ) -> SearchWidget:
        if separatorBefore:
                self.addSeparator()
        self._searchWidget = SearchWidget()
        self.addWidget( self._searchWidget )
        return self._searchWidget

    def setFocusToSearchfield( self ):
        self._searchWidget.setFocusToSearchField()

####################  BaseTableViewFrame  #####################
class BaseTableViewFrame( BaseWidget ):
    """
    Ein Widget, das eine BaseTableView enthält und eine erweiterbare Toolbar (BaseTableViewFrame.getToolBar()).
    """
    def __init__(self, tableView:BaseTableView ):
        QWidget.__init__( self )
        self._tv = tableView
        self._layout = QGridLayout()
        self._toolbar = BaseTableViewToolBar()
        self._createGui()

    def _createGui( self ):
        l = self._layout
        self.setLayout( l )
        l.addWidget( self._toolbar, 0, 0, alignment=QtCore.Qt.AlignTop )
        l.setContentsMargins( 0, 0, 0, 0 )
        l.addWidget( self._tv, 1, 0 )

    def getToolBar( self ) -> BaseTableViewToolBar:
        return self._toolbar

    def getTableView( self ) -> BaseTableView:
        return self._tv


########################### TEST  TEST  TEST  ############################
### Test siehe auch basetableview.py Funktion testBaseTableViewFrame()

def makeTestModel() -> BaseTableModel:
    nachnamen = ("Kendel", "Knabe", "Verhoeven", "Adler", "Strack-Zimmermann", "Kendel")
    vornamen = ("Martin", "Gudrun", "Paul", "Henriette", "Marie-Agnes", "Friedi")
    plzn = ("91077", "91077", "77654", "88954", "66538", "91077")
    orte = ("Keinsendelbach", "kainsendelbach", "Niederstetten", "Oberhimpflhausen", "Neunkirchen", "Steinbach")
    strn = ("Birnenweg 2", "Birnenweg 2", "Rebenweg 3", "Hubertusweg 22", "Wellesweilerstr. 56", "Ahornweg 2")
    alter = (67, 65, 54, 49, 60, 41)
    groessen = (180, 170, 179, 185, 161.5, 161.5)
    itemlist = list()
    for n in range( 0, len(nachnamen) ):
        i = TestItem()
        i.nachname = nachnamen[n]
        i.vorname = vornamen[n]
        i.plz = plzn[n]
        i.ort = orte[n]
        i.str = strn[n]
        i.alter = alter[n]
        i.groesse = groessen[n]
        itemlist.append( i )
    tm = BaseTableModel( itemlist )
    tm.headers = ("Nachname", "Vorname", "PLZ", "Ort", "Straße", "Alter", "Größe")
    key = tm.getKeyByHeader( "Straße" )
    print( key )
    return tm

def onSave():
    print( "onSave" )

def onYearChanged( newIndex ):
    print( "year changed: ", newIndex )

def onMonthChanged( newIndex ):
    print( "month changed: ", newIndex )

def onSearch( search ):
    print( "search for: ", search )

def onSort():
    print( "sort" )

def onFilter():
    print( "filter" )

def onResetFilter():
    print( "reset filter" )

def testFrame():
    app = QApplication()
    tm = makeTestModel()
    tv = BaseTableView()
    tv.setModel( tm )
    f = BaseTableViewFrame( tv )
    tb = f.getToolBar()
    tb.addSaveAction( "Änderungen speichern", onSave, separatorBefore=False )
    tb.addSeparator()
    tb.addYearCombo( (2022, 2021, 2020), onYearChanged )
    tb.addMonthCombo( onMonthChanged )

    sortHandler = MultiSortHandler( tv )
    tb.addSortAction( "Öffnet den Dialog zur Definition mehrfacher Sortierkriterien", sortHandler.onMultiSort )

    tb.addFilterAction( "Öffnet den Filterdialog zur Eingabe der Filterkriterien", onFilter, onResetFilter )
    searchwidget = tb.addSearchWidget( True )
    sh = SearchHandler( tv, searchwidget )

    f.show()
    tb.setFocusToSearchfield()
    app.exec_()

def testToolBar():
    def onYearChanged( newIndex ):
        print( "year changed: ", newIndex )

    def onMonthChanged( newIndex ):
        print( "month changed: ", newIndex )
        tb.setSaveActionEnabled( True )

    def onSave():
        print( "onSave" )
        tb.setSaveActionEnabled( False )

    def onSearch():
        pass

    app = QApplication()
    w = QWidget()
    w.setWindowTitle( "TestContainter für BaseTableViewToolBar" )
    l = QGridLayout()
    w.setLayout( l )
    tb = BaseTableViewToolBar()
    l.addWidget( tb, 0, 0 )
    tb.addYearCombo( (2022, 2021, 2020), onYearChanged )
    tb.addMonthCombo( onMonthChanged )
    tb.addSaveAction( "Änderungen speichern", onSave, enabled=True )
    tb.addSearchFacility( onSearch )
    w.show()
    app.exec_()