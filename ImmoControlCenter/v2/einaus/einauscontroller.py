from typing import List, Callable, Iterable

from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QAction, QDialog, QMenu

import datehelper
from base.baseqtderivates import BaseComboBox, BaseEdit, FloatEdit, IntEdit, BaseCheckBox, SmartDateEdit, MultiLineEdit, \
    EditableComboBox, BaseAction
from base.filterhandler import FilterHandler
from base.interfaces import VisibleAttribute
from base.messagebox import InfoBox
from base.multisorthandler import MultiSortHandler
from base.printhandler import PrintHandler
from base.searchhandler import SearchHandler
from v2.einaus.einausdialogcontroller import EinAusDialogController
from v2.einaus.einauslogic import EinAusLogic, EinAusTableModel
from v2.einaus.einausview import EinAusTableView, EinAusTableViewFrame, XEinAusUI, EinAusDialog
from v2.icc.constants import EinAusArt
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame

# ##############  EinAusController  ####################
from v2.icc.interfaces import XEinAus, XMasterobjekt, XMietobjekt, XKreditorLeistung, XLeistung
from v2.sammelabgabe.sammelabgabecontroller import SammelabgabeController


class EinAusController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._tv: EinAusTableView = EinAusTableView()
        self._sortHandler:MultiSortHandler = None
        self._filterHandler:FilterHandler = None
        self._searchHandler:SearchHandler = None
        self._printHandler:PrintHandler = None
        self._tvframe: EinAusTableViewFrame = EinAusTableViewFrame( self._tv, withEditButtons=True )
        self._logic = EinAusLogic()
        self._jahr:int = self.getYearToStartWith()

    def createGui( self ) -> EinAusTableViewFrame:
        jahr = self._jahr
        tv = self._tv
        tm = self._logic.getZahlungenModel( jahr )
        tv.setModel( tm )
        tv.sortByColumn( tm.getWriteTimeColumnIdx(), Qt.SortOrder.AscendingOrder )
        tb = self._tvframe.getToolBar()
        jahre = self.getJahre()
        if len(jahre) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre , self.onYearChanged )
        tb.setYear( jahr )
        tb.addSeparator()
        # sort
        self._sortHandler = MultiSortHandler( tv )
        tb.addSortAction( "Öffnet den Dialog zur Definition mehrfacher Sortierkriterien",
                          self._sortHandler.onMultiSort )
        # filter
        self._filterHandler = FilterHandler( tv )
        tb.addFilterAction( "Öffnet den Filterdialog zur Eingabe der Filterkriterien",
                            self._filterHandler.onFilter, self._filterHandler.onResetFilter )
        # search
        searchwidget = tb.addSearchWidget( True )
        self._searchHandler = SearchHandler( tv, searchwidget )
        self._printHandler = PrintHandler( tv )
        tb.addPrintAction( "Öffne Druckvorschau für diese Tabelle...", self._printHandler.handlePreview )
        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        ### neue Zahlung, Zahlung ändern, löschen:
        self._tvframe.newItem.connect( self.onNewEinAus )
        self._tvframe.editItem.connect( self.onEditEinAus )
        self._tvframe.deleteItems.connect( self.onDeleteEinAus )
        return self._tvframe

    def getMenu( self ) -> QMenu:
        menu = QMenu( "Sammelabgabe" )
        # Menü "Sammelabgabe"
        action = BaseAction( "Sammelabgabe erfassen und aufsplitten...", parent=menu )
        action.triggered.connect( self.onSammelabgabe )
        menu.addAction( action )
        return menu

    def onSammelabgabe( self ):
        c = SammelabgabeController()
        einauslist:List[XEinAus] = c.processSammelabgabe( self._jahr )
        if einauslist and len( einauslist ) > 0:
            tm:EinAusTableModel = self._tv.model()
            for ea in einauslist:
                tm.addObject( ea )

    def onNewEinAus( self ):
        ctrl = EinAusDialogController()
        ctrl.ea_inserted.connect( self.onNewEinAusInserted )
        ctrl.processNewEinAus()

    def onNewEinAusInserted( self, x:XEinAus ):
        # der Tabelle den neuen Satz hinzufügen - aber nur, wenn das steuerliche Jahr <x.jahr>
        # zu dem in der Combobox selektierten Jahr passt.
        if self._jahr == x.jahr:
            model:EinAusTableModel = self._tv.model()
            model.addObject( x )
        else:
            box = InfoBox( "Buchung für fremdes Jahr", "Die eingegebene Buchung bezieht sich auf das Jahr %d.\n"
                                                       "Eingestellt ist Jahr %d.\n"
                                                       "Deshalb kann die neue Buchung nicht angezeigt werden.\n"
                                                       "Sie wurde jedoch gespeichert." % (x.jahr, self._jahr), "", "OK" )
            box.exec_()

    def onEditEinAus( self, row:int ):
        print( "edit Zahlung ", str(row) )

    def onDeleteEinAus( self, rows:List[int] ):
        print( "delete Zahlungen ", rows )

    def onYearChanged( self, newYear:int ):
        self._jahr = newYear
        tm = self._logic.getZahlungenModel( self._jahr )
        tv = self._tv
        tv.setModel( tm )

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        #print( "context menu for column ", index.column(), ", row ", index.row() )
        l = list()
        l.append( QAction( "Action 1" ) )
        l.append( QAction( "Action 2" ) )
        sep = QAction()
        sep.setSeparator( True )
        l.append( sep )
        l.append( QAction( "Action 3" ) )
        return l

    def onSelected( self, action: QAction ):
        print( "selected action: ", str( action ) )


# #####################   TEST   TEST   TEST   ##################
#
def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = EinAusController()
    frame = c.createGui()
    w = frame.getTableView().getPreferredWidth()
    h = frame.getTableView().getPreferredHeight()
    frame.show()
    frame.resize( QSize(w, h) )
    app.exec_()
#
# def test():
#     from PySide2.QtWidgets import QApplication
#     app = QApplication()
#     tv = EinAusTableView()
#     vf = EinAusTableViewFrame( tv, withEditButtons=True )
#     vf.show()
#     app.exec_()