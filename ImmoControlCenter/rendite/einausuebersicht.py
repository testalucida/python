from typing import Dict, List, Any

from PySide2.QtCore import QModelIndex, QPoint
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QAction

import datehelper
from anlage_v.anlagev_base_logic import AnlageV_Base_Logic
from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from base.basetablemodel import BaseTableModel
from base.databasecommon import DatabaseCommon
from base.interfaces import XBase
from definitions import DATABASE
from icc.iccdata import IccData

#######################  XMasterEinAus  #############################
class XMasterEinAus( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )
        self.master_id = 0
        self.master_name = ""
        self.qm = 0
        self.monate = 0 # Anzahl vermietete Monate
        self.einnahmen = 0 # Bruttomiete plus NKA
        self.netto_je_qm = 0.0
        self.hg = 0 # HGV inkl. RüZuFü plus HGA (Entn. Rü. bleibt unberücksichtigt, da die RüZuFü zu den Ausgaben zählen)
        self.sonder_u = 0 # wird als Ausgabe gewertet
        self.allg_kosten = 0 # Kostenarten a, g, v
        self.rep_kosten = 0 # nicht verteilte und verteilte
        self.sonst_kosten = 0 # Kostenart s
        self.ertrag = 0

#######################  EinAusTableModel  #############################
class EinAusTableModel( BaseTableModel ):
    def __init__( self, einauslist:List[XMasterEinAus] ):
        BaseTableModel.__init__( self, einauslist )
        self._rowCount = len( einauslist ) + 1  # wegen Summenzeile
        self._fontSumme = QFont( "Arial", 12, weight=QFont.Bold )
        self._colIdxNettoQm = 5
        self._colIdxErtrag = 11
        self._summeErtrag = sum([e.ertrag for e in einauslist])

    def rowCount( self, parent: QModelIndex = None ) -> int:
        return self._rowCount

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexrow == self._rowCount - 1:
            if indexcolumn == 0:
                return "SUMME"
            elif indexcolumn == self._colIdxErtrag:
                return self._summeErtrag
            else:
                return None

        e:XMasterEinAus = self.getElement( indexrow )
        return e.getValue( self.keys[indexcolumn] )

    def getFont( self, indexrow: int, indexcolumn: int ) -> QFont or None:
        if indexrow == self._rowCount - 1:
            if indexcolumn in (0, self._colIdxErtrag):
                return self._fontSumme
            else:
                return None


#######################  EinAusLogic  #############################
class EinAusLogic:
    def __init__( self ):
        self._eadata = EinAusData()
        # die zu verteilenden Rep.-Aufwendungen holen wir über AnlageV_DataAccess:
        self._avdata = AnlageV_DataAccess( DATABASE )
        self._avdata.open()

    def getDaten( self, jahr:int ) -> EinAusTableModel:
        masters = self._eadata.getMasterobjekte()
        # die Einnahmen holen wir aus der Tabelle zahlung
        # die Kosten holen wir aus der Anlage V Geschäftslogik:
        avlogic = AnlageV_Base_Logic( jahr )
        l = list()
        for master in masters:
            x = XMasterEinAus()
            x.master_id = master["master_id"]
            x.master_name = master["master_name"]
            x.qm = master["gesamt_wfl"]
            x.monate = self._eadata.getAnzahlVermieteteMonate( x.master_id, jahr )
            x.einnahmen = self._eadata.getSummeEinzahlungen( x.master_id, jahr )
            if x.qm > 0:
                x.netto_je_qm = self._getAktuelleNettoMieteJeQm( x.master_id, x.qm )
            x.hg = self._eadata.getSummeHausgeld( x.master_id, jahr )
            x.sonder_u = self._eadata.getSummeSonderumlagen( x.master_id, jahr )
            x.rep_kosten = self._eadata.getSummeReparaturen( x.master_id, jahr )
            x.rep_kosten += self._getSummeVerteilteErhaltungsaufwendungen( x.master_name, jahr )
            wk = avlogic.getWerbungskosten( x.master_name )
            x.allg_kosten = wk.getSummeAllgemeineKosten() # grundsteuer + wk.strassenreinigung + wk.abwasser
            x.sonst_kosten = wk.getSummeSonstigeKosten()
            x.ertrag = x.einnahmen + x.hg + x.sonder_u + x.allg_kosten + x.rep_kosten + x.sonst_kosten
            l.append( x )

        l = sorted( l, key=lambda x: x.ertrag, reverse=True ) # größter Ertrag oben
        tm = EinAusTableModel( l )
        tm.setHeaders( ("id", "Master", "qm", "Anz.\nMonate", "Einnahmen\n(Netto+NKV+NKA)", "netto\nje qm",
                        "HG+HGA\n(inkl. RüZuFü)", "Sonder",
                        "Allg.\nKosten", "Rep.", "Sonst.\nKosten", "Ertrag") )
        return tm

    def _getSummeVerteilteErhaltungsaufwendungen( self, master_name:str, jahr:int ) -> int:
        su = 0
        replist = self._avdata.getVerteilteErhaltungsaufwendungen( master_name, jahr )
        for rep in replist:
            su += ( rep.betrag / rep.verteilen_auf_jahre )
        return int( round( su ) )

    def _getAktuelleNettoMieteJeQm( self, master_id:int, qm:int ) -> float:
        sumnetto =self._eadata.getNettomieteAktuell( master_id )
        nettojeqm = sumnetto / qm
        return float( format(nettojeqm, "0.2f") )

#######################  EinAusData  #############################
class EinAusData( IccData ):
    def __init__( self ):
        IccData.__init__( self )

    def getSummeEinzahlungen( self, master_id:int, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from zahlung " \
              "where master_id = %d " \
              "and jahr = %d " \
              "and zahl_art in ( 'bruttomiete', 'nka', 'nkv' ) " % (master_id, jahr)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getAnzahlVermieteteMonate( self, master_id:int, jahr:int ) -> int:
        sql = "select count(*) " \
              "from zahlung " \
              "where master_id = %d " \
              "and jahr = %d " \
              "and zahl_art = 'bruttomiete' " % (master_id, jahr)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getSummeAuszahlungen( self, master_id:int, kostenart:str, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from zahlung " \
              "where master_id = %d " \
              "and jahr = %d " \
              "and kostenart = '%s' " % ( master_id, jahr, kostenart )
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getSummeReparaturen( self, master_id:int, jahr:int ) -> int:
        sql = "select sum(z.betrag) " \
              "from zahlung z " \
              "inner join sonstaus sa on sa.saus_id = z.saus_id " \
              "where z.master_id = %d " \
              "and z.jahr = %d " \
              "and z.kostenart = 'r' " \
              "and sa.verteilen_auf_jahre = 1 "  % ( master_id, jahr )
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getSummeHausgeld( self, master_id:int, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from zahlung " \
              "where master_id = %d " \
              "and jahr = %d " \
              "and zahl_art in ('hgv', 'hga') " % ( master_id, jahr )
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getSummeSonderumlagen( self, master_id:int, jahr:int ) -> int:
        sql = "select sum(betrag) " \
              "from sonderumlage " \
              "where master_id = %d " \
              "and jahr = %d " % (master_id, jahr)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return int( round( summe ) ) if summe else 0.0

    def getNettomieteAktuell( self, master_id:int ) -> float:
        current_date = datehelper.getCurrentDateIso()
        sql = "select sum( netto ) " \
              "from sollmiete sm " \
              "inner join mietverhaeltnis mv on mv.mv_id = sm.mv_id " \
              "inner join mietobjekt mobj on mobj.mobj_id = mv.mobj_id " \
              "where mobj.master_id = %d " \
              "and sm.von <= '%s' " \
              "and (sm.bis is '' or sm.bis is NULL or sm.bis >= '%s') " % (master_id, current_date, current_date)
        tuplelist = self.read( sql )
        summe = tuplelist[0][0]
        return summe if summe else 0.0

    def getMasterobjekte( self ) -> List[Dict]:
        sql = "select master_id, master_name, gesamt_wfl " \
              "from masterobjekt " \
              "where (veraeussert_am is NULL or veraeussert_am = '') " \
              "and master_name not like '*%' " \
              "order by master_name "
        dictlist = self.readAllGetDict( sql )
        return dictlist


###############################################################################
def test():
    from PySide2.QtWidgets import QApplication
    from base.basetableview import BaseTableView
    from base.basetableviewframe import BaseTableViewFrame
    #eadata = EinAusData()
    #netto = eadata.getNettomieteAktuell( 17 )
    # su = eadata.getSummeEinzahlungen( 17, 2021 )
    # print( "Ein: ", su )
    # su = eadata.getSummeAuszahlungen( 17, 'r', 2021 )
    # print( "Aus r: ", su )
    # su = eadata.getSummeHausgeld( 17, 2021 )
    # print( "Aus r: ", su )
    # su = eadata.getSummeSonderumlagen( 17, 2021 )
    # print( "Sonder: ", su )
    def onChangeYear( newYear:int ):
        print( "year changed to ", newYear )
        tm = ealogic.getDaten( newYear )
        tv.setModel( tm )

    def onExport():
        print( "onExport")

    def onProvideContext( index:QModelIndex, point:QPoint, selectedIndexes ) -> List[QAction]:
        l = list()
        action = QAction( "Details..." )
        l.append( action )
        return l

    def onSelectedAction( action:QAction ):
        print( action.text() )

    ealogic = EinAusLogic()
    tm = ealogic.getDaten( 2021 )
    app = QApplication()
    tv = BaseTableView()
    tv.setModel( tm )
    tv.setAlternatingRowColors( True )
    tv.setContextMenuCallbacks( onProvideContext, onSelectedAction )
    frame = BaseTableViewFrame( tv )
    tb = frame.getToolBar()
    tb.addYearCombo( (2021, 2022), onChangeYear )
    tb.addExportAction( "Tabelle nach Calc exportieren", onExport )
    frame.show()
    app.exec_()
