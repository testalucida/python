from typing import Dict, List, Any

from PySide2.QtCore import QModelIndex, QPoint
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QAction

import datehelper
from anlage_v.anlagev_ausgabentablemodel import AnlageV_AusgabenTableModel
from anlage_v.anlagev_base_logic import AnlageV_Base_Logic
from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from anlage_v.anlagev_interfaces import XErhaltungsaufwand, XAllgemeineKosten
from anlage_v.anlagev_preview_logic import AnlageV_Preview_Logic
from base.baseqtderivates import BaseAction, BaseDialogWithButtons, getCloseButtonDefinition
from base.basetablemodel import BaseTableModel, SumTableModel
from base.databasecommon import DatabaseCommon
from base.interfaces import XBase
from base.printhandler import PrintHandler
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
class ErtragTableModel( SumTableModel ):
    def __init__( self, einauslist:List[XMasterEinAus] ):
        SumTableModel.__init__( self, einauslist, ("qm", "einnahmen", "hg", "allg_kosten", "rep_kosten", "sonst_kosten",
                                                   "ertrag") )
        self.colIdxAllgKosten = 8
        self.colIdxRep = 9
        self.colIdxSonstKosten = 10

#######################  EinAusLogic  #############################
class ErtragLogic:
    def __init__( self ):
        self._eadata = ErtragData()
        # die zu verteilenden Rep.-Aufwendungen holen wir über AnlageV_DataAccess:
        self._avdata = AnlageV_DataAccess( DATABASE )
        self._avdata.open()

    def getDaten( self, jahr:int ) -> ErtragTableModel:
        masters = self._eadata.getMasterobjekte( jahr )
        # die Einnahmen holen wir aus der Tabelle zahlung
        # die Kosten holen wir aus der Anlage V Geschäftslogik:
        avlogic = AnlageV_Base_Logic( jahr )
        l = list()
        #testsumme = 0
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
            # testsumme += x.rep_kosten
            #print( x.master_name, "\tRep.:\t", x.rep_kosten, "\tSumme Rep.:\t", testsumme )
            ### !!! Verteilte Rep.kosten werden hier nicht berücksichtigt !!!
            ###     Hier geht es nur um echte Zu - und Abflüsse im betreffenden Jahr,
            ###     wohingegen die Kostenverteilung ein rein steuerliches Ding ist.
            #vert_rep = self._getSummeVerteilteErhaltungsaufwendungen( x.master_name, jahr )
            # testsumme += vert_rep
            #print( x.master_name, "\tvert.R.:\t", vert_rep, "\tSumme Rep.:\t", testsumme )
            #x.rep_kosten += vert_rep
            wk = avlogic.getWerbungskosten( x.master_name )
            x.allg_kosten = wk.getSummeAllgemeineKosten() # grundsteuer + wk.strassenreinigung + wk.abwasser
            x.sonst_kosten = wk.getSummeSonstigeKosten()
            x.ertrag = x.einnahmen + x.hg + x.sonder_u + x.allg_kosten + x.rep_kosten + x.sonst_kosten
            l.append( x )

        l = sorted( l, key=lambda x: x.ertrag, reverse=True ) # größter Ertrag oben
        tm = ErtragTableModel( l )
        tm.setHeaders( ("id", "Master", "qm", "Anz.\nMonate", "Einnahmen\n(Netto+NKV+NKA)", "netto\nje qm",
                        "HG+HGA\n(inkl. RüZuFü)", "Sonder",
                        "Allg.\nKosten", "Rep.", "Sonst.\nKosten", "Ertrag") )
        return tm

    def getReparaturenEinzeln( self, master_name, jahr ) -> SumTableModel:
        l:List[XErhaltungsaufwand] = self._avdata.getNichtVerteilteErhaltungsaufwendungen( master_name, jahr )
        for x in l:
            x.__dict__["verteilt"] = ""
        l2:List[XErhaltungsaufwand] = self._avdata.getVerteilteErhaltungsaufwendungen( master_name, jahr )
        for x in l2:
            x.betrag = x.betrag / x.verteilen_auf_jahre
            x.__dict__["verteilt"] = "x"
        l += l2
        tm = SumTableModel( l, ("betrag",) )
        tm.setKeyHeaderMappings2( ( "mobj_id", "kreditor", "rgtext", "verteilt", "betrag"),
                                  ("Objekt", "Kreditor", "Reparatur", "vert.", "Betrag") )
        return tm

    def getAllgemeineKostenEinzeln( self, master_name, jahr ) -> SumTableModel:
        av_prev_logic = AnlageV_Preview_Logic( jahr )
        av_ausg_tm:AnlageV_AusgabenTableModel = av_prev_logic.getAllgemeineAusgabenModel( master_name )
        l = av_ausg_tm.getObjectList()
        tm = SumTableModel( l, ("betrag",) )
        tm.setKeyHeaderMappings2( ("kreditor", "mobj_id", "buchungstext", "kostenart", "betrag"),
                                  ("Kreditor", "Objekt", "Buchungstext", "Kostenart", "Betrag") )
        return tm

    def getSonstigeKostenEinzeln( self, master_name, jahr ) -> SumTableModel:
        av_prev_logic = AnlageV_Preview_Logic( jahr )
        av_ausg_tm:AnlageV_AusgabenTableModel = av_prev_logic.getSonstigeAusgabenModel( master_name )
        l = av_ausg_tm.getObjectList()
        tm = SumTableModel( l, ("betrag",) )
        tm.setKeyHeaderMappings2( ("kreditor", "mobj_id", "buchungsdatum", "buchungstext", "kostenart", "betrag"),
                                  ("Kreditor", "Objekt", "Datum", "Buchungstext", "Kostenart", "Betrag") )
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
class ErtragData( IccData ):
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
              "where z.master_id = %d " \
              "and z.jahr = %d " \
              "and z.kostenart = 'r' "  % ( master_id, jahr )
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

    def getMasterobjekte( self, jahr:int ) -> List[Dict]:
        refdat = "'" + str(jahr) + "-01-01'"
        sql = "select master_id, master_name, gesamt_wfl " \
              "from masterobjekt " \
              "where (veraeussert_am is NULL or veraeussert_am = '' or veraeussert_am > " + refdat + ") " \
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

    def showDetails():
        print( "showDetails" )

    def onProvideContext( index:QModelIndex, point:QPoint, selectedIndexes:List[QModelIndex] ) -> List[BaseAction]:
        l = list()
        col = index.column()
        model = tv.model()
        x:XMasterEinAus = model.getElement( selectedIndexes[0].row() )
        if col == tm.colIdxAllgKosten:
            action = BaseAction( "Details...", ident="allg" )
            action.setData( x )
            l.append( action )
        elif col == tm.colIdxRep:
            action = BaseAction( "Details...", ident="rep" )
            action.setData( x )
            l.append( action )
        elif col == tm.colIdxSonstKosten:
            action = BaseAction( "Details...", ident="sonst" )
            action.setData( x )
            l.append( action )
        return l

    def onSelectedAction( action:BaseAction ):
        def onClose():
            dlg.accept()

        x:XMasterEinAus = action.data()
        title = ""
        detail_tv = BaseTableView()
        tm:SumTableModel = None
        if action.ident == "rep":
            tm = ealogic.getReparaturenEinzeln( x.master_name, jahr )
            title = "Reparaturen '%s' " % x.master_name + "im Detail"
        elif action.ident == "allg":
            tm = ealogic.getAllgemeineKostenEinzeln( x.master_name, jahr )
            title = "Allgemeine Kosten '%s' " % x.master_name + "im Detail"
        elif action.ident == "sonst":
            tm = ealogic.getSonstigeKostenEinzeln( x.master_name, jahr )
            title = "Sonstige Kosten '%s' " % x.master_name + "im Detail"
        detail_tv.setModel( tm )
        dlg = BaseDialogWithButtons( title, getCloseButtonDefinition( onClose ) )
        dlg.setMainWidget( detail_tv )
        dlg.exec_()


    jahr = 2022
    ealogic = ErtragLogic()
    tm = ealogic.getDaten( jahr )
    app = QApplication()
    tv = BaseTableView()
    # tv.setModel( tm )
    # tv.setAlternatingRowColors( True )
    # tv.setContextMenuCallbacks( onProvideContext, onSelectedAction )
    frame = BaseTableViewFrame( tv )
    frame.setWindowTitle( "Ertragsübersicht" )
    tb = frame.getToolBar()
    tb.addYearCombo( (jahr,), onChangeYear )
    tb.setYear( jahr )
    tb.addExportAction( "Tabelle nach Calc exportieren", onExport )
    ph = PrintHandler( tv )
    tb.addPrintAction( "Druckvorschau für diese Tabelle öffnen...", ph.handlePreview )
    tv.setModel( tm )
    tv.setAlternatingRowColors( True )
    tv.setContextMenuCallbacks( onProvideContext, onSelectedAction )
    frame.show()
    app.exec_()
