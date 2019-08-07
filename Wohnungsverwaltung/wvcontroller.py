#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from wvframe import WV
from business import DataProvider
from rgcontroller import RechnungController

class WvController:
    def __init__(self, wv: WV):
        self._wv = wv
        self._dataProvider = DataProvider()
        self._rgcontroller = None

    def startWork(self) -> None:
        self._connect()
        self._loadTree()
        self._rgcontroller = RechnungController(self._dataProvider,
                                                self._wv.getRechnungTableView())
        self._rgcontroller.startWork()
        #self._configureMieteTable()
        #self._configureSonstigeTable()

    def _connect(self):
        #todo: Login-Dialog
        self._dataProvider.connect('martin', 'fuenf55')

    def _loadTree(self):
        whg_list = self._dataProvider.getWohnungsUebersicht()
        self._wv.populateWohnungenTree(whg_list)
        self._wv.registerWohnungClickCallback(self._onWohnungClicked)

    def _onWohnungClicked(self, whg_id:int) -> None:
        #print("Wohung ", whg_id, " clicked")
        # rg_list = self._dataProvider.getRechnungsUebersicht(whg_id)
        # self._wv.setRechnungen(rg_list)
        self._rgcontroller.wohnungSelected(whg_id)

    # def _configureRechnungenTable(self) -> None:
    #     columnsDefs = self._getWidgetDefs(
    #         "/home/martin/Projects/python/Wohnungsverwaltung/rechnung.json")
    #     self._wv.configureRechnungenTable(columnsDefs)
    #
    # def _configureMieteTable(self) -> None:
    #     columnsDefs = self._getWidgetDefs(
    #         "/home/martin/Projects/python/Wohnungsverwaltung/monatlicheeinaus.json")
    #     self._wv.configureMieteTable(columnsDefs)
    #
    # def _configureSonstigeTable(self) -> None:
    #     columnsDefs = self._getWidgetDefs(
    #         "/home/martin/Projects/python/Wohnungsverwaltung/sonstigeeinaus.json")
    #     self._wv.configureSonstigeTable(columnsDefs)
    #
    # def _getWidgetDefs(self, pathnfile: str) -> list:
    #     f = open(pathnfile)
    #     j = json.load(f)
    #     widgetDefs: list = j['columns']
    #     return widgetDefs