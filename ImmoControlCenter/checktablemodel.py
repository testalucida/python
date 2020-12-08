from PySide2.QtGui import QFont, QBrush, QColor
from PySide2.QtCore import *
from typing import List, Dict

from dictlisttablemodel import DictListTableModel

class CheckTableModel( DictListTableModel ):
    """ CheckTableModel hat einen genau definierten Aufbau bzgl. der ersten 7 Spalten
        Spalte 0: meinaus_id
        Spalte 1: mv_id oder vwg_id
        Spalte 2: von
        Spalte 3: bis
        Spalte 4: objekt
        Spalte 5: name  (kann Mieter oder Hausverwalter sein)
        Spalte 6: soll  (soll-miete oder soll-hausgeld)
        Spalte 7: ok  (Spalte für den OK-Button in jeder Zeile)
        Spalte 8: nok (Spalte für den NOK-Button in jeder Zeile)
        Die nachfolgenden Spalten sind beliebig. Derzeit: Je Monat eine Spalte, dann eine Zeilen-Summen-Spalte,
        dann eine Kommentarspalte.
    """
    def __init__( self, dictList:List[Dict], checkmonat:int ):
        DictListTableModel.__init__( self, dictList )
        self._greyColor = QColor( "#A19696" )
        self._greyBrush = QBrush( self._greyColor )
        self._inactiveBrush = QBrush( Qt.black )
        self._inactiveBrush.setStyle( Qt.BDiagPattern )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._yellow = QColor( "yellow" )
        self._yellowBrush = QBrush( self._yellow )
        self._leadingColumns = 9  # leading columns, die nichts mit den Monatswerten zu tun haben
        self._checkMonatColumnIdx = 0
        self._checkMonat = 0
        self._meinausidIdx = 0 # in Spalte 0 steht die meinaus_id
        self._nameColumnIdx = 5
        self._sollColumnIdx = 6  # die Spalte mit den Soll-Werten
        self._okColumnIdx = 7  # Spalte des OK-Buttons
        self._nokColumnIdx = 8  # Spalte des NOK-Buttons
        self._summeColumnIdx = 21  # Summe aller Monatszahlungen - Spalte
        self.setCheckmonat( checkmonat )
        self.okstatecallback = None
        # self._changedCallback = None
        self._changes:Dict[int, Dict] = {}
        """
        Aufbau von _changes:
        {
            12345 <meinaus_id>: {
                                    'mai': 445,90,
                                    'jun': 444,00
                                },
            3456 <meinaus_id>: {
                                    'jan': 440,00,
                                    'mrz': 445,20
                                }
        }
        """

    def resetChanges( self ):
        self._changes.clear()

    def getChanges( self ) -> Dict[int, Dict]:
        return self._changes

    def isChanged( self ) -> bool:
        return any( self._changes )

    def getOkColumnIdx( self ):
        return self._okColumnIdx

    def getNokColumnIdx( self ):
        return self._nokColumnIdx

    def setCheckmonat(self, monatIdx:int ) -> None:
        """
        Setzt den Checkmonat, das ist der, in den die Sollwerte per Knopfdruck übernommen werden
        :param monatIdx: 1: Januar, ..., 12: Dezember
        :return: None
        """
        self._checkMonat = monatIdx
        self._checkMonatColumnIdx = self._checkMonat + self._leadingColumns - 1

    def getCheckmonat( self ) -> int:
        """
        Liefert den eingestellten Checkmonat.
        :return: den Monatsindex. 1: Januar, ..., 12: Dezember
        """
        return self._checkMonat

    def getCheckmonatColumnIndex( self ) -> QModelIndex:
        idx = self.index( 0, self._checkMonatColumnIdx )
        return idx

    def setOkStateCallback(self, cbfnc ):
        self.okstatecallback = cbfnc

    def setOkState(self, index, isChecked ):
        ist = self.getCheckMonatIst( index )
        soll = self.getSoll( index )
        if ist != soll:
            self.setCheckMonatIst( index, soll )

    def setCheckMonatIst(self, index, val ):
        istidx = self.index(index.row(), self._checkMonatColumnIdx)
        #print( "going to set %d to cell %d/%d" % ( val, istidx.row(), istidx.column() ) )
        self.setData( istidx, val )

    def setSollwerte( self, sollwerte:List[Dict] ):
        # neue Sollwerte in die rowlist eintragen.
        # Das geht nicht mit zip, da die Anzahl der dictionaries in rowlist und sollwerte
        # nicht notwendigerweise übereinstimmt.
        # Annahme: beide Listen enthalten die dictionaries sortiert nach mv_id
        # Gutes Beispiel für zip:
        # https://stackoverflow.com/questions/9845369/comparing-2-lists-consisting-of-dictionaries-with-unique-keys-in-python
        n = 0
        for row in self.rowlist:
            solldict = sollwerte[n]
            if solldict["mv_id"] == row["mv_id"]:
                if solldict["brutto"] != row["soll"]:
                    row["brutto"] = solldict["brutto"]
                n+=1
            else:
                row["brutto"] = 0

    def setData( self, index, value ):
        rowdict = self.rowlist[index.row()]
        key = self._headers[index.column()]
        oldval = rowdict[key]
        oldval = 0 if not oldval else oldval
        if oldval == value: return

        summe = rowdict["summe"]
        summe -= oldval
        rowdict[key] = value
        rowdict["summe"] = summe + value
        self.dataChanged.emit( index, index )
        sumindex = self.index( index.row(), self._summeColumnIdx )
        self.dataChanged.emit( sumindex, sumindex )
        self._writeChangeLog( index, value )
        # if self._changedCallback:
        #     self._changedCallback()
        self.doChangedCallback()  #implementiert im DictListTableModel
        return True

    # def setChangedCallback( self, callbackFnc ):
    #     self._changedCallback = callbackFnc

    def _writeChangeLog( self, index, value:float ) -> None:
        """
        Schreibt ein Änderungslog für den durch <index> spezifizierten Monat
        :param index: spezifiert Zeile (meinaus_id) und Spalte (Monat)
        :param value: neuer Monatswert
        :return: None
        """
        # get meinaus_id
        ididx = self.index( index.row(), self._meinausidIdx )
        meinaus_id = self.data( ididx, Qt.DisplayRole )
        # get column name
        header = self.headerData( index.column(), Qt.Horizontal, Qt.DisplayRole )
        if not meinaus_id in self._changes:
            self._changes[meinaus_id] = {}
        self._changes[meinaus_id][header] = value

    def emitSollValuesChanged( self ):
        idxvon = self.index( 0, self._sollColumnIdx )
        idxbis = self.index( self.rowCount()-1, self._sollColumnIdx )
        self.dataChanged.emit( idxvon, idxbis )

    def getCheckMonatIst(self, index ):
        istidx = self.index(index.row(), self._checkMonatColumnIdx)
        ist = self.data(istidx, Qt.DisplayRole)
        return ist

    def getSoll( self, index ):
        sollidx = self.index(index.row(), self._sollColumnIdx)
        soll = self.data(sollidx, Qt.DisplayRole)
        return soll

    def setCheckMonatValue(self, index, value ):
        idx = self.createIndex( index.row(), self._checkMonatColumnIdx )
        self.setData( idx, value )

    def getBackgroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        # if indexcolumn == self._checkMonatColumnIdx:
        #     return self._yellowBrush
        if self._leadingColumns <= indexcolumn < self._summeColumnIdx:
            monat = indexcolumn - self._leadingColumns + 1  # der Hintergrund dieses Monats wird gerade abgefragt
            von = self.rowlist[indexrow]["von"]
            monatvon = int( von[5:7] ) # ab diesem Monat besteht das MV
            #print( von, "-", bis, " monatVon: ", monatvon, " monatIdx=", monat )
            if monatvon > monat: # MV bestand noch nicht
                return self._inactiveBrush
            bis = self.rowlist[indexrow]["bis"]
            if bis > "":
                monatbis = int( bis[5:7] ) #bis zu diesem Monat (einschließlich) bestand das MV
                if monatbis < monat:
                    return self._inactiveBrush
            # wir sind immer noch hier - also handelt es sich um eine Zelle mit aktivem MV
            if indexcolumn == self._checkMonatColumnIdx:
                return self._yellowBrush
        elif indexcolumn == self._nameColumnIdx:
            return self.headerBrush
        elif indexcolumn == self._summeColumnIdx:
            return QBrush( Qt.lightGray )
        return None

    def getForegroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        if indexcolumn < self._nameColumnIdx:
            return self._greyBrush
        else:
            return super().getForegroundBrush( indexrow, indexcolumn )

    def getFont( self, indexrow:int, indexcolumn:int ) -> QFont or None:
        if indexcolumn in (self._nameColumnIdx, self._summeColumnIdx):
            return self._boldFont

