#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from wvframe import WV
from business import DataProvider
from rgcontroller import RechnungController
from mtleacontroller import MtlEinAusController
from sonsteacontroller import SonstEinAusController
from grundsteuercontroller import GrundsteuerController
from stammdatencontroller import StammdatenController
from veranlagungcontroller import VeranlagungController

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
        self._veranlagungcontroller = VeranlagungController(self._dataProvider,
                                                            self._wv.getVeranlagungView())
        self._veranlagungcontroller.startWork()

    def _connect(self):
        #todo: Login-Dialog
        self._dataProvider.connect('martin', 'fuenf55')

    def _loadTree(self):
        whg_list = self._dataProvider.getWohnungsUebersicht()
        self._wv.populateWohnungenTree(whg_list)
        self._wv.registerWohnungClickCallback(self._onWohnungClicked)

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
