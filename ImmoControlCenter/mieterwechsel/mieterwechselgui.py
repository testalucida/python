from PySide2.QtGui import QFont, Qt
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QHBoxLayout
from generictable_stuff.okcanceldialog import OkCancelDialog
from mietverhaeltnisgui import MietverhaeltnisView
from qtderivates import AuswahlDialog, BaseEdit, SmartDateEdit, BaseLabel


##############  MietobjektAuswahlDialog  #######################
class MietobjektAuswahldialog( AuswahlDialog ):
    def __init__(self, parent=None):
        AuswahlDialog.__init__( self, "Auswahl des Mietobjekts", parent )

class MieterwechselView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        # altes Mietverhältnis
        self._edAlterMieter = BaseEdit()
        self._edAlteNettomiete = BaseEdit()
        self._edAlteNKV = BaseEdit()
        self._edAlteKaution = BaseEdit()
        self._sdEndeMietverh = SmartDateEdit()
        # neues Mietverhältnis
        self._neuesMietvh = MietverhaeltnisView()

        self._createGui()

    def _createGui( self ):
        r = self._createGuiAlterMieter()
        r+=1
        self._layout.addWidget( QLabel( "" ), r, 0 )
        r+=1
        self._createGuiNeuerMieter( r )
        self.setLayout( self._layout )

    def _createGuiAlterMieter( self ) -> int:
        l = self._layout
        r = c = 0
        lbl = BaseLabel( "Aktuelles / letztes Mietverhältnis " )
        lbl.setFont( QFont( "Arial", 12, QFont.Bold ) )
        l.addWidget( lbl, r, c, 1, 2 )

        r+=1
        lbl = QLabel( "Mieter: " )
        l.addWidget( lbl, r, c )
        self._edAlterMieter.setReadOnly( True )
        l.addWidget( self._edAlterMieter, r, c + 1 )

        r+=1
        lbl = BaseLabel( "Nettomiete / NKV : " )
        l.addWidget( lbl, r, c )

        c+=1
        hbox = QHBoxLayout()
        self._edAlteNettomiete.setReadOnly( True )
        self._edAlteNettomiete.setMaximumWidth( 100 )
        hbox.addWidget( self._edAlteNettomiete )

        self._edAlteNKV.setReadOnly( True )
        self._edAlteNKV.setMaximumWidth( 100 )
        hbox.addWidget( self._edAlteNKV )
        l.addLayout( hbox, r, c, Qt.AlignLeft )

        c = 0
        r += 1
        lbl = BaseLabel( "Kaution: " )
        l.addWidget( lbl, r, c )

        c+=1
        self._edAlteKaution.setReadOnly( True )
        self._edAlteKaution.setMaximumWidth( 100 )
        l.addWidget( self._edAlteKaution, r, c )

        c = 0
        r += 1
        lbl = QLabel( "Ende des Mietverhältnisses: " )
        l.addWidget( lbl, r, c )

        self._sdEndeMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdEndeMietverh, r, c + 1 )
        return r

    def _createGuiNeuerMieter( self, r: int ):
        c = 0
        l = self._layout
        lbl = BaseLabel( "Neues Mietverhältnis" )
        lbl.setFont( QFont( "Arial", 12, QFont.Bold ) )
        l.addWidget( lbl, r, c )

        r += 1
        l.addWidget( self._neuesMietvh, r, c, 1, 2 )

###############  MieterwechselDialog  ##########################
class MieterwechselDialog( OkCancelDialog ):
    def __init__(self, miet_obj:str, parent=None):
        OkCancelDialog.__init__( self, parent )
        self.setWindowTitle( miet_obj )
        self._view = MieterwechselView()
        self.addWidget( self._view, 0 )

#################################################################


def test():
    dlg = MieterwechselDialog( "NK_Volkerstal" )
    dlg.exec_()

if __name__ == "__main__":
    app = QApplication()
    test()