from typing import Iterable

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QGridLayout

import datehelper
from base.baseqtderivates import BaseEdit, SmartDateEdit, FloatEdit, MultiLineEdit, ButtonIdent, IntEdit, \
    BaseDialogWithButtons, getOkCancelButtonDefinitions
from base.basetableview import BaseTableView
from base.basetableviewframe import BaseTableViewFrame
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import VisibleAttribute, ButtonDefinition
from base.messagebox import ErrorBox
from v2.abrechnungen.abrechnungenview import HGAbrechnungTableView, NKAbrechnungTableView, HGAbrechnungTableViewFrame, \
    NKAbrechnungTableViewFrame, XAbrechnungUI
from v2.abrechnungen.abrechnunglogic import HGAbrechnungLogic, HGAbrechnungTableModel, AbrechnungTableModel, \
    TeilzahlungTableModel
from v2.einaus.einausview import ValueDialog
from v2.icc.icccontroller import IccController

################   AbrechnungenController   #####################
from v2.icc.interfaces import XHGAbrechnung


class AbrechnungController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self.abrechJahr = datehelper.getCurrentYear() - 1 # Abrechnungen liegen zum laufenden Jahr nicht vor
        self.dlg: DynamicAttributeDialog = None

################  HGAbrechnungController   ####################
class HGAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self )
        self._logic = HGAbrechnungLogic()
        self._tv = HGAbrechnungTableView()
        self._tvframe = HGAbrechnungTableViewFrame( self._tv )

    def createGui( self ) -> HGAbrechnungTableViewFrame:
        tm:HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( self.abrechJahr )
        self._tv.setModel( tm )
        self._tv.setAlternatingRowColors( True )
        tb = self._tvframe.getToolBar()
        jahre = [self.abrechJahr, self.abrechJahr - 1, self.abrechJahr - 2]
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( self.abrechJahr )
        self._tvframe.editItem.connect( self.onOpenAbrechnungDialog )
        return self._tvframe

    def onYearChanged( self, newYear:int ):
        tm: HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( newYear )
        self._tv.setModel( tm )
        self.abrechJahr = newYear

    def onOpenAbrechnungDialog( self, row:int ):
        """
        In der Tabelle der Abrechnungen wurde eine Zeile ausgewählt und der Edit-Button der TableView gedrückt.
        Wir öffnen den Dialog "Hausgeldabrechnung eintragen/ändern für Objekt..."
        Im Feld "Zahlung" wird die Summe aller Teilzahlungen angezeigt, die zur betreffenden HGA bislang geleistet wurden.
        :param row: in der Tabelle markierte Abrechnung (Zeile)
        :return:
        """
        def onOk() -> str:
            """
            Im Dialog "Hausgeldabrechnung eintragen/ändern für Objekt..." wurde OK gedrückt.
            Die neuen oder geänderten Werte validieren und - wenn Validierung ok - speichern.
            Dialog schließen.
            :return:
            """
            v = dlg.getDynamicAttributeView()
            xcopy:XHGAbrechnung = v.getModifiedXBaseCopy()
            # der logic übergeben zum Validieren
            msg = self._logic.validateAbrechnung( xcopy )
            if not msg:
                # Validierung war ok, jetzt die geänderten Daten von der View ins Model übernehmen, dann
                # das Model speichern
                self.dlg.getDynamicAttributeView().updateData()
                xhga = self.dlg.getDynamicAttributeView().getXBase()
                msg = self._logic.trySave( xhga )
            return msg
        def onCancel() -> str:
            """
            Dialog "Hausgeldabrechnung eintragen/ändern für Objekt..." wurde Abbrechen gedrückt.
            Dialog schließen.
            :return:
            """
            return ""

        model:AbrechnungTableModel = self._tv.model()
        x:XHGAbrechnung = model.getElement( row )
        if not x.ab_jahr:
            # neue Abrechnung, existiert noch nicht in der DB
            x.ab_jahr = self.abrechJahr
        xui = XAbrechnungUI( x )
        vislist = self._createVisibleAttributeList()
        xui.addVisibleAttributes( vislist )
        title = "Hausgeldabrechnung eintragen/ändern für Objekt '%s'" % x.master_name
        self.dlg = dlg = DynamicAttributeDialog( xui, title )
        btnApply = dlg.getButton( ButtonIdent.IDENT_APPLY )
        btnApply.setEnabled( False )
        dlg.setCallbacks( onOk, None, onCancel )
        dlg.setMinimumWidth( 500 )
        dlg.exec_()

    def onEditZahlungen( self ):
        """
        Im Dialog "Hausgeldabrechnung eintragen/ändern für Objekt ..." wurde der Button neben dem Zahlungsfeld
        gedrückt. In Abhängigkeit davon, ob es bereits eine (gespeicherte!) Zahlung für die ausgewählte
        Abrechnung gibt, wird der ValueDialog oder der TeilzahlungenDialog geöffnet.
        :return:
        """
        def onValueEntered( value:float, text:str, buchungsdatum:str ) -> str:
            # Im ValueDialog wurde OK gedrückt. Werte überprüfen und wenn ok, in den DynamicAttributeView
            # übernehmen
            if not value:
                return "Es ist kein Wert angegeben."
            if buchungsdatum and not datehelper.isValidIsoDatestring( buchungsdatum ):
                return "Datum im falschen Format. Muss YYYY-MM-DD sein."
            # die im ValueDialog erfasste Zahlung in die Liste der Teilzahlungen im Abrechnungsobjekt XHGAbrechnung
            # eintragen und die View aktualisieren:
            xhga.addZahlung( value, buchungsdatum, text )
            self.dlg.getDynamicAttributeView().updateUI( "zahlung" )
            return ""

        feZahlg:FloatEdit = self.dlg.getDynamicAttributeView().getWidget( "zahlung" )
        val = feZahlg.getFloatValue()
        xhga:XHGAbrechnung = self.dlg.getDynamicAttributeView().getXBase()
        if not val or not xhga.hga_id:
            # es gibt noch keine (gespeicherte) Zahlung zur ausgewählten Abrechnung.
            # Deshalb öffnen wir den kleinen ValueDialog.
            valuedlg = ValueDialog( mitBuchungsdatum=True )
            if val:
                valuedlg.setValue( val )
            valuedlg.setCallback( onValueEntered )
            valuedlg.exec_()
        else:
            def onNewTeilzahlung():
                print( "onNewTeilzahlung" )
            def onEditTeilzahlung( row:int ):
                print( "onEditTeilzahlung" )
            def onDeleteTeilzahlung(rows:Iterable[int]):
                print( "onDeleteTeilzahlung" )
            def onTzDialogOk():
                print( "ok" )
            def onTzDialogCancel():
                print( "cancel" )
            # Es gibt mind. 1 Zahlung für die ausgewählte Abrechnung.
            # Deshalb öffnen wir den Teilzahlungsdialog (mit der Übersicht über die bisher geleisteten Zahlungen).
            tzdlg = self._createTeilzahlungDialog( xhga, onNewTeilzahlung, onEditTeilzahlung, onDeleteTeilzahlung,
                                                   onTzDialogOk, onTzDialogCancel )
            tzdlg.exec_()

    def _createTeilzahlungDialog( self, xhga:XHGAbrechnung, newTzCallback, editTzCallback, deleteTzCallback,
                                  okCallback, cancelCallback ) -> BaseDialogWithButtons:
        tm = self._logic.getTeilzahlungTableModel( xhga )
        tv = BaseTableView()
        tv.setModel( tm )
        tvf = BaseTableViewFrame( tv, withEditButtons=True )
        tvf.newItem.connect( newTzCallback )
        tvf.editItem.connect( editTzCallback )
        tvf.deleteItems.connect( deleteTzCallback )
        w = tvf.getPreferredWidth()
        title = "Teilzahlungen für Objekt %s, Abrechnung %d, Forderung: %.2f Euro" % \
                (xhga.master_name, xhga.ab_jahr, xhga.forderung)
        dlg = BaseDialogWithButtons( title, getOkCancelButtonDefinitions( okCallback, cancelCallback ) )
        dlg.setMainWidget( tvf )
        dlg.resize( QSize( w, dlg.height() ) )
        return dlg

    def _createVisibleAttributeList( self ) -> Iterable[VisibleAttribute]:
        smallW = 90
        vislist = (
            VisibleAttribute( "master_name", BaseEdit, "Objekt: ", editable=False ),
            VisibleAttribute( "weg_name", BaseEdit, "WEG: ", editable=False ),
            VisibleAttribute( "vw_id", BaseEdit, "Verwalter: ", editable=False ),
            VisibleAttribute( "ab_jahr", IntEdit, "Abrechnung für: ", editable=False, widgetWidth=smallW ),
            VisibleAttribute( "ab_datum", SmartDateEdit, "abgerechnet am: ", widgetWidth=smallW ),
            VisibleAttribute( "forderung", FloatEdit, "Forderung (€): ", widgetWidth=smallW ),
            VisibleAttribute( "entnahme_rue", FloatEdit, "Entnahme aus Rückl. (€): ", widgetWidth=smallW ),
            VisibleAttribute( "bemerkung", MultiLineEdit, "Bemerkung: ", widgetHeight=55 ),
            VisibleAttribute( "zahlung", FloatEdit, "Zahlung (€): ", widgetWidth=smallW, editable=False,
                              trailingButton=ButtonDefinition(
                                  "...", callback=self.onEditZahlungen, tooltip="(Teil-)Zahlung erfassen / ändern",
                                  ident="tz", maxW=30, maxH=30
                              ) )
            #VisibleAttribute( "buchungsdatum", SmartDateEdit, "Buchungsdatum: ", widgetWidth=smallW )
        )
        return vislist

################  NKAbrechnungController   ####################
class NKAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self )
        self._tv = NKAbrechnungTableView()
        self._tvframe = NKAbrechnungTableViewFrame( self._tv )

    def createGui( self ) -> NKAbrechnungTableViewFrame:
        # todo
        return self._tvframe

########################   TEST  TEST  TEST  TEST  TEST  ######################

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    c = HGAbrechnungController()
    tvf = c.createGui()
    tvf.show()
    tvf.resize( QSize(1600, 200) )
    app.exec_()
