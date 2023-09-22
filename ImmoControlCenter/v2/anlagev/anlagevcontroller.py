import datehelper
from base.baseqtderivates import YearComboBox
from v2.anlagev.anlagevlogic import AnlageVLogic
from v2.anlagev.anlagevtablemodel import AnlageVTableModel, XAnlageV
from v2.anlagev.anlagevview import AnlageVView
from v2.icc.icccontroller import IccController


class AnlageVController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view = AnlageVView()
        self._logic = AnlageVLogic()
        self._vj:int = datehelper.getCurrentYear() - 1

    # def createGui( self ) -> AnlageVView:
    #     jahr = self._jahr
    #     tv = self._tv
    #     tmlist = self._logic.getAnlageVTableModel( jahr )
    #     for tm in tmlist:
    #
    #     tv.setModel( tm, selectRows=True, singleSelection=False )
    #     jahre = self._logic.getAvailableVeranlagungsjahre()
    #     if len(jahre) == 0:
    #         jahre.append( jahr )
    #     ycbo = YearComboBox( jahre )
    #     ycbo.setYear( jahr )
    #     ycbo.year_changed.connect( self.onYearChanged )
    #     tv.addToolWidget( ycbo )
    #     self._btnSortHausObjektEinAusArt = self._createHausObjektEinAusArtSortButton()
    #     # todo: create and connect with MultiSortHandler2
    #     tv.addToolWidget( self._btnSortHausObjektEinAusArt )
    #     tv.addStandardTableTools( (TableTool.SEARCH, TableTool.PRINT, TableTool.EXPORT) )
    #     tv.setContextMenuCallbacks( self.provideActions, self.onSelected )
    #     ### neue Zahlung, Zahlung ändern, löschen:
    #     self._tvframe.newItem.connect( self.onNewEinAus )
    #     self._tvframe.editItem.connect( self.onEditEinAus )
    #     self._tvframe.deleteItems.connect( self.onDeleteEinAus )
    #     return self._tvframe

def test():
    from PySide2.QtWidgets import QApplication
    def createModel() -> AnlageVTableModel:
        x = XAnlageV()
        x.vj = 2022
        x.bruttoMiete = 4904
        x.nettoMiete = 3100
        x.nkv = 1804
        x.nka = -104
        x.afa = -786
        x.erhaltg_voll = -1234
        x.verteil_aufwand_im_vj_angefallen = -6000
        x.erhaltg_anteil_vj = -2000
        x.erhaltg_anteil_vjminus1 = -3344
        x.entnahme_rue = -5000
        x.grundsteuer = -234
        # x.divAllgHk = 1000
        # x.versicherungen = 1000
        x.hgv_netto = -2000
        x.hga = 297
        x.reisen = -260
        x.sonstige = -111
        tm = AnlageVTableModel( x )
        return tm
    app = QApplication()
    tm = createModel()
    v = AnlageVView()
    v.setModel( tm, "N-Mendel7" )
    v.setPreferredSize()
    v.show()
    app.exec_()