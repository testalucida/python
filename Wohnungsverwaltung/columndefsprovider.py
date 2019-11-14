import json
import utils

class ColumnDefsProvider:
    @staticmethod
    def _getWidgetDefs(pathnfile: str) -> list:
        f = open(pathnfile)
        j = json.load(f)
        widgetDefs: list = j['columns']
        return widgetDefs

    @staticmethod
    def getRechnungDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            utils.getScriptPath() + "/rechnung.json")
        return columnsDefs

    @staticmethod
    def getMonatlicheEinAusDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            utils.getScriptPath() + "/monatlicheeinaus.json")
        return columnsDefs

    @staticmethod
    def getSonstigeEinAusDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            utils.getScriptPath() + "/sonstigeeinaus.json")
        return columnsDefs

    @staticmethod
    def getGrundsteuerDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            utils.getScriptPath() + "/grundsteuer.json")
        return columnsDefs

