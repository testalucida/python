import copy
from typing import List

from PySide2.QtCore import Signal, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QComboBox, QCheckBox, QApplication, QPushButton

import datehelper
from base.constants import monthLongNames
from definitions import ICON_DIR
from generictable_stuff.okcanceldialog import OkCancelDialog2
from generictable_stuff.xbasetablemodel import XBaseTableModel
from icc.iccview import IccTableEditorYearSpecificView

################### GeplantView ##################
from interfaces import XGeplant
from qtderivates import SmartDateEdit, FloatEdit, MultiLineEdit, BaseGridLayout


class GeplantView( IccTableEditorYearSpecificView ):
    """
    Die View, die eine Übersicht über alle Planungen bietet
    """
    def __init__( self, model:XBaseTableModel=None ):
        IccTableEditorYearSpecificView.__init__( self, model )

    def clear( self ):
        pass

##################   GeplantEditView   #####################
class GeplantEditView( QWidget ):
    """
    Eine View, die zur Anlage und ÄNderung einer Planung dient.
    Dazu muss sie in einen Dialog eingebettet werden (wg. der OK- und Cancel-Buttons).
    """
    masterobjektChanged = Signal( str )
    createHandwerker = Signal()
    def __init__( self, masterList:List[str]=None, firmenlist:List[str]=None, x:XGeplant=None, parent=None ):
        QWidget.__init__( self, parent )
        self._xgeplant = x
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._cboMasterObjekt = QComboBox()
        self._cboMasterObjekt.currentIndexChanged.connect( lambda x: self.masterobjektChanged.emit( self._cboMasterObjekt.currentText() ) )
        self._cboMobjId = QComboBox()
        self._txtLeistung = MultiLineEdit()
        self._cboFirma = QComboBox()
        self._btnNewFirma = QPushButton()
        self._btnNewFirma.clicked.connect( self.createHandwerker.emit )
        self._feKosten = FloatEdit()
        self._cbKostenvoranschlag = QCheckBox()
        self._cboJahr = QComboBox()
        self._cboMonat = QComboBox()
        self._cboMonat.addItems( monthLongNames )
        self._cbBeauftragt = QCheckBox()
        self._sdErledigtAm = SmartDateEdit()
        self._txtBemerkung = MultiLineEdit()
        self._provideJahre()
        if masterList:
            self.setMasterobjekte( masterList )
        if firmenlist:
            self.setFirmen( firmenlist )
        if x:
            self.setData( x )
        self._createGui()

    def _createGui( self ):
        """
        :return:
        """
        l = self._layout
        r = c = 0
        self._cboMasterObjekt.setMaximumWidth( 170 )
        l.addPair( "Masterobjekt: ", self._cboMasterObjekt, r, c, 1, 5  )
        r, c = r+1, 0
        self._cboMobjId.setMaximumWidth( 170 )
        l.addPair( "Mietobjekt (optional): ", self._cboMobjId, r, c, 1, 5 )
        r += 1
        self._txtLeistung.setMaximumHeight( 50 )
        l.addPair( "Leistung: ", self._txtLeistung, r, c, 1, 5 )
        r += 1
        l.addPair( "Firma: ", self._cboFirma, r, c, 1, 4 )
        c = 5
        self._btnNewFirma.setMaximumSize( QSize( 30, 30 )  )
        self._btnNewFirma.setIcon( QIcon( ICON_DIR + "add_512x512.png" ) )
        self._btnNewFirma.setToolTip( "Neue Firma erfassen" )
        l.addWidget( self._btnNewFirma, r, c )
        r, c = r+1, 0
        self._feKosten.setMaximumWidth( 90 )
        l.addPair( "Kosten: ", self._feKosten, r, c )
        c += 2
        l.addPair("Kostenvoranschlag: ", self._cbKostenvoranschlag, r, c )
        r, c = r+1, 0
        self._cboJahr.setMaximumWidth( 90 )
        l.addPair("Geplant: ", self._cboJahr, r, c )
        c += 2
        l.addWidget( self._cboMonat, r, c )
        r, c = r+1, 0
        l.addPair( "Beauftragt: ", self._cbBeauftragt, r, c )
        r, c = r + 1, 0
        self._sdErledigtAm.setMaximumWidth( 90 )
        l.addPair( "Erledigt am: ", self._sdErledigtAm, r, c )
        r, c = r+1, 0
        self._txtBemerkung.setMaximumHeight( 50 )
        self._txtBemerkung.setPlaceholderText( "Bemerkung" )
        l.addWidget( self._txtBemerkung, r, c, 1, 6 )
        r, c = r+1, 0
        dummy = QWidget()
        l.addWidget( dummy, r, c )

    def _createGui_( self ):
        """
        :return:
        """
        l = self._layout
        r = c = 0
        self._cboMasterObjekt.setMaximumWidth( 170 )
        l.addPair( "Masterobjekt: ", self._cboMasterObjekt, r, c, 1, 5  )
        r, c = r+1, 0
        self._cboMobjId.setMaximumWidth( 170 )
        l.addPair( "Mietobjekt (optional): ", self._cboMobjId, r, c, 1, 5 )
        r += 1
        self._txtLeistung.setMaximumHeight( 50 )
        l.addPair( "Leistung: ", self._txtLeistung, r, c, 1, 4 )
        r += 1
        l.addPair( "Firma: ", self._cboFirma, r, c, 1, 4 )
        c += 1
        self._btnNewFirma.setMaximumSize( QSize( 30, 30 )  )
        self._btnNewFirma.setIcon( QIcon( ICON_DIR + "save.png" ) )
        self._btnNewFirma.setToolTip( "Neue Firma erfassen" )
        #l.addWidget( self._btnNewFirma, r, c )
        r, c = r+1, 0
        self._feKosten.setMaximumWidth( 90 )
        l.addPair( "Kosten: ", self._feKosten, r, c )
        c += 2
        l.addPair("Kostenvoranschlag: ", self._cbKostenvoranschlag, r, c )
        r, c = r+1, 0
        self._cboJahr.setMaximumWidth( 90 )
        l.addPair("Geplant: ", self._cboJahr, r, c )
        c += 2
        l.addWidget( self._cboMonat, r, c )
        r, c = r+1, 0
        l.addPair( "Beauftragt: ", self._cbBeauftragt, r, c )
        r, c = r + 1, 0
        self._sdErledigtAm.setMaximumWidth( 90 )
        l.addPair( "Erledigt am: ", self._sdErledigtAm, r, c )
        r, c = r+1, 0
        self._txtBemerkung.setMaximumHeight( 50 )
        self._txtBemerkung.setPlaceholderText( "Bemerkung" )
        l.addWidget( self._txtBemerkung, r, c, 1, 5 )
        r, c = r+1, 0
        dummy = QWidget()
        l.addWidget( dummy, r, c )

    def _provideJahre( self ):
        y = datehelper.getCurrentYear()
        yearlist = []
        for y_ in range( y-2, y+6 ):
            yearlist.append( str(y_) )
        self._cboJahr.addItems( yearlist )
        self._cboJahr.setCurrentText( str(y) )

    def _setFieldsFromData( self ):
        """
        :return:
        """
        x = self._xgeplant
        self._cboMobjId.setCurrentText( x.mobj_id )
        self._txtLeistung.setText( x.leistung )
        self._cboFirma.setCurrentText( x.firma )
        self._feKosten.setFloatValue( x.kosten )
        self._cbKostenvoranschlag.setChecked( True if x.kostenvoranschlag > 0 else False )
        self._cboJahr.setCurrentText( str( x.jahr ) )
        monat = monthLongNames[x.monat - 1]
        self._cboMonat.setCurrentText( monat )
        self._sdErledigtAm.setDateFromIsoString( x.erledigtDatum )
        self._txtBemerkung.setText( x.bemerkung )

    def _setDataFromFields( self, x:XGeplant ):
        x.mobj_id = self._cboMobjId.currentText()
        x.leistung = self._txtLeistung.text()
        x.firma = self._cboFirma.currentText()
        x.kosten = self._feKosten.getFloatValue()
        x.kostenvoranschlag = 1 if self._cbKostenvoranschlag.isChecked() else 0
        x.jahr = int( self._cboJahr.currentText() )
        monat = self._cboMonat.getCurrentText()
        monIdx = monthLongNames.index( monat ) + 1
        x.monat = monIdx
        x.erledigtDatum = self._sdErledigtAm.getDate()
        x.bemerkung = self._txtBemerkung.toPlainText()

    def setMasterobjekte( self, masterlist:List[str] ):
        self._cboMasterObjekt.addItems( masterlist )

    def setMietobjekte( self, mobj_idList:List[str] ):
        """
        Versorgt die ComboBox mit den möglichen Werten (Mietobjekten)
        Diese Methode muss VOR setData() aufgerufen werden.
        :param mobj_idList:
        :return:
        """
        self._cboMobjId.addItems( mobj_idList )

    def clearMietobjekte( self ):
        self._cboMobjId.clear()

    def setFirmen( self, firmenlist:List[str] ):
        self._cboFirma.addItems( firmenlist )

    def getDataCopyWithChanges( self ) -> XGeplant:
        x = copy.copy( self._xgeschaeftsreise )
        self._setDataFromFields( x )
        return x

    def applyChanges( self ) -> XGeplant:
        self._setDataFromFields( self._xgeschaeftsreise )
        return self._xgeplant

    def setData( self, x:XGeplant ) -> None:
        self._xgeplant = x
        self._setFieldsFromData()

####################   GeplantEditDialog   #####################
class GeplantEditDialog( OkCancelDialog2 ):
    masterobjektChanged = Signal( str )
    createHandwerker = Signal()
    def __init__(self, masterList:List[str]=None, firmenlist:List[str]=None, x:XGeplant=None ):
        OkCancelDialog2.__init__( self )
        self._view = GeplantEditView( masterList, firmenlist, x )
        self._view.masterobjektChanged.connect( lambda master: self.masterobjektChanged.emit(master) )
        self._view.createHandwerker.connect( self.createHandwerker.emit )
        self.addWidget( self._view, 0 )
        title = "Neuanlage einer Planung" if not x or x.id == 0 else "Änderung '%s'" % \
                                                (x.leistung if len( x.leistung ) < 40 else x.leistung[0:40] + "...")
        self.setWindowTitle( title )

    def setMasterobjekte( self, masterobjekte ):
        self._view.setMasterobjekte( masterobjekte )

    def setMietobjekte( self, mietobjekte ):
        self._view.setMietobjekte( mietobjekte )

    def clearMietobjekte( self ):
        self._view.clearMietobjekte()

    def setFirmen( self, firmen ):
        self._view.setFirmen( firmen )

def test():
    app = QApplication()
    x = XGeplant()
    x.id = 1
    x.leistung = "Pflastern der Einfahrt mit Kabelkanal für Ladebox"
    dlg = GeplantEditDialog( ["kuchenberg_w", "lamm", "remigius"], ["Klempner: Saarbrücken >>> Jastrzebski",
                                                                    "Elektro: Illingen >>> Bardel"], x )
    # v = GeplantEditView( ["kuchenberg_w", "lamm", "remigius"], ["meyer", "bardel"]  )
    # dlg.addWidget( v, 0 )
    dlg.show()
    app.exec_()