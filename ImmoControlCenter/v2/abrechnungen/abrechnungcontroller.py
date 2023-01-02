from typing import Iterable

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QGridLayout

import datehelper
from base.baseqtderivates import BaseEdit, SmartDateEdit, FloatEdit, MultiLineEdit, ButtonIdent
from base.dynamicattributeui import DynamicAttributeDialog
from base.interfaces import VisibleAttribute, ButtonDefinition
from base.messagebox import ErrorBox
from v2.abrechnungen.abrechnungenview import HGAbrechnungTableView, NKAbrechnungTableView, HGAbrechnungTableViewFrame, \
    NKAbrechnungTableViewFrame, XAbrechnungUI
from v2.abrechnungen.abrechnunglogic import HGAbrechnungLogic, HGAbrechnungTableModel, AbrechnungTableModel
from v2.einaus.einausview import ValueDialog
from v2.icc.icccontroller import IccController

################   AbrechnungenController   #####################
from v2.icc.interfaces import XHGAbrechnung


class AbrechnungController( IccController ):
    def __init__( self ):
        IccController.__init__( self )

################  HGAbrechnungController   ####################
class HGAbrechnungController( AbrechnungController ):
    def __init__(self):
        AbrechnungController.__init__( self )
        self._logic = HGAbrechnungLogic()
        self._tv = HGAbrechnungTableView()
        self._tvframe = HGAbrechnungTableViewFrame( self._tv )
        self._abrechJahr = datehelper.getCurrentYear() - 1 # Abrechnungen liegen zum laufenden Jahr nicht vor
        self._dlg:DynamicAttributeDialog = None

    def createGui( self ) -> HGAbrechnungTableViewFrame:
        tm:HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( self._abrechJahr )
        self._tv.setModel( tm )
        self._tv.setAlternatingRowColors( True )
        tb = self._tvframe.getToolBar()
        jahre = [self._abrechJahr, self._abrechJahr - 1, self._abrechJahr - 2]
        tb.addYearCombo( jahre, self.onYearChanged )
        tb.setYear( self._abrechJahr )
        self._tvframe.editItem.connect( self.onOpenAbrechnungDialog )
        return self._tvframe

    def onYearChanged( self, newYear:int ):
        tm: HGAbrechnungTableModel = self._logic.getAbrechnungTableModel( newYear )
        self._tv.setModel( tm )
        self._abrechJahr = newYear

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
            # der logic übergeben zum Speichern
            msg = self._logic.trySave( xcopy )
            if not msg: self._dlg.getDynamicAttributeView().updateData()
            return msg
        def onCancel() -> str:
            """
            Dialog "Hausgeldabrechnung eintragen/ändern für Objekt..." wurde Abbrechen gedrückt.
            Dialog schließen.
            :return:
            """
            print( "cancel" )
            return ""

        model:AbrechnungTableModel = self._tv.model()
        x:XHGAbrechnung = model.getElement( row )
        xui = XAbrechnungUI( x )
        vislist = self._createVisibleAttributeList()
        xui.addVisibleAttributes( vislist )
        title = "Hausgeldabrechnung eintragen/ändern für Objekt '%s'" % x.master_name
        self._dlg = dlg = DynamicAttributeDialog( xui, title )
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
            #feZahlg.setFloatValue( value )
            xhga.addZahlung( value, buchungsdatum, text )
            self._dlg.getDynamicAttributeView().updateUI( "zahlung" )
            return ""

        feZahlg:FloatEdit = self._dlg.getDynamicAttributeView().getWidget( "zahlung" )
        val = feZahlg.getFloatValue()
        xhga:XHGAbrechnung = self._dlg.getDynamicAttributeView().getXBase()
        if not val or not xhga.hga_id:
            # es gibt noch keine (gespeicherte) Zahlung zur ausgewählten Abrechnung.
            # Deshalb öffnen wir den kleinen ValueDialog.
            valuedlg = ValueDialog( mitBuchungsdatum=True )
            if val:
                valuedlg.setValue( val )
            valuedlg.setCallback( onValueEntered )
            valuedlg.exec_()
        else:
            # Es gibt mind. 1 Zahlung für die ausgewählte Abrechnung.
            # Deshalb öffnen wir den Teilzahlungsdialog (mit der Übersicht über die bisher geleisteten Zahlungen).
            print( "Öffne TeilzahlungenDialog" )


    def _createVisibleAttributeList( self ) -> Iterable[VisibleAttribute]:
        smallW = 90
        vislist = (
            VisibleAttribute( "master_name", BaseEdit, "Objekt: ", editable=False ),
            VisibleAttribute( "weg_name", BaseEdit, "WEG: ", editable=False ),
            VisibleAttribute( "vw_id", BaseEdit, "Verwalter: ", editable=False ),
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
