#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from wvframe import WV
from business import DataProvider
from rgcontroller import RechnungController
from mtleacontroller import MtlEinAusController

class WvController:
    def __init__(self, wv: WV):
        self._wv = wv
        self._dataProvider = DataProvider()
        self._rgcontroller = None
        self._mtleacontroller = None

    def startWork(self) -> None:
        self._connect()
        self._loadTree()
        self._rgcontroller = RechnungController(self._dataProvider,
                                                self._wv.getRechnungTableView())
        self._rgcontroller.startWork()
        self._mtleacontroller = MtlEinAusController(self._dataProvider,
                                                    self._wv.getMonatlicheTableView())
        self._mtleacontroller.startWork()

    def _connect(self):
        #todo: Login-Dialog
        self._dataProvider.connect('martin', 'fuenf55')

    def _loadTree(self):
        whg_list = self._dataProvider.getWohnungsUebersicht()
        self._wv.populateWohnungenTree(whg_list)
        self._wv.registerWohnungClickCallback(self._onWohnungClicked)

    def _onWohnungClicked(self, whg_id:int) -> None:
        self._rgcontroller.wohnungSelected(whg_id)
        self._mtleacontroller.wohnungSelected(whg_id)
