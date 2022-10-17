from abc import abstractmethod
from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QAction, QDialog

from base.baseqtderivates import BaseEdit, FloatEdit, SmartDateEdit, IntEdit, MultiLineEdit
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import XBaseUI, VisibleAttribute
from base.messagebox import ErrorBox
from v2.einaus.einausview import EinAusTableView
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccTableViewFrame, IccCheckTableViewFrame
from v2.icc.interfaces import XMtlZahlung, XEinAus
from v2.mtleinaus.mtleinauslogic import MieteLogic, MtlEinAusTableModel, MtlEinAusLogic
from v2.mtleinaus.mtleinausview import MieteTableView, MieteTableViewFrame, ValueDialog, MtlZahlungEditDialog


#############  MtlEinAusController  #####################
class MtlEinAusController( IccController ):
    def __init__( self, logic:MtlEinAusLogic ):
        IccController.__init__( self )
        self._logic:MtlEinAusLogic = logic
        self._newEinAus:XEinAus = None # hier werden ggf. neu angelegte Zahlungen geparkt

    @abstractmethod
    def createGui( self ) -> IccCheckTableViewFrame:
        pass

    @abstractmethod
    def getTableViewFrame( self ) -> IccTableViewFrame:
        pass

    @abstractmethod
    def getModel( self ) -> MtlEinAusTableModel:
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
        sollVal = model.getSollValue( row )
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
                print( "ACCEPTED" )
            else:
                print( "CANCELLED" )

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
                self._logic.deleteZahlungen( xlist, monatstm )
                # hat geklappt - jetzt die gelöschten Zahlungen aus dem MtlZahlungEditDialog entfernen:
                eatm.removeObjects( xlist )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Delete", str( ex ),
                                "\nException aufgetreten in MtlEinAusController.onBetragEdit.onDeleteItems" )
                box.moveToCursor()
                box.exec_()

        monatstm:MtlEinAusTableModel = self.getModel()
        monthIdx = monatstm.getSelectedMonthIdx()
        eatm = self._logic.getZahlungenModelMieterMonat( monatstm.getMieter( index.row() ), self._year, monthIdx )
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
            self._newEinAus = self._logic.addMonatsZahlung( model.getMietobjekt( row ), model.getDebiKredi( row ),
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


##############  MieteController  ####################
class MieteController( MtlEinAusController ):
    def __init__( self ):
        MtlEinAusController.__init__( self, MieteLogic.inst() )
        self._tv: MieteTableView = MieteTableView()
        self._tvframe: MieteTableViewFrame = MieteTableViewFrame( self._tv )

    def createGui( self ) -> IccCheckTableViewFrame:
        jahr, monat = self.getYearAndMonthToStartWith()
        tm = self._logic.getMietzahlungenModel( jahr, monat )
        tv = self._tv
        tv.setModel( tm )
        tb = self._tvframe.getToolBar()
        jahre = self.getJahre()
        if len(jahre) == 0:
            jahre.append( jahr )
        tb.addYearCombo( jahre , self.onYearChanged )
        tb.setYear( jahr )
        tb.addMonthCombo( self.onMonthChanged )
        tb.setMonthIdx( monat )

        tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
        tv.okClicked.connect( self.onBetragOk )
        tv.nokClicked.connect( self.onBetragEdit )
        return self._tvframe

    def getTableViewFrame( self ) -> IccTableViewFrame:
        return self._tvframe

    def getModel( self ) -> MtlEinAusTableModel:
        return self._tv.model()

    def provideActions( self, index, point, selectedIndexes ) -> List[QAction]:
        print( "context menu for column ", index.column(), ", row ", index.row() )
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

    def onYearChanged( self, newYear:int ):
        tm = self._logic.getMietzahlungenModel( newYear, self.getModel().getEditableMonthIdx() )
        self._tv.setModel( tm )

    def onMonthChanged( self, newMonthIdx:int, newMonthLongName:str = "" ) :
        model: MtlEinAusTableModel = self.getModel()
        model.setEditableMonth( newMonthIdx )

