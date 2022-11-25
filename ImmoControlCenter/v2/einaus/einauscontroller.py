from typing import List, Callable, Iterable
from PySide2.QtWidgets import QAction

import datehelper
from base.baseqtderivates import BaseComboBox, BaseEdit, FloatEdit, IntEdit, BaseCheckBox, SmartDateEdit, MultiLineEdit, \
    EditableComboBox
from base.filterhandler import FilterHandler
from base.interfaces import VisibleAttribute
from base.multisorthandler import MultiSortHandler
from base.printhandler import PrintHandler
from base.searchhandler import SearchHandler
from v2.einaus.einauslogic import EinAusLogic
from v2.einaus.einausview import EinAusTableView, EinAusTableViewFrame, XEinAusUI, EinAusDialog
from v2.icc.constants import EinAusArt
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame

# ##############  EinAusController  ####################
from v2.icc.interfaces import XEinAus, XMasterobjekt, XMietobjekt, XKreditorLeistung, XLeistung


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

    def createGui( self ) -> EinAusTableViewFrame:
        jahr = self.getYearToStartWith()
        tm = self._logic.getZahlungenModel( jahr )
        tv = self._tv
        tv.setModel( tm )
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

    def onNewEinAus( self ):
        def onMasterChanged( newMaster:str ):
            # Mietobjektnamen für geänderten Master ermitteln:
            mietobjektnamen = self._logic.getMietobjektNamen( newMaster )
            v = dlg.getDynamicAttributeView()
            cbo:BaseComboBox = v.getWidget( "mobj_id" )
            cbo.clear()
            cbo.addItems( mietobjektnamen )
            # Kreditoren für geänderten Master ermitteln:
            kreditoren = self._logic.getKreditoren( newMaster )
            cbo = v.getWidget( "debi_kredi" )
            cbo.clear()
            cbo.addItems( kreditoren )

        def onKreditorChanged( newKreditor:str ):
            # Leistungen für den geänderten Kreditor ermitteln:
            cbo = dlg.getDynamicAttributeView().getWidget( "master_name" )
            master_name = cbo.currentText()
            leistungen:List[str] = self._logic.getLeistungen( master_name, newKreditor )
            cbo:BaseComboBox = dlg.getDynamicAttributeView().getWidget( "leistung" )
            cbo.clear()
            cbo.addItems( leistungen )

        def onLeistungChanged( newLeistung:str ):
            umlegbar = "Nein"
            if newLeistung:
                v = dlg.getDynamicAttributeView()
                cbo = v.getWidget( "master_name" )
                master_name = cbo.currentText()
                cbo = v.getWidget( "debi_kredi" )
                kreditor = cbo.currentText()
                leist:XLeistung = self._logic.getLeistungskennzeichen( master_name, kreditor, newLeistung)
                if leist:
                    umlegbar = "Ja" if leist.umlegbar else "Nein"
                    #todo ea_art =
            cbo = v.getWidget( "umlegbar" )
            cbo.setCurrentText( umlegbar )

        x = XEinAus()
        masternames = self._logic.getMasterNamen()
        x.master_name = masternames[0]
        mietobjektenames = self._logic.getMietobjektNamen( x.master_name )
        kreditoren = self._logic.getKreditoren( x.master_name )
        x.buchungsdatum = datehelper.getCurrentDateIso()
        xui = XEinAusUI( x )
        vislist = self._createVisibleAttributeList( masternames, mietobjektenames, kreditoren,
                                                    onMasterChanged, onKreditorChanged, onLeistungChanged )
        xui.addVisibleAttributes( vislist )
        dlg = EinAusDialog( xui )
        dlg.exec_()

    @staticmethod
    def _createVisibleAttributeList( masterobjekte:List[str], mietobjekte:List[str], kreditoren:List[str],
                                     onMasterChangedCallback:Callable, onKreditorChangedCallback:Callable,
                                     onLeistungChangedCallback:Callable ) \
            -> Iterable[VisibleAttribute]:
        smallW = 90
        vislist = (
            VisibleAttribute( "master_name", BaseComboBox, "Haus: ", nextRow=False,
                              comboValues=masterobjekte, comboCallback=onMasterChangedCallback ),
            VisibleAttribute( "mobj_id", BaseComboBox, "Wohnung: ", widgetWidth=150, comboValues=mietobjekte ),
            VisibleAttribute( "debi_kredi", EditableComboBox, "Zahlung an/von: ",
                              comboValues=kreditoren, comboCallback=onKreditorChangedCallback ),
            VisibleAttribute( "leistung", EditableComboBox, "Art d. Leistung: ",
                              comboCallback=onLeistungChangedCallback ),
            VisibleAttribute( "betrag", FloatEdit, "Betrag: ", widgetWidth=smallW ),
            VisibleAttribute( "ea_art", BaseComboBox, "Art d. Zahlung: ", comboValues=EinAusArt.getMemberNames() ),
            VisibleAttribute( "verteilt_auf", IntEdit, "vert. auf Jhre: ", widgetWidth=smallW ),
            VisibleAttribute( "umlegbar", BaseComboBox, "umlegbar: ", widgetWidth=smallW, comboValues=["Nein", "Ja"] ),
            VisibleAttribute( "buchungsdatum", SmartDateEdit, "Buchungsdatum: ", widgetWidth=smallW ),
            VisibleAttribute( "buchungstext", BaseEdit, "Buchungstext: ", columnspan=3 ),
            VisibleAttribute( "mehrtext", MultiLineEdit, "Bemerkung: ", widgetHeight=55, columnspan=3 )
        )
        return vislist

    def onEditEinAus( self, row:int ):
        print( "edit Zahlung ", str(row) )

    def onDeleteEinAus( self, rows:List[int] ):
        print( "delete Zahlungen ", rows )

    def onYearChanged( self, newYear:int ):
        # tm = self._logic.getMietzahlungenModel( newYear )
        # self._tv.setModel( tm )
        pass

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
    frame.show()
    app.exec_()
#
# def test():
#     from PySide2.QtWidgets import QApplication
#     app = QApplication()
#     tv = EinAusTableView()
#     vf = EinAusTableViewFrame( tv, withEditButtons=True )
#     vf.show()
#     app.exec_()