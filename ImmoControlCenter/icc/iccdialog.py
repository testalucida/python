from abc import abstractmethod
from typing import Callable

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QDialog, QGridLayout, QWidget

from icc.iccview import IccView


class IccDialog( QDialog ):
    dialogClosing = Signal()
    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self._layout = QGridLayout()
        self.setLayout( self._layout )
        self._view:IccView = None
        self.closeEvent = self.onClose

    def getView( self ) -> IccView:
        """
        liefert die View, die von diesem Dialog gewrappt wird
        :return:
        """
        return self._view

    def setView( self, view ):
        self._view = view
        self._layout.addWidget( view, 0, 0 )

    def getPreferredWidth( self ) -> int:
        """
        liefert die Breite der TableView
        :return:
        """
        tv = self._view.getTableView()
        # return tv.width() das funktioniert erst, wenn die Miete- und HGV-TableView auf normale TableViews umgestellt sind
        return 1400

    def onClose( self, event ):
        """
        Umleitung der Methode closeEvent() aus QDialog.
        Ruft Methode mayClose()->bool auf, die von allen abgeleiteten Dialogen implementiert werden muss.
        :param event:
        :return:
        """
        if not self.mayClose():
            # Dialog nicht schließen
            event.ignore()
        else:
            # Dialog wird geschlossen. Emit dialogClosing-Signal
            self.dialogClosing.emit()

    def mayClose( self ) -> bool:
        """
        Diese Methode wird vom Controller umgeleitet auf IccController.mayDialogClose(), von wo es
        auf die abstrakte Methode isCHanged() weitergeleitet wird, die von jedem Controller zu implementieren ist.
        :return:
        """
        return False
