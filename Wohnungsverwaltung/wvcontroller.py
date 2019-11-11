#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, traceback
from tkinter import messagebox
from functools import partial
from wvframe import WV, WohnungAction, AnlageVAction
from business import DataProvider, WvException
from rgcontroller import RechnungController
from mtleacontroller import MtlEinAusController
from sonsteacontroller import SonstEinAusController
from grundsteuercontroller import GrundsteuerController
from stammdatenview import StammdatenAction
from stammdatencontroller import StammdatenController
from veranlagungcontroller import VeranlagungController
from wohnungdialogcontroller import WohnungDialogController
from wohnungdialog import WohnungDialog
from vjdialog import VjDialog
from interfaces import XWohnungDaten
from anlagevcreatorbatch import AnlageVCreatorBatch

class WvController:
    def __init__(self, wv: WV):
        self._wv = wv
        self._dataProvider = DataProvider()
        self._rgcontroller = None
        self._mtleacontroller = None
        self._sonsteacontroller = None
        self._grundsteuercontroller = None
        self._stammdatencontroller = None
        self._veranlagungcontroller = None

    def startWork(self) -> None:
        self._wv.registerWohnungActionCallback(self.onWohnungMenuAction)
        self._wv.registerAnlageVActionCallback(self.onAnlageVAction)
        self._connect()
        self._loadTree()

        self._rgcontroller = RechnungController(self._dataProvider,
                                                self._wv.getRechnungTableView())
        self._rgcontroller.startWork()

        self._mtleacontroller = MtlEinAusController(self._dataProvider,
                                                    self._wv.getMonatlicheTableView())
        self._mtleacontroller.startWork()

        self._sonsteacontroller = SonstEinAusController(self._dataProvider,
                                                    self._wv.getSonstigeTableView())
        self._sonsteacontroller.startWork()

        self._grundsteuercontroller = GrundsteuerController(self._dataProvider,
                                                        self._wv.getGrundsteuerTableView())
        self._grundsteuercontroller.startWork()

        self._stammdatencontroller = StammdatenController(self._dataProvider,
                                                          self._wv.getStammdatenView())
        self._stammdatencontroller.startWork()

        self._veranlagungcontroller = VeranlagungController(self._dataProvider,
                                                            self._wv.getVeranlagungView())
        self._veranlagungcontroller.startWork()

        self._stammdatencontroller.\
            registerWohnungActionCompletedCallback(
                self._veranlagungcontroller.onWohnungChanged)

        self._veranlagungcontroller.\
            registerWohnungDatenChangedCallback(
                self._stammdatencontroller.onWohnungDatenChangedByOthers)

    def _connect(self):
        import os
        #check if a configuration file exists. If so, connect remote, else local.
        scriptpath = os.path.realpath(__file__)
        scriptdir = scriptpath.replace('/wvcontroller.py', '')
        configfile = scriptdir + '/connect_remote'
        user = 'test'
        if os.path.isfile(configfile): user = 'd02bacec'
        self._dataProvider.connect(user)

    def _loadTree(self):
        whg_list = self._dataProvider.getWohnungsUebersicht()
        self._wv.populateWohnungenTree(whg_list)
        self._wv.registerWohnungClickCallback(self._onWohnungClicked)

    def onWohnungMenuAction(self, whg_id: int, action: WohnungAction):
        if action == WohnungAction.delete:
            self._deleteWohnung(whg_id)
        elif(action == WohnungAction.new):
            dlg = WohnungDialog(self._wv)
            dlg.grab_set()
            ctrl = StammdatenController(self._dataProvider, dlg.getView())
            #ctrl.registerActionCompletedCallback(lambda: dlg.close())
            ctrl.registerWohnungActionCompletedCallback(
                partial(self._wohnungActionCompleted, dlg))
            ctrl.startWork()

    def onAnlageVAction(self, action: AnlageVAction) -> None:
        def _onOk(selectedVj):
            dlg.destroy()
            if action == AnlageVAction.all:
                batch = AnlageVCreatorBatch(int(selectedVj), self._dataProvider)
                try:
                    batch.startWork()
                except WvException as e:
                    #traceback.print_exc(file=sys.stdout)
                    messagebox.showerror('Verarbeitung wird abgebrochen', e.toString())
                    return
            else:
                # todo
                pass
            return

        dlg = VjDialog(self._wv)
        dlg.registerCallback(_onOk)

    def _wohnungActionCompleted(self, dlg: WohnungDialog,
                                action: StammdatenAction,
                                xdata: XWohnungDaten) -> None:
        dlg.close()
        if action == StammdatenAction.save_changes: # new wohnung created
            self._loadTree()
        self._wv.selectWohnungItem(xdata.whg_id)

    def _deleteWohnung(self, whg_id: int) -> None:
        self._dataProvider.deleteWohnung(whg_id)
        self._loadTree()

        self._rgcontroller.wohnungSelected(-1)
        self._mtleacontroller.wohnungSelected(-1)
        self._sonsteacontroller.wohnungSelected(-1)
        self._grundsteuercontroller.wohnungSelected(-1)
        self._stammdatencontroller.clear()
        self._veranlagungcontroller.clear()

    def _onWohnungClicked(self, whg_id:int) -> None:
        root = self._wv.master
        root.config(cursor='clock')
        root.update()
        self._rgcontroller.wohnungSelected(whg_id)
        self._mtleacontroller.wohnungSelected(whg_id)
        self._sonsteacontroller.wohnungSelected(whg_id)
        self._grundsteuercontroller.wohnungSelected(whg_id)
        self._stammdatencontroller.wohnungSelected(whg_id)
        self._veranlagungcontroller.wohnungSelected(whg_id)
        root.configure(cursor='')
        root.update()
