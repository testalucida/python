import json

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
            "/home/martin/Projects/python/Wohnungsverwaltung/rechnung.json")
        return columnsDefs

    @staticmethod
    def getMonatlicheEinAusDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            "/home/martin/Projects/python/Wohnungsverwaltung/monatlicheeinaus.json")
        return columnsDefs

    @staticmethod
    def getSonstigeEinAusDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            "/home/martin/Projects/python/Wohnungsverwaltung/sonstigeeinaus.json")
        return columnsDefs

    @staticmethod
    def getGrundsteuerDefs() -> list:
        columnsDefs = ColumnDefsProvider._getWidgetDefs(
            "/home/martin/Projects/python/Wohnungsverwaltung/grundsteuer.json")
        return columnsDefs

