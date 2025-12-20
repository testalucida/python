from PySide6.QtCore import QObject

from generictable_stuff.okcanceldialog import OkCancelDialog
from gui.currenciespanel import CurrenciesPanel
from logic.currencyhistorylogic import CurrencyHistoryLogic


class CurrencyHistoryController( QObject ):
    def __init__( self ):
        QObject.__init__( self )
        self._panel:CurrenciesPanel = CurrenciesPanel()
        self._panel.years_count_changed.connect(self.onYearsCountChanged)
        self._logic = CurrencyHistoryLogic()
        self._dlgCurrenciesHistory = None
        self._createDialog()

    def _createDialog( self ):
        self._dlgCurrenciesHistory = OkCancelDialog( title="Wechselkurse im Verhältnis zum Euro" )
        self._dlgCurrenciesHistory.addWidget( self._panel, 0 )

    def showCurrencyHistory(self):
        self.onYearsCountChanged(1)

    def onYearsCountChanged( self, cntYears:int ):
        daylist, currencies = self._logic.getDaysAndCurrencies(cntYears=cntYears)
        self._panel.setCurrencies( daylist, currencies )
        self._dlgCurrenciesHistory.show()
        self._dlgCurrenciesHistory.resize( self._dlgCurrenciesHistory.sizeHint() )


def test():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    ctrl = CurrencyHistoryController()
    ctrl.showCurrencyHistory()
    app.exec()

if __name__ == "__main__":
    test()