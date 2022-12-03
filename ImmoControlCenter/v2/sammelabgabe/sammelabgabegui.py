from PySide2.QtCore import QSize, Qt, Signal
from PySide2.QtWidgets import QWidget

from base.baseqtderivates import OkApplyCancelDialog, BaseGridLayout, FloatEdit, BaseLabel, MultiLineEdit, SmartDateEdit
from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView
from v2.icc.interfaces import XSammelabgabe, XGrundbesitzabgabe


class SammelabgabeSplitterDialog( OkApplyCancelDialog ):
    sammelabgabe_erfasst = Signal( float )

    def __init__( self ):
        OkApplyCancelDialog.__init__( self, "Zahlung einer Sammelabgabe erfassen und aufteilen" )
        self.getApplyButton().setEnabled( False )
        #self._layout = BaseGridLayout()
        #self.setLayout( self._layout )
        self._tv = None
        self._feBetrag: FloatEdit = None
        self._mainWidget: QWidget = None
        self._createDlg()

    def _createDlg( self ):
        w = 90
        self._tv = BaseTableView()
        self._feBetrag = FloatEdit()
        self._feBetrag.setMaximumWidth( w )
        self._sdBuchungsdatum = SmartDateEdit()
        self._sdBuchungsdatum.setMaximumWidth( w )
        self._mainWidget = self._createMainWidget()
        self.setMainWidget( self._mainWidget )
        self.setCallbacks( beforeAcceptCallback=self.beforeAccept, applyCallback=None, beforeRejectCallback=None )

    def _createMainWidget( self ):
        # das kombinierte Widget aus der BaseTableView und dem Eingabefeld erstellen:
        w = QWidget()
        lay = BaseGridLayout()
        w.setLayout( lay )
        lay.addWidget( self._tv, 0, 0, 1, 2 )
        lay.addWidget( BaseLabel( "Von der Stadt eingezogener Betrag: " ), 1, 0, Qt.AlignRight )
        lay.addWidget( self._feBetrag, 1, 1 ) #, Qt.AlignLeft )
        lay.addWidget( BaseLabel( "Buchungsdatum: " ), 2, 0, Qt.AlignRight )
        lay.addWidget( self._sdBuchungsdatum, 2, 1 )
        mleHinweis = MultiLineEdit()
        text = "Nach Drücken von OK werden soviele Zahlungen angelegt wie Objekte angezeigt werden." \
               "Der eingegebene Betrag wird dabei als Buchungstext in alle Zahlungen übernommen."
        mleHinweis.setValue( text )
        mleHinweis.setEnabled( False )
        mleHinweis.setMaximumHeight( 60 )
        lay.addWidget( mleHinweis, 3, 0, 1, 2 )
        return w

    def setTableModel( self, tm:BaseTableModel ):
        self._tv.setModel( tm )
        w = self._tv.getPreferredWidth()
        h = self._tv.model().rowCount() * 25 + 200
        self.resize( QSize( w+35, h ) )

    def setAbschlag( self, betrag:float ):
        self._feBetrag.setFloatValue( betrag )

    def getAbschlag( self ) -> float:
        return self._feBetrag.getFloatValue()

    def getBuchungsdatum( self ) -> str:
        """
        :return: yyyy-mm-dd
        """
        return self._sdBuchungsdatum.getDate()

    def setBuchungsdatum( self, datum:str ):
        """
        :param datum: yyyy-mm-dd
        :return:
        """
        self._sdBuchungsdatum.setDateFromIsoString( datum )

    def getTableView( self ) -> BaseTableView:
        return self._tv

    def beforeAccept( self ):
        print( "before accept" )

def test():
    from PySide2.QtWidgets import QApplication
    from v2.sammelabgabe.sammelabgabelogic import SammelabgabeTableModel
    app = QApplication()
    x = XGrundbesitzabgabe()
    x.master_name = "KLFDSJ"
    x.grundsteuer = 123.44
    x.abwasser = 22.22
    x.strassenreinigung = 3.44
    x.computeSum()
    tm = SammelabgabeTableModel( (x, ), 2022 )
    dlg = SammelabgabeSplitterDialog()
    dlg.setTableModel( tm )
    dlg.exec_()