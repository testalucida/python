#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import libs
import utils
from functools import partial
from wvframe import WV, WohnungAction
from business import DataProvider, WvException
from wohnungdetailscontroller import WohnungDetailsController
from rgcontroller import RechnungController
from mtleacontroller import MtlEinAusController
from sonsteacontroller import SonstEinAusController
from grundsteuercontroller import GrundsteuerController
from stammdatenview import StammdatenAction
from stammdatencontroller import StammdatenController
from mietverhaeltniscontroller import MietverhaeltnisController
from veranlagungcontroller import VeranlagungController
from wohnungdialogcontroller import WohnungDialogController
from wohnungdialog import WohnungDialog
from anlagevauswahldialog import AnlageVAuswahlDialog
from interfaces import XWohnungDaten
from anlagevcreatorbatch import AnlageVCreatorBatch
from mywidgets import CheckableItemList

class WvController:
    def __init__(self, wv: WV):
        self._wv = wv
        self._dataProvider = DataProvider()
        self._wohnungdetailscontroller = None
        self._rgcontroller = None
        self._mtleacontroller = None
        self._sonsteacontroller = None
        self._grundsteuercontroller = None
        self._stammdatencontroller = None
        self._mietverhaeltniscontroller = None
        self._veranlagungcontroller = None

    def startWork(self) -> None:
        self._wv.registerWohnungActionCallback(self.onWohnungMenuAction)
        self._wv.registerAnlageVActionCallback(self.onAnlageVAction)
        self._connect()
        self._loadTree()

        self._wohnungdetailscontroller = WohnungDetailsController(self._dataProvider,
                                                self._wv.getWohnungDetailsView())

        self._wohnungdetailscontroller.startWork()

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

        self._mietverhaeltniscontroller = MietverhaeltnisController(
                        self._dataProvider, self._wv.getMietverhaeltnisView())
        self._mietverhaeltniscontroller.startWork()

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
        # import os
        # #check if a configuration file exists. If so, connect remote, else local.
        # scriptpath = os.path.realpath(__file__)
        # scriptdir = scriptpath.replace('/wvcontroller.py', '')
        # configfile = scriptdir + '/connect_remote'
        # user = 'test'
        # if os.path.isfile(configfile): user = 'd02bacec'
        #self._dataProvider.connect(user)
        self._dataProvider.connect(utils.getUser())

    def _loadTree(self):
        whg_list = self._dataProvider.getWohnungsUebersicht()
        self._wv.populateWohnungenTree(whg_list)
        self._wv.registerWohnungClickCallback(self._onWohnungClicked)
        self._wv.registerNoWohnungClickCallback(self._onNoWohnungClicked)

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

    def onAnlageVAction(self) -> None:
        def _onOk(selectedVj, whgItemList: CheckableItemList):
            def _removeWhgFromList(whg_id: int):
                for whg in whgList:
                    if int(whg['whg_id']) == whg_id:
                        whgList.remove(whg)
                        return
                raise ValueError('_removeWhgFromList: whg_id ' +
                                 str(whg_id) + ' not found.')

            dlg.destroy()
            #remove the non-checked wohnungen:
            for whgItem in whgItemList.getItems():
                if not whgItem.check:
                    _removeWhgFromList(whgItem.id)

            batch = AnlageVCreatorBatch(int(selectedVj), self._dataProvider, whgList)
            try:
                batch.startWork()
            except WvException as e:
                #traceback.print_exc(file=sys.stdout)
                messagebox.showerror('Verarbeitung wird abgebrochen', e.toString())
                return


        whgList: List[Dict[str, str]] = self._dataProvider.getWohnungsUebersicht()
        itemList = CheckableItemList()
        for whg in whgList:
            bez = whg['ort'] + ', ' + whg['strasse'] + ' / ' + whg['whg_bez']
            itemList.appendItem(bez, int(whg['whg_id']), True)

        dlg = AnlageVAuswahlDialog(self._wv, itemList)
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
        self._wohnungdetailscontroller.wohnungSelected(-1)
        self._rgcontroller.wohnungSelected(-1)
        self._mtleacontroller.wohnungSelected(-1)
        self._sonsteacontroller.wohnungSelected(-1)
        self._grundsteuercontroller.wohnungSelected(-1)
        self._mietverhaeltniscontroller.clear()
        self._stammdatencontroller.clear()
        self._veranlagungcontroller.clear()

    def _onWohnungClicked(self, whg_id:int) -> None:
        root = self._wv.master
        root.config(cursor='clock')
        root.update()
        self._wohnungdetailscontroller.wohnungSelected(whg_id)
        self._rgcontroller.wohnungSelected(whg_id)
        self._mtleacontroller.wohnungSelected(whg_id)
        self._sonsteacontroller.wohnungSelected(whg_id)
        self._grundsteuercontroller.wohnungSelected(whg_id)
        self._stammdatencontroller.wohnungSelected(whg_id)
        self._mietverhaeltniscontroller.wohnungSelected(whg_id)
        self._veranlagungcontroller.wohnungSelected(whg_id)
        root.configure(cursor='')
        root.update()

    def _onNoWohnungClicked(self):
        self._stammdatencontroller.clear()
        self._wohnungdetailscontroller.clear()
        self._rgcontroller.clear()
        self._mtleacontroller.clear()
        self._sonsteacontroller.clear()
        self._grundsteuercontroller.clear()
        self._mietverhaeltniscontroller.clear()
        self._veranlagungcontroller.clear()
