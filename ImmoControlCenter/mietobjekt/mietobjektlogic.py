from typing import List

from interfaces import XMietobjektExt, XMasterobjekt, XMietobjekt
from mietobjekt.mietobjektdata import MietobjektData


class MietobjektLogic:
    def __init__( self ):
        self._db = MietobjektData()

    def getMasterobjektNamen( self ) -> List[str]:
        masterlist = self._db.getMasterobjektNamen()
        return masterlist

    def getMietobjektNamen( self, master_name:str ) -> List[str]:
        namenlist = self._db.getMietobjektNamen( master_name )
        return namenlist

    def getMietobjekteKurzZuMaster( self, master_name:str ):
        mobj_idlist = self._db.getMietobjekteKurzZuMaster( master_name )
        return mobj_idlist

    def validateMietobjektExt( self, x:XMietobjektExt ) -> str:
        msg = ""
        if not x.strasse_hnr or not x.plz or not x.ort:
            msg = "Die Adresse des Master-Objekts muss vollständig angegeben sein."
        elif not x.whg_bez:
            msg = "Die Bezeichnung der Wohnung muss angegeben sein."
        return msg

    def modifyObjekt( self, x:XMietobjektExt ):
        """
        Ändert Masterobjekt und Mietobjekt. Validiert die Daten vorher.
        :param x:
        :return:
        """
        # Validierung:
        msg = self.validateMietobjektExt( x )
        if msg:
            raise Exception( "Mietobjektlogic.modifyObjekt()\nValidierung der Daten für "
                             "Masterobjekt '%s', Mietobjekt '%s' fehlgeschlagen."
                             % x.master_name, x.mobj_id )
        # Update auf Masterobjekt
        xmaster = XMasterobjekt()
        xmaster.master_id = x.master_id
        xmaster.strasse_hnr = x.strasse_hnr
        xmaster.plz = x.plz
        xmaster.ort = x.ort
        xmaster.gesamt_wfl = x.gesamt_wfl
        xmaster.anz_whg = x.anz_whg
        xmaster.veraeussert_am = x.veraeussert_am
        xmaster.bemerkung = x.bemerkung_masterobjekt
        xmaster.hauswart = x.hauswart
        xmaster.hauswart_telefon = x.hauswart_telefon
        xmaster.hauswart_mailto = x.hauswart_mailto
        if  self._db.updateMasterobjekt( xmaster ) == 0:
            raise Exception( "Mietobjektlogic.modifyObjekt()\nUpdate fehlgeschlagen, "
                             "Masterobjekt '%s' mit master_id '%d' nicht gefunden."
                             % x.master_name, x.master_id )
        # Update auf Mietobjekt
        xmobj = XMietobjekt()
        xmobj.mobj_id = x.mobj_id
        xmobj.whg_bez = x.whg_bez
        xmobj.qm = x.qm
        xmobj.container_nr = x.container_nr
        xmobj.bemerkung = x.bemerkung_mietobjekt
        if self._db.updateMietobjekt( xmobj ) == 0:
            raise Exception( "Mietobjektlogic.modifyObjekt()\nUpdate fehlgeschlagen, Mietobjekt '%s' nicht gefunden."
                             % xmobj.mobj_id )

