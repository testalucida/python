from abc import abstractmethod
from enum import IntEnum
from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog

from base.baseqtderivates import BaseEdit, FloatEdit, SmartDateEdit, IntEdit, MultiLineEdit, BaseAction
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from base.messagebox import ErrorBox
from v2.einaus.einauslogic import EinAusTableModel
from v2.einaus.einausview import EinAusTableView
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccTableViewFrame, IccCheckTableViewFrame
from v2.icc.interfaces import XMtlZahlung, XEinAus
from v2.mtleinaus.mtleinauslogic import MieteLogic, MtlEinAusTableModel, MtlEinAusLogic, MieteTableModel
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, ValueDialog, MtlZahlungEditDialog

class Action( IntEnum ):
    SHOW_MIETOBJEKT = 0,
    SHOW_MIETVERHAELTNIS = 1,
    SHOW_NETTOMIETE_UND_NKV = 2,
    COMPUTE_SUMME = 3,
    COPY = 4


#############  MtlEinAusController  #####################
class MtlEinAusController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._newEinAus:XEinAus = None # hier werden ggf. neu angelegte Zahlungen geparkt

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr, monat = self.getYearAndMonthToStartWith()
        # tm = self.createModel( jahr, monat )
        # tv = self._tv
        # tv.setModel( tm )
        tvf:IccCheckTableViewFrame = self.createTableViewFrame( jahr, monat )
        tb = tvf.getToolBar()
        jahre = self.getJahre()
        if len( jahre ) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( jahr )
        tb.addMonthCombo( self.onMonthChanged )
        tb.setMonthIdx( monat )
        tv = tvf.getTableView()
        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        tv.okClicked.connect( self.onBetragOk )
        tv.nokClicked.connect( self.onBetragEdit )
        return tvf

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
    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        pass

    @abstractmethod
    def onSelected( self, action: QAction ):
        pass

    @abstractmethod
    def onYearChanged( self, newYear: int ):
        pass

    @abstractmethod
    def onMonthChanged( self, newMonthIdx: int, newMonthLongName: str ):
        pass

    # def getCurrentYearAndMonth( self ):
    #     return self._year, self._month

    def onBetragOk( self, index:QModelIndex ):
        model:MtlEinAusTableModel = self.getModel()
        row = index.row()
        col = model.getEditableColumnIdx()
        val = model.getValue( row, col )
        if val > 0:
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
            MtlZahlungEditDialog aktualisieren.
            MtlEinAusTableView aktualisieren (Geänderte Zahlung anzeigen).
            :param row: Zeile des zu ändernden XEinAus-Objekts
            :return:
            """
            x:XEinAus = eatm.getElement( row )
            xui = XBaseUI( x )
            vislist = ( VisibleAttribute( "mobj_id", BaseEdit, "Wohnung: ", editable=False, nextRow=False ),
                        VisibleAttribute( "debi_kredi", BaseEdit, "Mieter: ", editable=False ),
                        VisibleAttribute( "jahr", IntEdit, "Jahr: ", editable=False, widgetWidth=50 ),
                        VisibleAttribute( "monat", BaseEdit, "Monat: ", widgetWidth=50, editable=False ),
                        VisibleAttribute( "betrag", FloatEdit, "Betrag: ", widgetWidth=60, nextRow=False ),
                        VisibleAttribute( "mehrtext", MultiLineEdit, "Bemerkung: ", widgetHeight=60 ),
                        VisibleAttribute( "write_time", BaseEdit, "eingetragen: ", widgetWidth=100, editable=False ) )
            xui.addVisibleAttributes( vislist )
            dlg = DynamicAttributeDialog( xui, "Ändern einer Monatsmietzahlung" )
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
            Ausgewählte Zahlungen löschen, MtlZahlungEditDialog aktualisieren (Row entfernen),
            MtlEinAusTableView aktualisieren (den Betrag der gelöschten Zahlung vom Monatswert abziehen).
            :param rowlist:
            :return:
            """
            xlist:List[XEinAus] = eatm.getElements( rowlist )
            try:
                # wir übergeben der Logik die Einzelzahlungen in xlist zum Löschen aus der <einaus>.
                # Außerdem übergeben wir das Model mit den XMtlZahlung-Objekten. (Ein XMtlZahlung-Objekt ist aus
                # der Saldierung mehrerer XEinAus-Objekte entstanden.
                self.getLogic().deleteZahlungen( xlist, monatstm )
                # hat geklappt - jetzt die gelöschten Zahlungen aus dem MtlZahlungEditDialog entfernen:
                eatm.removeObjects( xlist )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Delete", str( ex ),
                                "\nException aufgetreten in MtlEinAusController.onBetragEdit.onDeleteItems" )
                box.moveToCursor()
                box.exec_()

        monatstm:MtlEinAusTableModel = self.getModel()
        monthIdx = monatstm.getSelectedMonthIdx()
        eatm = self.getLogic().getZahlungenModelMieterMonat( monatstm.getMieter( index.row() ), self._year, monthIdx )
        keys = ( "mobj_id", "debi_kredi", "jahr", "monat", "betrag", "write_time" )
        headers = ( "Wohnung", "Mieter", "Jahr", "Monat", "Betrag", "eingetragen" )
        eatm.setKeyHeaderMappings2( keys, headers )
        if eatm.rowCount() > 0:
            # Es gibt schon eine Zahlung für den betreff. Monat.
            # Deshalb den MtlZahlungEditDialog zeigen, damit der User die Zahlung auswählen kann, die er ändern oder
            # löschen will. Er kann auch eine neue Zahlung anlegen.
            eatv = EinAusTableView()
            eatv.setModel( eatm )
            dlg = MtlZahlungEditDialog( eatv )
            tvframe = dlg.getTableViewFrame()
            tvframe.newItem.connect( onNewItem )
            tvframe.editItem.connect( onEditItem )
            tvframe.deleteItems.connect( onDeleteItems )
            dlg.exec_()
        else:
            # Es gibt noch keine Zahlung für den betreff. Monat,
            # deshalb können wir den "kleinen" Dialog zeigen
            showValueDialog()

    def _addZahlung( self, row:int, value:float, bemerkung="" ) -> XEinAus:
        model: MtlEinAusTableModel = self.getModel()
        selectedMonthIdx = model.getSelectedMonthIdx()
        selectedYear = model.getJahr()
        try:
            # Datenbank-Insert
            self._newEinAus = self.getLogic().addMonatsZahlung( model.getMietobjekt( row ), model.getDebiKredi( row ),
                                                      selectedYear, selectedMonthIdx, value, bemerkung )

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
        # Datenbank-Update:
        self.getLogic().updateMonatsZahlung( x )
        # Update des MtlEinAusTableModel:
        model = self.getModel()
        newval = sum( [b.betrag for b in xlist ] )
        editColIdx = model.getEditableColumnIdx()
        model.setValue( row, editColIdx, newval )


##############  MieteController  ####################
class MieteController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self )
        self._logic = MieteLogic()
        self._tv: MieteTableView = None #MieteTableView()
        self._tvframe: MieteTableViewFrame = None #MieteTableViewFrame( self._tv )

    # def createGui( self ) -> IccCheckTableViewFrame:
    #     jahr, monat = self.getYearAndMonthToStartWith()
    #     tm = self._logic.createMietzahlungenModel( jahr, monat )
    #     tv = self._tv
    #     tv.setModel( tm )
    #     tb = self._tvframe.getToolBar()
    #     jahre = self.getJahre()
    #     if len(jahre) == 0:
    #         jahre.append( jahr )
    #     tb.addYearCombo( jahre , self.onYearChanged )
    #     tb.setYear( jahr )
    #     tb.addMonthCombo( self.onMonthChanged )
    #     tb.setMonthIdx( monat )

        # tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        # tv.okClicked.connect( self.onBetragOk )
        # tv.nokClicked.connect( self.onBetragEdit )
        # return self._tvframe

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
        print( "context menu for column ", index.column(), ", row ", index.row() )
        model:MieteTableModel = self._tv.model()
        idxlist = self._tv.selectedIndexes()
        for idx in idxlist:
            print( idx.row(), "/", idx.column() )
        l = list()
        col = index.column()
        key = model.keys[col]
        debikredi_key = self._logic.getDebiKrediKey()
        if key == "mobj_id":
            l.append( BaseAction( text="Objektdaten anzeigen", ident=Action.SHOW_MIETOBJEKT ) )
        if key == debikredi_key:
            l.append( BaseAction( "Mietverhaeltnisdaten anzeigen", ident=Action.SHOW_MIETVERHAELTNIS ) )
        if key == "soll":
            l.append( BaseAction( "Nettomiete und NKV anzeigen", ident=Action.SHOW_NETTOMIETE_UND_NKV ) )
        if key not in ( "mobj_id", "mv_id", "soll", "ok", "nok", "summe" ):
            if len( idxlist ) > 1:
                l.append( BaseAction( "Berechne Summe", ident=Action.COMPUTE_SUMME ) )
        if key not in ( "ok", "nok" ):
            sep = BaseAction()
            sep.setSeparator( True )
            l.append( sep )
            l.append( BaseAction( "Kopiere", ident=Action.COPY ) )

        # l.append( QAction( "Action 1" ) )
        # l.append( QAction( "Action 2" ) )
        # sep = QAction()
        # sep.setSeparator( True )
        # l.append( sep )
        # l.append( QAction( "Action 3" ) )
        return l

    def onSelected( self, action: BaseAction ):
        print( "selected action: ", str( action ), " - ident: ", action.ident )

    def onYearChanged( self, newYear:int ):
        tm = self._logic.createMietzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
        model: MtlEinAusTableModel = self.getModel()
        model.setEditableMonth( newMonthIdx )

