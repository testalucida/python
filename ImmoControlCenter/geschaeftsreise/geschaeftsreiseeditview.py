import copy
from typing import List

from PySide2.QtWidgets import QWidget, QFormLayout, QComboBox, QApplication, QPushButton, QHBoxLayout

from generictable_stuff.okcanceldialog import OkCancelDialog
from interfaces import XGeschaeftsreise
from qtderivates import SmartDateEdit, BaseEdit, MultiLineEdit, IntEdit, FloatEdit


class GeschaeftsreiseEditView( QWidget ):
    def __init__( self, mobjIdList:List[str]=None, x:XGeschaeftsreise=None, parent=None ):
        QWidget.__init__( self, parent )
        self._xgeschaeftsreise = x
        self._layout = QFormLayout()
        self.setLayout( self._layout )
        self._cboMobjId = QComboBox()
        self._sdVon = SmartDateEdit()
        self._sdBis = SmartDateEdit()
        self._beZiel = BaseEdit()
        self._meZweck = MultiLineEdit()
        self._ieKm = IntEdit()
        self._feVpflPausch = FloatEdit()
        self._beUebernachtung = BaseEdit()
        self._feUebernachtKosten = FloatEdit()
        # self._btnSave = QPushButton( "Speichern" )
        # self._btnSaveClose = QPushButton( "Speichern und Schließen" )
        # self._btnCancel = QPushButton( "Abbrechen" )
        self._createGui()
        if mobjIdList:
            self.setMietobjekte( mobjIdList )
        if x:
            self.setData( x )

    def _createGui( self ):
        """
        :return:
        """
        l = self._layout
        self._cboMobjId.setMaximumWidth( 100 )
        l.addRow( "Mietobjekt: ", self._cboMobjId )
        self._sdVon.setMaximumWidth( 100 )
        l.addRow( "Beginn: ", self._sdVon )
        self._sdBis.setMaximumWidth( 100 )
        l.addRow( "Ende: ", self._sdBis )
        l.addRow( "Ziel: ", self._beZiel )
        self._meZweck.setMaximumHeight( 80 )
        l.addRow( "Zweck: ", self._meZweck )
        l.addRow( "Übernachtung: ", self._beUebernachtung )
        self._feUebernachtKosten.setMaximumWidth( 55 )
        l.addRow( "Übernacht.-Kosten: ", self._feUebernachtKosten )
        self._ieKm.setMaximumWidth( 55 )
        l.addRow( "Gefahrene Kilometer: ", self._ieKm )
        self._feVpflPausch.setMaximumWidth( 55 )
        l.addRow( "Verpfleg.-Pauschale: ", self._feVpflPausch )
        dummy = QWidget()
        dummy.setFixedHeight( 20 )
        l.addRow( "", dummy )
        # boxl = QHBoxLayout()
        # boxl.addWidget( self._btnSave )
        # boxl.addWidget( self._btnSaveClose )
        # boxl.addWidget( self._btnCancel )
        # l.addRow( boxl )

    def _setFieldsFromData( self ):
        """
        :return:
        """
        x = self._xgeschaeftsreise
        self._cboMobjId.setCurrentText( x.mobj_id )
        self._sdVon.setDateFromIsoString( x.von )
        self._sdBis.setDateFromIsoString( x.bis )
        self._beZiel.setText( x.ziel )
        self._meZweck.setText( x.zweck )
        self._ieKm.setIntValue( x.km )
        self._feVpflPausch.setFloatValue( x.verpfleg_pauschale )
        self._beUebernachtung.setText( x.uebernachtung )
        self._feUebernachtKosten.setFloatValue( x.uebernacht_kosten )

    def _setDataFromFields( self, x:XGeschaeftsreise ):
        x.mobj_id = self._cboMobjId.currentText()
        x.von = self._sdVon.getDate()
        x.bis = self._sdBis.getDate()
        x.ziel = self._beZiel.text()
        x.zweck = self._meZweck.toPlainText()
        x.km = self._ieKm.getIntValue()
        x.verpfleg_pauschale = self._feVpflPausch.getFloatValue()
        x.uebernachtung = self._beUebernachtung.text()
        x.uebernacht_kosten = self._feUebernachtKosten.getFloatValue()

    def setMietobjekte( self, mobj_idList:List[str] ):
        """
        Versorgt die ComboBox mit den möglichen Werten (Mietobjekten)
        Diese Methode muss VOR setData() aufgerufen werden.
        :param mobj_idList:
        :return:
        """
        self._cboMobjId.addItems( mobj_idList )

    def getDataCopyWithChanges( self ) -> XGeschaeftsreise:
        x = copy.copy( self._xgeschaeftsreise )
        self._setDataFromFields( x )
        return x

    def applyChanges( self ) -> XGeschaeftsreise:
        self._setDataFromFields( self._xgeschaeftsreise )
        return self._xgeschaeftsreise

    def setData( self, x:XGeschaeftsreise ) -> None:
        self._xgeschaeftsreise = x
        self._setFieldsFromData()

########################  GeschaeftsreiseEditDialog  ####################
class GeschaeftsreiseEditDialog( OkCancelDialog ):
    def __init__( self, geschaeftsreiseeditview:GeschaeftsreiseEditView, parent=None ):
        OkCancelDialog.__init__( self, parent )
        self.view = GeschaeftsreiseEditView()
        self.addWidget( self.view )


def test():
    app = QApplication()
    v = GeschaeftsreiseEditView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()











