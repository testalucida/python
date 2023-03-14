from abc import abstractmethod
from typing import List

from PySide2.QtCore import QModelIndex, QSize
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog, QMenu

from base.baseqtderivates import BaseEdit, FloatEdit, IntEdit, MultiLineEdit, BaseAction, SumDialog
from base.basetablefunctions import BaseTableFunctions
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from base.messagebox import ErrorBox, InfoBox
from v2.einaus.einauslogic import EinAusTableModel
from v2.einaus.einausview import EinAusTableView, TeilzahlungDialog, ValueDialog
from v2.einaus.einauswritedispatcher import EinAusWriteDispatcher
from v2.icc.constants import Action
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame, IccTableView
from v2.icc.interfaces import XMtlZahlung, XEinAus
from v2.mietobjekt.mietobjektcontroller import MietobjektController
#from v2.mietverhaeltnis.mietverhaeltniscontroller import MietverhaeltnisController
from v2.mtleinaus.mtleinauslogic import MieteLogic, MtlEinAusTableModel, MtlEinAusLogic, MieteTableModel, HausgeldLogic, \
    HausgeldTableModel, AbschlagLogic, AbschlagTableModel
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, \
    HausgeldTableView, HausgeldTableViewFrame, AbschlagTableView, AbschlagTableViewFrame


#############  MtlEinAusController  #####################
class MtlEinAusController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._tableViewFrame:IccCheckTableViewFrame = None
        self._tv:IccTableView = None
        self._newEinAus:XEinAus = None # hier werden ggf. neu angelegte Zahlungen geparkt

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr, monthIdx = self.getYearAndMonthToStartWith()
        tvf:IccCheckTableViewFrame = self.createTableViewFrame( jahr, monthIdx )
        tb = tvf.getToolBar()
        jahre = self.getJahre()
        if len( jahre ) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( jahr )
        tb.addMonthCombo( self.onMonthChanged )
        tb.setMonthIdx( monthIdx )
        tv = tvf.getTableView()
        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        tv.okClicked.connect( self.onBetragOk )
        tv.nokClicked.connect( self.onBetragEdit )
        self._tableViewFrame = tvf
        self._tv = tv
        return tvf

    @abstractmethod
    def getMenu( self ) -> QMenu:
        pass

    @abstractmethod
    def getSollActions( self ) -> List[BaseAction]:
        pass

    @abstractmethod
    def createTableViewFrame( self, jahr:int, monat:int ) -> IccCheckTableViewFrame:
        pass

    @abstractmethod
    def createModel( self, jahr: int, monat: int ) -> MtlEinAusTableModel:
        pass

    @abstractmethod
    def getModel( self ) -> MtlEinAusTableModel:
        pass

    @abstractmethod
    def getLogic( self ) -> MtlEinAusLogic:
        pass

    @abstractmethod
    def getEinzelzahlungenModelMonat( self, debikredi:str, sab_id:int, jahr:int, monthIdx:int ) -> EinAusTableModel:
        pass

    @abstractmethod
    def getShowDebiKrediAction( self ) -> BaseAction:
        pass

    @abstractmethod
    def getSollAction( self ) -> BaseAction:
        pass

    @abstractmethod
    def onSpecificAction( self, action:Action ):
        pass

    @abstractmethod
    def onYearChanged( self, newYear: int ):
        model: MtlEinAusTableModel = self.getModel()
        # todo

    def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
        model: MtlEinAusTableModel = self.getModel()
        model.setEditableMonth( newMonthIdx )
        self.getLogic().selectedMonthChanged( model, newMonthIdx )

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        """
        Callback-Function, die zur Verfügung stehende Aktionen liefert, wenn der User durch Rechtsklick
        in eine Tabellenzelle das Kontextmenü öffnen möchte
        :param index:
        :param point:
        :param selectedIndexes:
        :return:
        """
        def isNumeric( row, col ) -> bool:
            val = model.getValue( row, col )
            return type( val ) in (int, float)

        model: MieteTableModel = self._tv.model()
        col = index.column()
        key = model.keys[col]
        debikredi_key = self._logic.getDebiKrediKey()
        l = list()
        if key == "mobj_id":
            mobj_id = model.getValue( index.row(), index.column() )
            if mobj_id:
                l.append( BaseAction( text="Objektdaten anzeigen...", ident=Action.SHOW_MIETOBJEKT ) )
        if key == debikredi_key:
            l.append( self.getShowDebiKrediAction() )
        if key == "soll":
            l.append( self.getSollAction() )
        if key in ( "leistung", "vnr" ):
            l.append( BaseAction( text="Leistungsvertrag anzeigen...", ident=Action.SHOW_LEISTUNGSVERTRAG ) )
        if key not in ( "mobj_id", debikredi_key, "soll", "ok", "nok", "summe" ):
            idxlist = self._tv.selectedIndexes()
            if len( idxlist ) > 1:
                l.append( BaseAction( "Berechne Summe...", ident=Action.COMPUTE_SUMME ) )
        if key not in ( "ok", "nok" ):
            sep = BaseAction()
            sep.setSeparator( True )
            l.append( sep )
            l.append( BaseAction( "Kopiere", ident=Action.COPY ) )
        return l

    def onSelected( self, action: BaseAction ):
        if action.ident == Action.SHOW_MIETOBJEKT:
            self._showMietobjekt()
        elif action.ident == Action.COMPUTE_SUMME:
            self._computeSumme()
        elif action.ident == Action.COPY:
            self._copySelectionToClipboard()
        else:
            self.onSpecificAction( action )

    def onBetragOk( self, index:QModelIndex ):
        model:MtlEinAusTableModel = self.getModel()
        row = index.row()
        col = model.getEditableColumnIdx()
        val = model.getValue( row, col )
        if val != 0:
            box = ErrorBox( "Übernahme des Soll-Werts nicht möglich.", "Der Monatswert ist bereits versorgt.",
                            "Vor Übernehmen des Soll-Werts muss der eingetragene Wert gelöscht werden." )
            box.exec_()
            return
        sollVal = model.getSollValue( row )
        if sollVal == 0:
            box = ErrorBox( "Übernahme des Soll-Werts nicht möglich.",
                            "Ein Sollwert von '0' kann nicht übernommen werden.", "" )
            box.exec_()
            return
        self._addZahlung( row, sollVal )

    def onBetragEdit( self, index: QModelIndex ):
        def showValueDialog():
            dlg = ValueDialog()
            crsr = QCursor.pos()
            dlg.setCallback( editing_done )
            dlg.move( crsr.x(), crsr.y() )
            dlg.exec_()

        def editing_done( val:float, bemerkung:str ):
            # callback für den ValueDialog, der dann zum Einsatz kommt, wenn es für einen Monat keine oder nur eine
            # Zahlung gibt.
            self._addZahlung( index.row(), val, bemerkung )
            eatm.addObject( self._newEinAus )

        def onNewItem():
            showValueDialog()

        def onEditItem( row:int ):
            """
            Callback vom MtlZahlungEditDialog.
            Ausgewählte Zahlung im DynamicAttributeDialog ändern lassen.
            TeilzahlungDialog aktualisieren.
            MtlEinAusTableView aktualisieren (Geänderte Zahlung anzeigen).
            :param row: Zeile des zu ändernden XEinAus-Objekts
            :return:
            """
            debikrediLabel = self.getModel().getDebiKrediHeader() + ": "
            x:XEinAus = eatm.getElement( row )
            xui = XBaseUI( x )
            vislist = ( VisibleAttribute( "master_name", BaseEdit, "Haus: ", editable=False, nextRow=False ),
                        VisibleAttribute( "mobj_id", BaseEdit, "Wohnung: ", editable=False, nextRow=False ),
                        VisibleAttribute( "debi_kredi", BaseEdit, debikrediLabel, editable=False ),
                        VisibleAttribute( "jahr", IntEdit, "Jahr: ", editable=False, widgetWidth=50 ),
                        VisibleAttribute( "monat", BaseEdit, "Monat: ", widgetWidth=50, editable=False ),
                        VisibleAttribute( "betrag", FloatEdit, "Betrag: ", widgetWidth=60, nextRow=False ),
                        VisibleAttribute( "buchungstext", MultiLineEdit, "Bemerkung: ", widgetHeight=60 ),
                        VisibleAttribute( "write_time", BaseEdit, "gebucht am: ", editable=False, columnspan=2 ) )
            xui.addVisibleAttributes( vislist )
            dlg = DynamicAttributeDialog( xui, "Ändern einer Monatszahlung" )
            if dlg.exec_() == QDialog.Accepted:
                v = dlg.getDynamicAttributeView()
                xcopy = v.getModifiedXBaseCopy()
                msg = self.getLogic().validateMonatsZahlung( xcopy )
                if msg:
                    box = ErrorBox( "Validierungsfehler", msg, xcopy.toString( printWithClassname=True ) )
                    box.exec_()
                    return
                v.updateData() # Validierung war ok, also Übernahme der Änderungen ins XBase-Objekt
                try:
                    # aus dem MtlZahlungenEditDialog die Liste der Einzelzahlungen holen,
                    # die in Summe die Monatszahlung ergeben:
                    xlist:List[XEinAus] = eatm.getRowList()
                    self._updateZahlung( x, xlist, row )
                except Exception as ex:
                    box = ErrorBox( "Fehler beim Ändern einer Monatszahlung", str( ex ), x.toString( True ) )
                    box.exec_()
                    return
            else:
                # cancelled
                return

        def onDeleteItems( rowlist:List[int] ):
            """
            Callback vom MtlZahlungEditDialog.
            Ausgewählte Zahlungen in <rowlist> löschen, MtlZahlungEditDialog aktualisieren (Row entfernen),
            MtlEinAusTableView aktualisieren (den Betrag der gelöschten Zahlung vom Monatswert abziehen).
            :param rowlist:
            :return:
            """
            try:
                self._deleteZahlungen( eatm, rowlist )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Delete", str( ex ),
                                "\nException aufgetreten in MtlEinAusController.onBetragEdit.onDeleteItems" )
                box.moveToCursor()
                box.exec_()

        monatstm:MtlEinAusTableModel = self.getModel()
        monthIdx = monatstm.getSelectedMonthIdx()
        eatm = self.getEinzelzahlungenModelMonat( monatstm.getDebiKredi( index.row() ),  monatstm.getSab_id( index.row() ),
                                                  self._year, monthIdx )
        if eatm.rowCount() > 0:
            # Es gibt schon eine Zahlung für den betreff. Monat.
            # Deshalb den TeilzahlungDialog zeigen, damit der User die Zahlung auswählen kann, die er ändern oder
            # löschen will. Er kann auch eine neue Zahlung anlegen.
            eatv = EinAusTableView()
            eatv.setModel( eatm )
            dlg = TeilzahlungDialog( eatv )
            tvframe = dlg.getTableViewFrame()
            tvframe.newItem.connect( onNewItem )
            tvframe.editItem.connect( onEditItem )
            tvframe.deleteItems.connect( onDeleteItems )
            w = tvframe.getPreferredWidth()
            h = tvframe.getPreferredHeight()
            dlg.resize( QSize( w, h ) )
            dlg.exec_()
        else:
            # Es gibt noch keine Zahlung für den betreff. Monat,
            # deshalb können wir den "kleinen" Dialog zeigen
            showValueDialog()

    def _addZahlung( self, row:int, value:float, bemerkung="" ) -> XEinAus or None:
        model: MtlEinAusTableModel = self.getModel()
        selectedMonthIdx = model.getSelectedMonthIdx()
        selectedYear = model.getJahr()
        try:
            # Datenbank-Insert
            x:XMtlZahlung = model.getElement( row ) # das OBjekt, in das die neue Monatszahlung eingetragen werden soll
            self._newEinAus = self.getLogic().addMonatsZahlung( x, selectedYear, selectedMonthIdx, value, bemerkung )
            # EinAusWriteDispatcher informieren, damit die tableview "Alle Zahlungen" und die Summenfelder
            # aktualisiert werden
            EinAusWriteDispatcher.inst().einaus_inserted( self._newEinAus )
        except Exception as ex:
            box = ErrorBox( "Fehler beim Aufruf von MieteLogic.addZahlung(...) ",
                            "Exception in MtlEinAusController._addZahlung():\n" +
                            str( ex ), "" )
            box.exec_()
            return None
        # Update von Model und View
        editColIdx = model.getEditableColumnIdx()
        oldval = model.getValue( row, editColIdx )
        model.setValue( row, editColIdx, oldval + value )
        return self._newEinAus

    def _updateZahlung( self, x:XEinAus, xlist:List[XEinAus], row ):
        """
        Die Zahlung <x>, die Teil einer Monatszahlung ist, wurde geändert.
        (Der angezeigte Monatswert kann aus 0 bis n einzelnen Zahlungen bestehen.)
        Der angezeigte Monatswert muss deshalb aktualisiert werden.
        Alle relevanten Einzelzahlungen sind in xlist vorhanden.
        Zunächst erfolgt der Datenbank-Update mit der geänderten Zahlung <x>.
        Danach werden alle Einzelzahlungen in xlist addiert, was den neuen Monatswert ergibt.
        Mit diesem wird das MtlEinAusTableModel aktualisiert.
        :param x: die geänderte Zahlung
        :param xlist: Liste aller Zahlungen des betreff. Monats
        :param row: Die Zeile im MtlEinAusTableModel, in der sich das zu ändernde XMtlZahlung-Objekt befindet
        :return: 
        """
        try:
            # Datenbank-Update:
            delta = self.getLogic().updateMonatsZahlung( x, self.getModel() )
            # EinAusWriteDispatcher informieren, damit die tableview "Alle Zahlungen" und die Summenfelder
            # aktualisiert werden
            EinAusWriteDispatcher.inst().einaus_updated( x, delta )
        except Exception as ex:
            box = ErrorBox( "Fehler beim Aufruf von MtlEinAusLogic.updateMonatsZahlung(...) ",
                            "Exception in MtlEinAusController._updateZahlung():\n" +
                            str( ex ), "" )
            box.exec_()
            return None

    def _deleteZahlungen( self, eatm:EinAusTableModel, rowlist:List[int] ):
        """
        Ein oder mehrere Einzelzahlungen, die zu einem Monatswert gehören, sollen gelöscht werden.
        :param eatm: EinAusTableModel, das die Einzelzahlungen enthält, die in Summe einen Monatswert ausmachen.
        :param rowlist: Liste der zu löschenden Zeilennummern.
                        Es handelt sich um das Model der Einzelzahlungen, die die Monatszahlung ergeben.
        :return:
        """
        if len( rowlist ) < 1: return
        xlist: List[XEinAus] = eatm.getElements( rowlist )
        ea_id_list = [x.ea_id for x in xlist]
        ea_art = xlist[0].ea_art # Annahme, dass alle ea_art'en gleich sind. Überprüft wird das im Logik-Modul.
        # wir übergeben der Logik die Einzelzahlungen in xlist zum Löschen aus der <einaus>.
        # Außerdem übergeben wir das Model mit den XMtlZahlung-Objekten. (Ein XMtlZahlung-Objekt ist aus
        # der Saldierung mehrerer XEinAus-Objekte entstanden.
        delta = self.getLogic().deleteZahlungen( xlist, self.getModel() )
        # hat geklappt - jetzt die gelöschten Zahlungen aus dem MtlZahlungEditDialog
        # ("Ändern/Ergänzen von Zahlungen") entfernen:
        eatm.removeObjects( xlist )
        # EinAusWriteDispatcher informieren, damit die tableview "Alle Zahlungen" und die Summenfelder
        # aktualisiert werden
        EinAusWriteDispatcher.inst().einaus_deleted( ea_id_list, ea_art, delta )

    def _showMietobjekt( self ):
        model:MtlEinAusTableModel = self.getModel()
        idx = self._tv.selectedIndexes()[0]
        mobj_id = model.getValue( idx.row(), idx.column() )
        mobjCtrl = MietobjektController.fromMietobjekt( mobj_id )
        mobjCtrl.createGui()

    def _computeSumme( self ):
        btf = BaseTableFunctions()
        btf.computeSumme( self._tv, 5 )

    def _copySelectionToClipboard( self ):
        btf = BaseTableFunctions()
        btf.copySelectionToClipboard( self._tv )

##############  MieteController  ####################
class MieteController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self )
        self._logic = MieteLogic()
        self._tv: MieteTableView = None #MieteTableView()
        self._tvframe: MieteTableViewFrame = None #MieteTableViewFrame( self._tv )

    def getTableView( self ) -> MieteTableView:
        return self._tv

    def createTableViewFrame( self, jahr:int, monat:int ) -> IccCheckTableViewFrame:
        self._tv = MieteTableView()
        tm = self.createModel( jahr, monat )
        self._tv.setModel( tm )
        self._tvframe = MieteTableViewFrame( self._tv )
        return self._tvframe

    def createModel( self, jahr:int, monat:int ) -> MieteTableModel:
        return self._logic.createMietzahlungenModel( jahr, monat )

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def getLogic( self ) -> MieteLogic:
        return self._logic

    def getMenu( self ) -> QMenu:
        return None

    def getEinzelzahlungenModelMonat( self, debikredi: str, sab_id:int, jahr: int, monthIdx: int ) -> EinAusTableModel:
        eatm = self._logic.getZahlungenModelDebiKrediMonat( debikredi, jahr, monthIdx )
        keys = ("mobj_id", "debi_kredi", "jahr", "monat", "betrag", "write_time")
        headers = ("Wohnung", "Mieter", "Jahr", "Monat", "Betrag", "gebucht am")
        eatm.setKeyHeaderMappings2( keys, headers )
        return eatm

    def onSpecificAction( self, action: BaseAction ):
        if action.ident == Action.SHOW_NETTOMIETE_UND_NKV:
            self._showNettomiete()
        elif action.ident == Action.SHOW_MIETVERHAELTNIS:
            self._showMietverhaeltnis()

    def _showMietverhaeltnis( self ):
        model: MieteTableModel = self.getModel()
        idx = self._tv.selectedIndexes()[0]
        mv_id = model.getValue( idx.row(), idx.column() )
        #mvCtrl = MietverhaeltnisController.fromMietverhaeltnis( mv_id )
        #mvCtrl.createGui()

    def _showNettomiete( self ):
        model: MieteTableModel = self.getModel()
        idx = self._tv.selectedIndexes()[0]
        mv_id = model.getElement( idx.row() ).getValue( "mv_id" )
        box = InfoBox( "Nettomiete und NKV", "Hieraus entsteht die Anzeige von Nettomiete und NKV für '%s'" % mv_id, "", "OK" )
        box.exec_()

    def onYearChanged( self, newYear:int ):
        tm = self._logic.createMietzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    # def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
    #     model: MtlEinAusTableModel = self.getModel()
    #     model.setEditableMonth( newMonthIdx )

    def getShowDebiKrediAction( self ) -> BaseAction:
        return BaseAction( "Mietverhaeltnisdaten anzeigen", ident=Action.SHOW_MIETVERHAELTNIS )

    def getSollAction( self ) -> BaseAction:
        """
        User hat im Kontextmenü der Miete-Tabelle die rechte Maustaste gedrückt.
        :return:
        """
        return BaseAction( "Nettomiete und NKV anzeigen", ident=Action.SHOW_NETTOMIETE_UND_NKV )

#############  HausgeldController  ####################
class HausgeldController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self )
        self._logic = HausgeldLogic()
        self._tv: HausgeldTableView = None
        self._tvframe: HausgeldTableViewFrame = None

    def getTableView( self ) -> HausgeldTableView:
        return self._tv

    def createTableViewFrame( self, jahr:int, monat:int ) -> IccCheckTableViewFrame:
        self._tv = HausgeldTableView()
        tm = self.createModel( jahr, monat )
        self._tv.setModel( tm )
        self._tvframe = HausgeldTableViewFrame( self._tv )
        return self._tvframe

    def createModel( self, jahr:int, monat:int ) -> HausgeldTableModel:
        return self._logic.createHausgeldzahlungenModel( jahr, monat )

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def getLogic( self ) -> HausgeldLogic:
        return self._logic

    def getMenu( self ) -> QMenu:
        return None

    def getEinzelzahlungenModelMonat( self, debikredi: str, sab_id:int, jahr: int, monthIdx: int ) -> EinAusTableModel:
        eatm = self._logic.getZahlungenModelDebiKrediMonat( debikredi, jahr, monthIdx )
        keys = ("debi_kredi", "jahr", "monat", "betrag", "write_time")
        headers = ("WEG", "Jahr", "Monat", "Betrag", "gebucht am")
        eatm.setKeyHeaderMappings2( keys, headers )
        return eatm

    def onSpecificAction( self, action: BaseAction ):
        if action.ident == Action.SHOW_HAUSGELD_UND_RUEZUFUE:
            self._showHausgeld()

    def _showHausgeld( self ):
        model: HausgeldTableModel = self.getModel()
        idx = self._tv.selectedIndexes()[0]
        weg_name = model.getElement( idx.row() ).getValue( "weg_name" )
        box = InfoBox( "Hausgeld und RüZuFü", "Hieraus entsteht die Anzeige von Hausgeld und "
                                              "Rücklagenzuführung für '%s'" % weg_name,
                       "", "OK" )
        box.exec_()

    def onYearChanged( self, newYear:int ):
        tm = self._logic.createHausgeldzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )


    def getShowDebiKrediAction( self ) -> BaseAction:
        """
        Anzeige, die gebracht werden soll, wenn der User in der Tableview mit der rechten Maustaste auf
        den WEG-Namen geklickt hat
        :return:
        """
        return BaseAction( "Verwaltungsdetails anzeigen...", ident=Action.SHOW_WEG_UND_VERWALTER )

    def getSollAction( self ) -> BaseAction:
        """
        User hat im Kontextmenü der Miete-Tabelle die rechte Maustaste gedrückt.
        :return:
        """
        return BaseAction( "Netto-Hausgeld und RüZuFü anzeigen", ident=Action.SHOW_HAUSGELD_UND_RUEZUFUE )

#############  AbschlagController  ####################
class AbschlagController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self )
        self._logic = AbschlagLogic()
        self._tv: AbschlagTableView = None
        self._tvframe: AbschlagTableViewFrame = None

    def getTableView( self ) -> AbschlagTableView:
        return self._tv

    def createTableViewFrame( self, jahr:int, monat:int ) -> IccCheckTableViewFrame:
        self._tv = AbschlagTableView()
        tm = self.createModel( jahr, monat )
        self._tv.setModel( tm )
        self._tvframe = AbschlagTableViewFrame( self._tv )
        return self._tvframe

    def createModel( self, jahr:int, monat:int ) -> AbschlagTableModel:
        return self._logic.createAbschlagzahlungenModel( jahr, monat )

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def getLogic( self ) -> AbschlagLogic:
        return self._logic

    def getMenu( self ) -> QMenu:
        return None

    def getEinzelzahlungenModelMonat( self, debikredi: str, sab_id:int, jahr: int, monthIdx: int ) -> EinAusTableModel:
        # für die Anzeige, aus welchen Einzelzahlungen sich der ausgewiesene Monatswert zusammensetzt
        # todo: Einzelzahlungen anhand sab_id ermitteln
        eatm = self._logic.getEinzelzahlungenModel( sab_id, jahr, monthIdx )
        # keys = ("master_name", "mobj_id", "debi_kredi", "sab_id", "jahr", "monat", "betrag", "write_time")
        # headers = ("Haus", "Wohnung", "Firma", "sab_id", "Jahr", "Monat", "Betrag", "gebucht am")
        # eatm.setKeyHeaderMappings2( keys, headers )
        return eatm

    def onSpecificAction( self, action: BaseAction ):
        if action.ident == Action.SHOW_LEISTUNGSVERTRAG:
            self._showLeistungsvertrag()

    def _showLeistungsvertrag( self ):
        model: AbschlagTableModel = self.getModel()
        idx = self._tv.selectedIndexes()[0]
        sab_id = model.getElement( idx.row() ).getValue( "sab_id" )
        box = InfoBox( "Leistungsvertrag", "Hieraus entsteht die Anzeige des Leistungsvertrags "
                                           "für sab_id = '%d'" % sab_id, "", "OK" )
        box.exec_()

    def onYearChanged( self, newYear:int ):
        tm = self.createModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    def getShowDebiKrediAction( self ) -> BaseAction:
        """
        Anzeige, die gebracht werden soll, wenn der User in der Tableview mit der rechten Maustaste auf
        den Kreditor-Namen geklickt hat
        :return:
        """
        return None

    def getSollAction( self ) -> BaseAction:
        """
        User hat im Kontextmenü der Miete-Tabelle die rechte Maustaste gedrückt.
        :return:
        """
        return BaseAction( "Leistungsvertrag anzeigen", ident=Action.SHOW_LEISTUNGSVERTRAG )



