from PySide2.QtCore import QSize
from PySide2.QtWidgets import QMenu, QWidget

from base.baseqtderivates import BaseAction
from base.messagebox import ErrorBox, InfoBox
from generictable_stuff.okcanceldialog import OkCancelDialog2
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XMietobjektAuswahl
from v2.mietobjekt.mietobjektlogic import MietobjektLogic, MietobjektTableModel
from v2.mietobjekt.mietobjektview import MietobjektAuswahlTableView, MietobjektView, MietobjektDialog


######################   MietobjektAuswahl   #########################
class MietobjektAuswahl:
    def __init__( self ):
        self._selectedObject = None

    def selectMieter( self ) -> XMietobjektAuswahl:
        """
        Lässt aus einer Liste von Objekten mit Mietern eine Auswahl von einer oder keiner Zeile treffen.
        Die Liste ist nach Mietern sortiert.
        Wenn eine Auswahl getroffen wurde, wird ein XMietobjektAuswahl-Objekt zurückgegeben, sonst None
        :return:
        """
        x:XMietobjektAuswahl = self._selectMietobjekt( sortByMieter=True )
        return x

    def selectMietobjekt( self ) -> XMietobjektAuswahl:
        """
        Lässt aus einer Liste von Objekten mit Mietern eine Auswahl von einer oder keiner Zeile treffen.
        Die Liste ist nach Mietobjekten sortiert.
        Wenn eine Auswahl getroffen wurde, wird ein XMietobjektAuswahl-Objekt zurückgegeben, sonst None
        :return:
        """
        x:XMietobjektAuswahl = self._selectMietobjekt( sortByMieter=False )
        return x

    def _selectMietobjekt( self, sortByMieter=False ) -> XMietobjektAuswahl or None:
        def onOk():
            v = dlg.getWidget( 0 )
            row = v.getFirstSelectedRow()
            tm: MietobjektTableModel = v.model()
            self._selectedObject = tm.getElement( row )
            dlg.accept()
        def onCancel():
            self._selectedObject = None
            dlg.reject()

        dlg = self._getAuswahlDialog( sortByMieter )
        dlg.ok_pressed.connect( onOk )
        dlg.cancel_pressed.connect( onCancel )
        dlg.exec_()
        return self._selectedObject

    @staticmethod
    def _getAuswahlDialog( sortByMieter=False ) -> OkCancelDialog2:
        logic = MietobjektLogic()
        tm = logic.getMietobjektTableModel()
        v = MietobjektAuswahlTableView()
        v.setModel( tm )
        w = v.getPreferredWidth()
        h = 800
        v.resize( QSize( w, h ) )
        dlg = OkCancelDialog2( "Mieter auswählen" if sortByMieter else "Mietobjekt auswählen" )
        dlg.setOkButtonText( "Auswählen" )
        dlg.addWidget( v, 0 )
        dlg.resize( QSize( v.width(), v.height() ) )
        if sortByMieter:
            tm.sort( 2 )
        return dlg

######################   MietobjektController   #########################
class MietobjektController( IccController ):
    def __init__( self, mobj_id:str=None ):
        IccController.__init__( self )
        self._logic = MietobjektLogic()

    def createGui( self ) -> QWidget:
        pass

    def getMenu( self ) -> QMenu or None:
        """
        Jeder Controller liefert dem MainController ein Menu, das im MainWindow in der Menubar angezeigt wird
        :return:
        """
        menu = QMenu( "Mietobjekt" )
        action = BaseAction( "Objektstammdaten...", parent=menu )
        action.triggered.connect( self.onObjektStamdaten )
        menu.addAction( action )
        return menu

    def onObjektStamdaten( self ):
        ausw = MietobjektAuswahl()
        xmobj_sel = ausw.selectMietobjekt()
        xmobj_ext = self._logic.getMietobjektExt( xmobj_sel.mobj_id )
        v = MietobjektView( xmobj_ext )
        v.edit_miete.connect( self.onEditMiete )
        v.edit_mieter.connect( self.onEditMieter )
        v.edit_hausgeld.connect( self.onEditHausgeld )
        dlg = MietobjektDialog( v, xmobj_ext.master_name + " / " + xmobj_ext.mobj_id )
        dlg.exec_()

    def onEditMieter( self, mv_id:str ):
        self._notYetImplemented( " '%s': Funktion Mieter Ändern noch nicht realisiert" % mv_id )

    def onEditMiete( self, mv_id:str ):
        self._notYetImplemented( "'%s': Funktion Miete Ändern noch nicht realisiert" % mv_id )

    def onEditHausgeld( self, mobj_id:str ):
        self._notYetImplemented( "'%s': Funktion Hausgeld Ändern noch nicht realisiert" % mobj_id )

    def _notYetImplemented( self, msg:str ):
        box = InfoBox( "Not yet implemented", msg, "", "OK" )
        box.exec_()



def test():
    from PySide2.QtWidgets import QWidget, QMenu, QApplication
    app = QApplication()
    c = MietobjektController()
    c.onObjektStamdaten()
    app.exec_()

def test2():
    class A:
        def __init__( self ):
            self._marzipan = "naja"
        def fncA( self ):
            def onOk():
                marzipan = "gut"
                self._marzipan = "lecker"
            marzipan = "süss"
            onOk()
            return marzipan, self._marzipan

    a = A()
    m1, m2 = a.fncA()
    print( m1, m2 )
