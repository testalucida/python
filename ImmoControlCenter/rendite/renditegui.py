from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QSize, Qt, QDate, QPoint, Signal
from PySide2.QtGui import QIcon, QDoubleValidator, QFont, QIntValidator
from PySide2.QtWidgets import QWidget, QComboBox, QLineEdit, QCheckBox, QPushButton, QCalendarWidget, \
    QVBoxLayout, QDialog, QBoxLayout, QHBoxLayout, QTextEdit, QSpinBox, QLabel, QTableView, QMessageBox, \
    QAbstractItemView
from typing import List

from generictable_stuff.generictableviewdialog import CustomTableView

############  RenditeTableView  #####################
from rendite.renditetablemodel import RenditeTableModel


class RenditeTableView( CustomTableView ):
    def __init__( self, parent=None ):
        CustomTableView.__init__( self, parent )

################  RenditeView  ######################
class RenditeView( QWidget ):
    betrachtungsjahrChanged = Signal( int )

    def __init__( self, model:RenditeTableModel, parent=None ):
        QWidget.__init__( self, parent )
        self._mainLayout = QtWidgets.QGridLayout()
        self._toolbarLayout = QHBoxLayout()
        self._cboBetrachtungsjahr = QtWidgets.QComboBox()
        self._tv = CustomTableView()
        self._btnClose = QPushButton( "Schließen" )
        self._btnClose.clicked.connect( self.close )
        self._createGui()
        if model:
            self.setTableModel( model )

    def _createGui( self ):
        self._assembleToolbar()
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._mainLayout.addWidget( self._tv, 1, 0 )
        self._mainLayout.addWidget( self._btnClose, 2, 0 )
        self.setLayout( self._mainLayout )

    def _assembleToolbar( self ):
        #### Combobox Betrachtungsjahr
        font = QFont( "Arial", 14, weight=QFont.Bold )
        self._cboBetrachtungsjahr.setFont( font )
        self._cboBetrachtungsjahr.setToolTip(
            "Jahr, für das die Renditen angezeigt werden." )
        self._cboBetrachtungsjahr.currentIndexChanged.connect( self._onBetrachtungsjahrChanged )
        self._toolbarLayout.addWidget( self._cboBetrachtungsjahr, stretch=0, alignment=Qt.AlignLeft )

    def _onBetrachtungsjahrChanged( self, arg:int ):
        print( arg )
        self.betrachtungsjahrChanged.emit( int( self._cboBetrachtungsjahr.currentText() ) )

    def setBetrachtungsjahre( self, jahre:List[int] ):
        """
        setzt die Liste der auswählbaren Jahre für die Buchungsjahr-Combobox
        :param jahre:
        :return:
        """
        for jahr in jahre:
            self._cboBetrachtungsjahr.addItem( str( jahr ) )

    def setBetrachtungsjahr( self, jahr: int ) -> None:
        """
        setzt das Jahr, das in der Buchungsjahr-Combobox anzuzeigen ist
        :param jahr:
        :return:
        """
        self._cboBetrachtungsjahr.setCurrentText( str( jahr ) )

    def setTableModel( self, model:RenditeTableModel ):
        self._tv.setModel( model )

    def getModel( self ) -> RenditeTableModel:
        return self._tv.model()

##########################################################################
def onChangeBetrachtungsjahr( jahr:int ):
    print( "neues Betrachtungsjahr: ", str( jahr ) )


def test():
    import sys
    app = QtWidgets.QApplication( sys.argv )
    v = RenditeView()
    v.setBetrachtungsjahre( (2020, 2021) )
    v.setBetrachtungsjahr( 2021 )
    v.betrachtungsjahrChanged.connect( onChangeBetrachtungsjahr )

    #sav.setBuchungsjahrChangedCallback( onChangeBuchungsjahr )
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()