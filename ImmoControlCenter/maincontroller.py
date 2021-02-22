from typing import List, Dict, Tuple

from PySide2.QtCore import QAbstractItemModel

from business import BusinessLogic
from constants import einausart
from datehelper import getCurrentYear
from mdisubwindow import MdiSubWindow
from immocentermainwindow import ImmoCenterMainWindow, MainWindowAction
from checkcontroller import MdiChildController, MietenController, HGVController
from sollzahlungencontroller import SollzahlungenController, SollType
from sonstauscontroller import SonstAusController
from sumfieldsprovider import SumFieldsProvider


class MainController:
    def __init__(self, win:ImmoCenterMainWindow ):
        self._mainwin:ImmoCenterMainWindow = win
        datum, text = BusinessLogic.inst().getLetzteBuchung()
        win.setLetzteBuchung( datum, text )
        win.setActionCallback( self.onMainWindowAction )
        win.setShutdownCallback( self.onShutdown )

        self._mietenCtrl:MietenController = MietenController()
        self._mietenCtrl.changedCallback = self.onViewChanged
        self._mietenCtrl.savedCallback = self.onViewSaved

        self._hgvCtrl:HGVController = HGVController()
        self._hgvCtrl.changedCallback = self.onViewChanged
        self._hgvCtrl.savedCallback = self.onViewSaved

        self._sonstAusCtrl:SonstAusController = SonstAusController()
        self._sonstAusCtrl.changedCallback = self.onViewChanged
        self._sonstAusCtrl.savedCallback = self.onViewSaved

        self._sollMietenCtrl = SollzahlungenController( SollType.MIETE_SOLL )
        self._sollHausgelderCtrl = SollzahlungenController( SollType.HAUSGELD_SOLL )

        self._nChanges = 0  # zählt die Änderungen, damit nach Speichern-Vorgängen das Sternchen nicht zu früh entfernt wird.

        #TODO: _viewsandcontroller bereinigen, wenn ein View geschlossen wird
        self._viewsandcontroller:[Dict[MdiSubWindow, MdiChildController]] = {}
        self._someViewChanged:bool = False
        self._x, self._y = 0, 0

        self._provideSumFields()

    def _provideSumFields( self ):
        #sumMieten, sumAusgaben, sumHGV = BusinessLogic.inst().getSummen()
        sfa:SumFieldsProvider = SumFieldsProvider.inst()
        sfa.setSumFields()
        #sfa.setSumMieten( sumMieten )
        #sfa.setSumAusgaben( sumAusgaben )
        #sfa.setSumHGV( sumHGV )

    def showStartViews( self ):
        self.showMieteView()
        self.showHGVView()
        self.showSonstAusView()

    def onMainWindowAction( self, action:MainWindowAction ):
        switcher = {
            MainWindowAction.NEW_WINDOW: self._newWindow,
            MainWindowAction.SAVE_ACTIVE_VIEW: self._saveActiveView,
            MainWindowAction.SAVE_ALL: self._saveAll,
            MainWindowAction.PRINT_ACTIVE_VIEW: self._printActiveView,
            MainWindowAction.OPEN_MIETE_VIEW: self.showMieteView,
            MainWindowAction.OPEN_HGV_VIEW: self.showHGVView,
            MainWindowAction.FOLGEJAHR: self.createFolgejahr,
            MainWindowAction.OPEN_SOLL_MIETE_VIEW: self.showSollMietenView,
            MainWindowAction.OPEN_SOLL_HG_VIEW: self.showSollHausgelderView,
            MainWindowAction.OPEN_NKA_VIEW: self.showNKAbrechnungenView,
            MainWindowAction.OPEN_HGA_VIEW: self.showHGAbrechnungenView,
            MainWindowAction.RESIZE_MAIN_WINDOW: self.resizeAllViews,
            MainWindowAction.EXPORT_CSV: self.exportToCsv
        }
        fnc = switcher.get( action )
        try:
            fnc()
        except:
           self._mainwin.showException( "function call failed", "MainController.onMainWindowAction():\nconcerned action: '%s'." % (str( action ) ) )

    def anyViewChanged( self ) -> bool:
        return self._someViewChanged

    def onViewChanged( self ):
        self._mainwin.setWindowTitle( "ImmoControlCenter *" )
        self._someViewChanged = True
        self._nChanges += 1

    def onViewSaved( self ):
        self._nChanges -= 1
        if self._nChanges == 0:
            self._mainwin.setWindowTitle( "ImmoControlCenter" )
            self._someViewChanged = False

    def arrange( self, *views ):
        print( views )

    def _newWindow( self ):
        pass

    def _saveActiveView( self ):
        child:MdiSubWindow = self._mainwin.mdiArea.activeSubWindow()
        #child.installEventFilter( self )
        ctrl:MdiChildController = self._viewsandcontroller[child]
        ctrl.save()
        self._mainwin.setWindowTitle( "ImmoControlCenter" )
        self._someViewChanged = False

    def _saveAll( self ):
        self._setLetzteBuchung()

    def _printActiveView( self ):
        pass

    def showMieteView( self ):
        #TODO prüfen, ob schon ein MieteView vorhanden ist. Wenn ja, diesen in den Vordergrund bringen.
        #     Nur wenn nein, einen anlegen.
        # if <exists miete view:
        #     bring to front
        # else:
        self.createMieteViewAndShow()

    def createMieteViewAndShow( self ):
        subwin = self._mietenCtrl.createSubwindow()
        self._installView( subwin, self._mietenCtrl )
        w, h = self.getMainWindowSize()
        w2 = w/2
        subwin.setGeometry( 0, 0, w2, h ) #h-22 )
        subwin.show()

    def showHGVView( self ):
        # TODO prüfen, ob schon ein HGV-View vorhanden ist. Wenn ja, diesen in den Vordergrund bringen.
        #     Nur wenn nein, einen anlegen.
        # if <exists hgv view:
        #     bring to front
        # else:
        self.createHgvViewAndShow()

    def createHgvViewAndShow( self ):
        subwin = self._hgvCtrl.createSubwindow()
        self._installView( subwin, self._hgvCtrl )
        w, h = self.getMainWindowSize()
        w2 = w / 2
        x = w2
        # sonstaussubwin = self.getView( self._sonstAusCtrl )
        # y = h - sonstaussubwin.height()
        # h2 = h - y - 25
        h2 = h/2
        y = h2
        subwin.setGeometry( x, y, w2, h2 )
        subwin.show()

    def showSonstAusView( self ):
        self.createSonstAusViewAndShow()

    def createSonstAusViewAndShow( self ):
        subwin = self._sonstAusCtrl.createSubwindow()
        self._installView( subwin, self._sonstAusCtrl )
        w, h = self.getMainWindowSize()
        w2 = w / 2
        x = w2
        subwin.setGeometry( x, 0, w2, h / 2 )
        subwin.show()

    def showSollMietenView( self ):
        # TODO: prüfen, ob shon ein SollzahlungenView vorhanden ist. Nur wenn nein, einen anlegen.
        self.createSollMietenViewAndShow()

    def createSollMietenViewAndShow( self ):
        subwin = self._sollMietenCtrl.createSubwindow()
        self._installView( subwin, self._sollMietenCtrl )
        # w, h = self.getMainWindowSize()
        subwin.setGeometry( 10, 10, 400, 400 )
        subwin.show()

    def showSollHausgelderView( self ):
        # TODO: prüfen, ob shon ein SollzahlungenView vorhanden ist. Nur wenn nein, einen anlegen.
        self.createSollHausgelderViewAndShow()

    def showNKAbrechnungenView( self ):
        self.createNkaViewAndShow()

    def showHGAbrechnungenView( self ):
        self.createHgaViewAndShow()

    def resizeAllViews( self ):
        # wird gerufen, wenn das MainWindow resized wird.
        geom = self._mainwin.geometry()
        #print( "resized. new size: ", geom.width(), " x ", geom.height() )

    def exportToCsv( self ):
        child: MdiSubWindow = self._mainwin.mdiArea.activeSubWindow()
        model: QAbstractItemModel = child.widget().getModel()
        try:
            BusinessLogic.inst().exportToCsv( model )
        except Exception as ex:
            child.showException( "Export als .csv-Datei", str( ex ), "in MainController.exportToCsv()" )

    def onShutdown( self ) -> bool:
        self._setLetzteBuchung()
        return True

    def _setLetzteBuchung( self ):
        d = self._mainwin.getLetzteBuchung()
        try:
            BusinessLogic.inst().setLetzteBuchung( d["datum"], d["text"] )
        except Exception as ex:
            self._mainwin.showException( str( ex ), "MainController.onShutdown()" )

    def createSollHausgelderViewAndShow( self ):
        subwin = self._sollHausgelderCtrl.createSubwindow()
        self._installView( subwin, self._sollHausgelderCtrl )
        subwin.setGeometry( 20, 20, 1000, 400 )
        subwin.show()

    def createNkaViewAndShow( self ):
        print( "MainController.createNkaViewAndShow" )
        #Todo

    def createHgaViewAndShow( self ):
        print( "MainController.createHgaViewAndShow" )
        #Todo

    def _installView( self, subwin:MdiSubWindow, ctrl:MdiChildController ):
        #subwin.addQuitCallback( self.onCloseSubWindow )
        self._viewsandcontroller[subwin] = ctrl
        self._mainwin.addMdiChild( subwin )

    def getMainWindowSize( self ) -> Tuple:
        geom = self._mainwin.mdiArea.geometry()
        return geom.width(), geom.height()

    def createFolgejahr( self ):
        y = getCurrentYear()
        y += 1
        if not BusinessLogic.inst().existsEinAusArt( einausart.MIETE, y ):
            BusinessLogic.inst().createMtlEinAusJahresSet( y )
            self._mietenCtrl.addJahr( y )
            self._hgvCtrl.addJahr( y )
        #TODO testen!!!!!

    def getView( self, ctrl:MdiChildController ) -> MdiSubWindow:
        for w, c in self._viewsandcontroller.items():
            if c == ctrl:
                return w
        raise Exception( "internal error: can't find MdiSubWindow for Controller " + ctrl.getViewTitle() )

    # def showSubWindow( self, subwin:MdiSubWindow, x:int, y:int, w:int, h:int ):
    #     subwin.setGeometry( self._x, self._y, 1200, geom.height() / 5 * 4 )
    #     self._x += 20
    #     self._y += 20
    #     subwin.show()

    def onCloseSubWindow( self, window:MdiSubWindow ) -> bool:
        self._viewsandcontroller.pop( window )
        return True

    def _exit( self ):
        pass

