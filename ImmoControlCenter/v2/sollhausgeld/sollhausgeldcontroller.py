from abc import abstractmethod

from PySide2.QtCore import Slot, QSize
from PySide2.QtWidgets import QApplication, QDialog, QMenu

from base.baseqtderivates import BaseAction
from base.basetablemodel import BaseTableModel
from base.basetableview import BaseTableView
from generictable_stuff.okcanceldialog import OkCancelDialog, OkDialog
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame
from v2.icc.interfaces import XSollHausgeld
from v2.sollhausgeld.sollhausgeldeditcontroller import SollHausgeldEditController
from v2.sollhausgeld.sollhausgeldlogic import SollHausgeldLogic, SollHausgeldTableModel
from v2.sollhausgeld.sollhausgeldview import SollHausgeldView, SollHausgeldDialog

class SollzahlungenController( IccController ):
    _menu = ""
    _menu_returned = False
    def __init__( self ):
        IccController.__init__( self )
        #self._menu: QMenu = None

    def getMenu( self ) -> QMenu or None:
        if not SollzahlungenController._menu_returned:
            SollzahlungenController._menu = QMenu( "Sollzahlungen")
        action = self.getAction( SollzahlungenController._menu )
        SollzahlungenController._menu.addAction( action )
        SollzahlungenController._menu.addSeparator()
        if not SollzahlungenController._menu_returned:
            SollzahlungenController._menu_returned = True
            return SollzahlungenController._menu
        return None

    def createGui( self ) -> IccCheckTableViewFrame:
        pass

    def showSollzahlungenDialog( self, tm:BaseTableModel, title:str ):
        v = BaseTableView()
        v.setModel( tm, selectRows=True, singleSelection=False )
        v.setAlternatingRowColors( True )
        dlg = OkDialog( title )
        dlg.addWidget( v, 0 )
        w = v.getPreferredWidth()
        h = v.getPreferredHeight()
        dlg.resize( QSize( w, h + 25 ) )
        dlg.move( self.getMainWindow().cursor().pos() )
        dlg.exec_()

    @abstractmethod
    def getAction( self, menu:QMenu ) -> BaseAction:
        pass

#############  SollMieteController  #####################
class SollHausgeldController( SollzahlungenController ):
    def __init__( self ):
        SollzahlungenController.__init__( self )
        self._logic = SollHausgeldLogic()

    def onAlleSollHausgelder( self ):
        tm:SollHausgeldTableModel = self._logic.getAllSollHausgelder()
        self.showSollzahlungenDialog( tm, "Alle Soll-Hausgelder" )

    def getAction( self, menu:QMenu ) -> BaseAction:
        action = BaseAction( "Sollhausgelder anzeigen...", parent=menu )
        action.triggered.connect( self.onAlleSollHausgelder )
        return action

    def showHgvAndRueZuFue( self, mobj_id:str, jahr:int, monthNumber:int ):
        """
        Zeigt die SollHausgeld-View mit den gewünschten Daten
        :param mobj_id:
        :param jahr:
        :param monthNumber: 1 -> Januar, ... , 12 -> Dezember
        :return:
        """
        x:XSollHausgeld = self._logic.getSollHausgeldAm( mobj_id, jahr, monthNumber )
        v = SollHausgeldView( x )
        dlg = SollHausgeldDialog( v )
        dlg.setWindowTitle( "Soll-Hausgeld für '%s' (%s)" % (x.weg_name, x.mobj_id) )
        dlg.edit_clicked.connect( lambda: self.onEditSollHausgeld( x, v ) )
        if dlg.exec_() == QDialog.Accepted:
            # Die Bemerkung könnte geändert sein. Keine Validierung, direkt an die Logik zum Speichern übergeben.
            v.applyChanges()
            self._logic.updateSollHausgeldBemerkung( x.shg_id, x.bemerkung )


    def onEditSollHausgeld( self, x: XSollHausgeld, view: SollHausgeldView ):
        """
        Im SollHausgeldDialog wurde der Button "Folge-Soll erfassen oder ändern..." gedrückt.
        Wir instanzieren den SollHausgeldEditController und lassen ihn die Anlage eines neuen
        Hausgeld-Intervalls behandeln
        :param x: das derzeitige XSollHausgeld-Objekt
        :param view: die SollHausgeldView, in der o.a. Button gedrückt wurde.
        :return:
        """
        def onBisChanged( bis: str ):
            view.setBis( bis )
        shgEditCtrl = SollHausgeldEditController()
        shgEditCtrl.endofcurrentsoll_modified.connect( onBisChanged )
        shgEditCtrl.handleFolgeSollHausgeld( x )

def test():
    app = QApplication()
    ctrl = SollHausgeldController()
    ctrl.showHgvAndRueZuFue( "remigius", 2023, 3 )
