from typing import List

from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QApplication, QMenu, QDialog, QMessageBox

import datehelper
from base.messagebox import ErrorBox, QuestionBox
from v2.icc.constants import Modus
from v2.icc.icccontroller import IccController
from v2.icc.interfaces import XEinAus
from v2.sammelabgabe.sammelabgabegui import SammelabgabeSplitterDialog
from v2.sammelabgabe.sammelabgabelogic import SammelabgabeLogic


class SammelabgabeController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = SammelabgabeLogic()
        self._dlg:SammelabgabeSplitterDialog = None

    def _createGui( self ) -> SammelabgabeSplitterDialog:
        self._dlg = SammelabgabeSplitterDialog()
        tm = self._logic.getSammelabgabeTableModel( self.getYearToStartWith() )
        self._dlg.setTableModel( tm )
        self._dlg.setAbschlag( tm.getVierteljahresAbschlag() )
        self._dlg.setBuchungsdatum( datehelper.getCurrentDateIso() )

    def getMenu( self ) -> QMenu or None:
        return None

    def processSammelabgabe( self, jahr:int ) -> List[XEinAus] or None:
        self._createGui()
        if self._dlg.exec_() == QDialog.Accepted:
            abschlag = self._dlg.getAbschlag()
            buchungsdatum = self._dlg.getBuchungsdatum()
            try:
                summe = self._logic.checkSammelabgabe( buchungsdatum )
                if summe != 0:
                    msg = "Etwa zum Zeitpunkt %s wurden Grundsteuerabgaben in Höhe von %.2f bezahlt.\n" % (buchungsdatum, summe )
                    msg += "Soll die Buchung trotzdem durchgeführt werden?"
                    box = QuestionBox( "Abgabenzahlung gefunden", msg, "JA", "NEIN" )
                    if box.exec_() != QMessageBox.Yes:
                        return
            except Exception as ex:
                msg = str(ex) + "\nBuchung wird nicht durchgeführt."
                box = ErrorBox( "Fehler beim Zugriff auf Tabelle <einaus>", str(ex), "" )
                box.exec_()
                return
            try:
                l:List[XEinAus] = self._logic.trySaveSammelabgabe( jahr, abschlag, buchungsdatum )
                return l
            except Exception as ex:
                msg = "Exception beim Speichern des Abschlags von %.2f Euro mit Buchungsdatum %s:\n " %  \
                      (abschlag, buchungsdatum )
                msg += str(ex)
                box = ErrorBox( "Fehler beim Speichern der Sammelabgabe", msg, "" )
                box.exec_()
                return None


def test():
    app = QApplication()
    c = SammelabgabeController()
    c.processSammelabgabe( 2022 )

