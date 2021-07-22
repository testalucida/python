from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from generictable_stuff.okcanceldialog import OkCancelDialog
from qtderivates import AuswahlDialog, BaseEdit, SmartDateEdit


##############  MietobjektAuswahlDialog  #######################
class MietobjektAuswahldialog( AuswahlDialog ):
    def __init__(self, parent=None):
        AuswahlDialog.__init__( self, "Auswahl des Mietobjekts", parent )

class MieterwechselView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self._layout = QGridLayout()
        self._edLetzterMieter = BaseEdit()
        self._edEndeMietverh = BaseEdit()
        self._sdBeginnMietverh = SmartDateEdit()
        self._createGui()

    def _createGui( self ):
        l = self._layout
        r = c = 0
        lbl = QLabel( "letzter/aktueller Mieter: " )
        l.addWidget( lbl, r, c )
        self._edLetzterMieter.setReadOnly( True )
        l.addWidget( self._edLetzterMieter, r, c+1 )
        r += 1
        lbl = QLabel( "Ende des Mietverhältnisses: " )
        l.addWidget( lbl, r, c )
        self._edEndeMietverh.setReadOnly( True )
        self._edEndeMietverh.setMaximumWidth( 100 )
        l.addWidget( self._edEndeMietverh, r, c+1 )

        r+=1
        l.addWidget( QLabel( "" ), r, c )

        r+=1
        lbl = QLabel( "Beginn des neuen Mietverhältnisses: " )
        l.addWidget( lbl, r, c )
        self._sdBeginnMietverh.setMaximumWidth( 100 )
        l.addWidget( self._sdBeginnMietverh, r, c+1 )

        self.setLayout( self._layout )

###############  MieterwechselDialog  ##########################
class MieterwechselDialog( OkCancelDialog ):
    def __init__(self, miet_obj:str, parent=None):
        OkCancelDialog.__init__( self, parent )
        self.setWindowTitle( miet_obj )
        self._view = MieterwechselView()
        self.addWidget( self._view, 0 )

#################################################################


def test():
    dlg = MieterwechselDialog()
    dlg.exec_()

if __name__ == "__main__":
    app = QApplication()
    test()