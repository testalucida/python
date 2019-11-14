#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, traceback
import itertools
import requests
import json
from typing import Dict, List, Text
from copy import deepcopy
import datehelper
from interfaces import \
    XMtlHausgeld, XMtlHausgeldList, \
    XHausgeldAdjustment, XHausgeldAdjustmentList, \
    XSonstigeKosten, XSonstigeKostenList, \
    XZurechnung, XImmoStammdaten, XMtlEinnahmen, XMtlEinnahmenList, \
    XAfa, XWohnungDaten, XVermieter, XVerwalter, XVermieterList, XVerwalterList, \
    XWohnungDetails

# def testRequests():
#     s = requests.Session() #create a persistent session
#     d = {
#         'user': 'martin',
#         'password': 'fuenf55'
#     }
#     r2 = s.post( 'http://localhost/kendelweb/dev/php/login.php', data=d )
#     if r2.status_code != 200:
#         return r2
#
#     #r = s.get( 'http://localhost/kendelweb/dev/php/business.php?q=uebersicht_wohnungen' )
#     d = {
#         'user': 'martin',
#         'q': 'uebersicht_wohnungen'
#     }
#     r = s.get('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_wohnungen&user=martin' )
#     return r

class WvException(Exception):
    def __init__(self, rc: str, msg: str):
        Exception.__init__(self, rc, msg)
        self.__rc = rc
        self.__msg = msg

    def rc(self):
        return self.__rc

    def message(self):
        return self.__msg

    def toString(self):
        return ''.join(('RC= ', str(self.__rc), '\nMessage=', self.__msg))

#+++++++++++++++++++++++++++++++++++++++++++++

class ServiceException(WvException):
    def __init__(self, rc, msg):
        WvException.__init__(self, rc, msg)

#+++++++++++++++++++++++++++++++++++++++++++++

class DataError(WvException):
    def __init__(self, retVal: dict):
        WvException.__init__(self, retVal['rc'], retVal['errormsg'])
        self.__retVal = retVal

    def toString(self):
        s: str = '+++++DataError+++++\n'
        for k, v in self.__retVal.items():
            s = s + k + ': ' + str(v) + '\n'
        return s

#+++++++++++++++++++++++++++++++++++++++++++++

class WriteRetVal:
    def __init__(self, rc, obj_id):
        self.__rc = rc
        self.__obj_id = obj_id
        #self.__msg = msg

    def rc(self):
        return self.__rc

    # def message(self):
    #     return self.__msg

    def object_id(self):
        return self.__obj_id

class Server:
    LOCALHOST: str = 'http://localhost/kendelweb/dev/php/'
    REMOTE: str = 'http://kendelweb.de/dev/php/'
    SERVER: str = ''

class DataProvider:
    JSONERROR: int = -2

    def __init__(self):
        self.__session = requests.Session()
        self.__user = ''

    def __del__(self):
        self.disconnect()

    def _checkException(self, resp, additionalText: str = None) -> None:
        if resp.status_code != 200 or not resp.content:
            msg = resp.text
            if additionalText:
                msg = ''.join((msg, '\n', additionalText))
            ex = ServiceException(resp.status_code, msg)
            raise ex

    def connect(self, user) -> None:
        Server.SERVER = Server.LOCALHOST if user == 'test' else Server.REMOTE
        self.__user = user
        #d = {'user':user, 'password':pwd}
        d = {'user': user}
        resp = self.__session.post(Server.SERVER + 'login.php', data=d )
        #resp = self.__session.post(SERVER + 'testecho.php', data=d)
        if resp.status_code != 200:
            msg = ''.join(('Error on connecting user ', user, '\nServer says: ', resp.text))
            raise ServiceException(resp.status_code, msg)

    def disconnect(self):
        self.__session.close()

    def getWohnungsUebersicht(self) -> list:
        """
        :return: a list of dictionaries of that kind:
        {
            'whg_id': '3',
            'plz': '90429',
            'ort': 'Nürnberg',
            'strasse': 'Austr. 22',
            'whg_bez': '2. OG'
        }
        """
        resp = self.__session.\
            get(Server.SERVER + 'business.php?q=uebersicht_wohnungen&' +
                'user=' + self.__user)
        whg_list = self._getReadRetValOrRaiseException(resp)
        if whg_list is None: whg_list = []
        return whg_list

    def getWohnungDetails(self, whg_id ) -> XWohnungDetails:
        resp = self.__session.\
            get(Server.SERVER + 'business.php?q=whg_detail&id=' + str(whg_id) + '&user=' +
                self.__user )
        data: dict = self._getReadRetValOrRaiseException(resp)
        if data['angeschafft_am']:
            data['angeschafft_am'] = datehelper.convertIsoToEur(data['angeschafft_am'])
        details = XWohnungDetails(data)
        return details

    def getWohnungIdentifikation(self, whg_id: int ):
        resp = self.__session.\
            get(Server.SERVER + 'business.php?q=wohnung_kurz&id=' +
                str(whg_id) + '&user=' +
                self.__user )
        data: dict = self._getReadRetValOrRaiseException(resp)
        """
        {
            'plz': '90429', 
            'ort': 'Nürnberg', 
            'strasse': 'Mendelstr. 24', 
            'whg_bez': '3. OG rechts', 
            'einhwert_az': '24106630826488', 
            'angeschafft_am': None,
            'steuerl_zurechng_ehemann: 100,
            'steuerl_zurechng_ehefrau: 0
        }
        """
        if data['angeschafft_am']:
            data['angeschafft_am'] = datehelper.convertIsoToEur(data['angeschafft_am'])
        return data

    def getWohnungMinStammdaten(self, whg_id: int) -> XWohnungDaten:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=wohnung_min_stamm&id=' +
                str(whg_id) + '&user=' +
                self.__user)
        data: dict = self._getReadRetValOrRaiseException(resp)
        if data['angeschafft_am']:
            data['angeschafft_am'] = datehelper.convertIsoToEur(data['angeschafft_am'])
        return XWohnungDaten(data)

    def getVerwalterListe(self) -> XVerwalterList:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=verwalter_list&id=' +
                '&user=' + self.__user)
        sk = XVerwalterList(XVerwalter,
                            self._getReadRetValOrRaiseException(resp))
        return sk

    def getVermieterListe(self) -> XVermieterList:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=vermieter_list&id=' +
                '&user=' + self.__user)
        sk = XVermieterList(XVermieter,
                            self._getReadRetValOrRaiseException(resp))
        return sk

    def getRechnungsUebersicht( self, whg_id: int ) -> list:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=uebersicht_rechnungen&id=' +
                str( whg_id ) + '&user=' + self.__user)
        # self._checkException(resp)
        # rg_list = json.loads(resp.content)
        rg_list = self._getReadRetValOrRaiseException(resp)
        rg_list = self._getDictEurDate(rg_list, 'rg_datum', 'rg_bezahlt_am')
        return rg_list

    def getMtlEinAusData(self, whg_id: int):
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=mtl_ein_aus_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        # self._checkException(resp)
        # mea_data = json.loads(resp.content)
        mea_data = self._getReadRetValOrRaiseException(resp)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    def getSonstigeEinAusData(self, whg_id: int):
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=sonst_ein_aus_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        # self._checkException(resp)
        # sea_data = json.loads(resp.content)
        sea_data = self._getReadRetValOrRaiseException(resp)
        return sea_data

    def getSonstigeEinAusArten(self) -> list:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=sonst_ein_aus_arten' +
                '&user=' + self.__user)
        art_data = self._getReadRetValOrRaiseException(resp)
        """
        art_data is a list of suchlike dictionaries: 
            {
                'art_id': '1', 
                'art': 'Hausgeldnachzahlung (Eigentümer->Verw.)', 
                'ein_aus': 'a'
            }
        """
        return art_data

    def getCurrentAndFutureMtlEinAus(self, whg_id:int) -> list:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=current_future_mtl_ein_aus&id=' +
                str(whg_id) + '&user=' + self.__user)
        self._checkException(resp)
        mea_data = json.loads(resp.content)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    def getGrundsteuerData(self, whg_id: int):
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=grundsteuer_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        gs_data = self._getReadRetValOrRaiseException(resp)
        return gs_data

    # def getVermieterData(self, whg_id: int):
    #     resp = self.__session. \
    #         get('http://localhost/kendelweb/dev/php/business.php?q=vermieter_data&id=' +
    #             str(whg_id) + '&user=' + self.__user)
    #     v_data = self._getReadRetValOrRaiseException(resp)
    #     return v_data

    def getVerwalterData(self, verwalter_id: int):
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=verwalter_data&id=' +
                str(verwalter_id) + '&user=' + self.__user)
        data = self._getReadRetValOrRaiseException(resp)
        xverwalter = XVerwalter(data)
        return xverwalter

    def getVeranlagungData(self, whg_id: int, vj: int) -> dict:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=veranl_data&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        veranl_data = self._getReadRetValOrRaiseException(resp)
        self._translateVeranlagung(veranl_data)
        return veranl_data

    def getAfa(self, whg_id: int, vj: int) -> dict:
        """
        Note: this method will provide afa data and sonstige Kosten
        (Verwaltung, Porto etc.) whose vj_ab is equal *or earlier* than the given vj
        :param whg_id:
        :param vj:
        :return:
        """
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=afa&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        data = self._getReadRetValOrRaiseException(resp)
        self._translateVeranlagung(data)
        """
         data: 
         {
            'afa_id': '2', 
            'vj_ab': '2018', 
            'betrag': '343', 
            'prozent': '2.23', 
            'lin_deg_knz': 'l',
            'afa_wie_vorjahr': 'Ja', 
            'art_afa': 'linear'
        }
        """
        return data

    def getAnlageVData_33_to_35_afa(self, whg_id: int, vj: int) -> XAfa:
        data = self.getAfa(whg_id, vj)
        return XAfa(data)

    def _translateVeranlagung(self, data: dict):
        if data:
            data['art_afa'] = 'linear' if data['lin_deg_knz'] == 'l' else 'degressiv'
            if 'angeschafft_am' in data and data['angeschafft_am']:
                data['angeschafft_am'] = \
                    datehelper.convertIsoToEur(data['angeschafft_am'])

    def existsAfaData(self, whg_id: int, vj: int) -> bool:
        """
        Note: this methods will check for a vj_ab which is *equal* to the given vj
        as opposed to method getAfaAndSonstige
        :param whg_id:
        :param vj:
        :return:
        """

        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=exists_afa_data&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        exists = self._getReadRetValOrRaiseException(resp)
        return exists

    def getAfaId(self, whg_id: int, vj: int) -> int:
        """
        Note: this methods will check for a record whose vj_ab
        is *equal* to the given vj as opposed to method getAfaAndSonstige
        :param whg_id:
        :param vj:
        :return:
        """

        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=afa_id&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        iddict = self._getReadRetValOrRaiseException(resp)
        return 0 if iddict is None else int(iddict['afa_id'])

    def getAnlageVData_1_to_8(self, whg_id: int, vj: int) -> XImmoStammdaten:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_1_to_8&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)

        data = self._getReadRetValOrRaiseException(resp)
        """
        data:
        <class 'dict'>: 
        {
            'name': 'Kendel', 
            'vorname': 'Martin', 
            'steuernummer': '217/235/50499', 
            'strasse': 'Mendelstr. 24', 
            'plz': '90429', 'ort': 'Nürnberg', 
            'whg_bez': '3. OG rechts', 
            'qm': '53', 
            'angeschafft_am': '1989-02-13', 
            'einhwert_az': '123456789', 
            'fewontzg': 'N', 
            'isverwandt': 'N'
        }
        """
        data['angeschafft_am'] = '' if not data['angeschafft_am'] else \
                                datehelper.convertIsoToEur(data['angeschafft_am'])
        data['fewontzg'] = '1' if data['fewontzg'] == 'J' else '2'
        data['isverwandt'] = '1' if data['isverwandt'] == 'J' else '2'
        immostamm = XImmoStammdaten(data)
        return immostamm

    def getAnlageVData_9_to_14_mtlEinn(self, whg_id: int, vj: int) -> XMtlEinnahmenList:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_9_to_14_mtl_einn&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        data = self._getReadRetValOrRaiseException(resp)
        return XMtlEinnahmenList(XMtlEinnahmen, data)

    def getAnlageVData_13_nkKorr(self, whg_id: int, vj: int) -> List[Dict[str, str]]:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_13_nk_korr&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        data = self._getReadRetValOrRaiseException(resp)
        """
        data: list of dictionaries:
        [
            {
                'sea_id': '11', 
                'vj': '2018', 
                'betrag': '93.00', 
                'art_id': '3', 
                'art': 'Nebenkostennachzahlung (Mieter->Verm.)',
                'ein_aus': 'e'
            },
            ...
        ]
        """

        return data

    def getAnlageVData_46_grundsteuer(self, whg_id: int, vj: int) -> int:
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_grundsteuer&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        data = self._getReadRetValOrRaiseException(resp)
        return int(round(float(data['betrag'])))

############### Zeilen 47 und 49 ANFANG ################################################
    """
    Verwaltungskosten (Zeile 47) sind insbesondere Zahlungen an den Hausverwalter 
    sowie Hausgelder. 
    
    Zu «Sonstiges» (Zeile 49) gehören z. B. Mitgliedsbeiträge zum 
    Haus- und Grundbesitzerverein, 
    Kosten für die Mietersuche (Makler, Zeitungsanzeigen) 
    oder der Einziehung der Miete (Anwalts-, Mahn-, Gerichtskosten), 
    Kontoführungsgebühren (pauschal 16 EUR), 
    Reisekosten (Fahrtkosten, Verpflegungsmehraufwendungen 
                 und Übernachtungskosten im Zusammenhang mit Reparaturen, Behördengängen, 
                 Handwerkerbesprechungen oder Grundstückskontrollen) 
    sowie Telefongespräche mit den Mietern und Steuerberatungskosten im Zusammenhang 
    mit dem vermieteten Objekt. 
    (siehe https://www.steuern.de/steuererklaerung-anlage-v.html und
           https://www.smartsteuer.de/online/ausfuellhilfen/anlage-v-ausfuellhilfe/)
    """

    def getAnlageVData_47_hausgeld(self, whg_id: int, vj: int) -> int:
        """
        returns corrected Hausgeld
        :param whg_id:
        :param vj:
        :return:
        """
        #periodical payments
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlageV_47_mtl_hausgeld&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        '''
        resp contains a list of dictionaries:
        <class 'list'>: 
        [
            {
                'mea_id': '3', 
                'gueltig_ab': '2017-08-01', 
                'gueltig_bis': '2018-09-30', 
                'hg_netto_abschlag': '20.00'
            }, 
            {
                'mea_id': '4', 
                'gueltig_ab': '2018-10-01', 
                'gueltig_bis': '2019-05-31', 
                'hg_netto_abschlag': '25.00'
            },
            ...
        ]
        '''
        hg = XMtlHausgeldList(XMtlHausgeld,
                             self._getReadRetValOrRaiseException(resp))
        sum_abschlag = 0
        for dic in hg.getList():
            cnt: int = datehelper.getNumberOfMonths(dic.gueltig_ab, dic.gueltig_bis, vj)
            sum_abschlag += (cnt * float(dic.hg_netto_abschlag))

        #adjustment payment as needed
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_47_hausgeld_korr&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        '''
        resp contains a list of dictionaries (typically only one):
        <class 'list'>: 
        [
            {
                'sea_id': '12', 
                'vj': '2018', 
                'betrag': '130.00', 
                'art_id': '1', 
                'art': 'Hausgeldnachzahlung (Eigentümer->Verw.)', 
                'ein_aus': 'a'
            },
            ...
        ]
        '''
        hgadjust = XHausgeldAdjustmentList(XHausgeldAdjustment,
                                          self._getReadRetValOrRaiseException(resp))
        sum_adjust = 0
        for dic in hgadjust.getList():
            adj_betrag = float(dic.betrag)
            if dic.ein_aus == 'e': # hausgeld is an expense.
                                   # 'e' means a redemption, a reduction of this expense,
                                    # so we have to subtract it from the periodically payment ,
                                   # hence multiply by -1
                adj_betrag *= -1
            sum_adjust += adj_betrag

        hg_adjusted = sum_abschlag + sum_adjust

        return int(round(hg_adjusted))

    def getAnlageVData_49_sonstiges(self, whg_id: int, vj: int) -> int:
        """
        Ermittelt aus der Tabelle 'sonstige_ein_aus' alle zur whg_id und vj passenden
        Sätze der Art 'sonst_kost'.
        """
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_49_sonstige_kosten&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        sk = XSonstigeKostenList(XSonstigeKosten,
                                 self._getReadRetValOrRaiseException(resp))

        sum_sonstige = 0.0
        for item in sk.getList():
            sum_sonstige += float(item.betrag)

        return int(sum_sonstige)

############### Zeilen 47 und 49 ENDE ##################################################

    def getAnlageVData_24_zurechnung(self, whg_id: int):
        resp = self.__session. \
            get(Server.SERVER + 'business.php?q=anlagev_24_zurechnung&id=' +
                str(whg_id) + '&user=' + self.__user)
        zurechnung = XZurechnung(self._getReadRetValOrRaiseException(resp))
        return (zurechnung.steuerl_zurechng_mann, zurechnung.steuerl_zurechng_frau)

    '''
    insert wohnung
    '''
    def insertWohnungMin(self, xdata:XWohnungDaten) -> int:
        return self._writeWohnungMin(xdata, isInsert=True)

    '''
    update wohnung min
    '''
    def updateWohnungMin(self, xdata:XWohnungDaten) -> int:
        return self._writeWohnungMin(xdata, isInsert=False)

    def _writeWohnungMin(self, xdata: XWohnungDaten, isInsert: bool) -> int:
        q = 'insert_wohnung_min' if isInsert else 'update_wohnung_min'
        xdatatmp:XWohnungDaten = deepcopy(xdata)
        if xdata.angeschafft_am:
            if datehelper.isValidEurDatestring(xdata.angeschafft_am):
                xdatatmp.angeschafft_am = \
                    datehelper.convertEurToIso(xdata.angeschafft_am)
            else:
                if not datehelper.isValidIsoDatestring(xdata.angeschafft_am):
                    raise ValueError(''.join((
                        'Wohnung angeschafft am: ',
                        xdata.angeschafft_am,
                        ' ist kein gültiges Datumsformat')))

        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=' + q + '&user=' + self.__user,
                 data=xdatatmp.getValuesAsDict())

        retval = self._getWriteRetValOrRaiseException(resp)

        return int(retval.object_id())

    '''
    insert afa
    '''
    def insertAfaData(self, afa_dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_afa&user=' + self.__user,
                 data=afa_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update afa
    '''
    def updateAfaData(self, afa_dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_afa&user=' + self.__user,
                 data=afa_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update whg veranlag data
    '''
    def updateWhgVeranlagData(self, data: dict):
        """
        :param data:
        {
            'whg_id': nnnn
            'angeschafft_am': yyyy-mm-dd,
            'einhwert_az': xxxxxxxxxxxxxxx,
            'steuerl_zurechng_mann: nn,
            'steuerl_zurechng_frau: nn
        }
        :return:
        """
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_whg_veranlag&user=' + self.__user,
                 data=data)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval


    '''
    insert mtl ein_aus
    '''
    def insertMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update mtl ein_aus
    '''
    def updateMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    terminate mtl ein_aus
    '''
    def terminateMtlEinAus(self, mea_id, gueltig_bis):
        d = {'mea_id': mea_id, 'gueltig_bis': gueltig_bis}
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=terminate_mtl_ein_aus&user=' + self.__user,
                 data=d)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete mtl ein_aus
    '''
    def deleteMtlEinAus(self, mea_id):
        d = {'mea_id': mea_id}
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=delete_mtl_ein_aus&user=' + self.__user, data=d)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert sonstige ein_aus
    '''
    def insertSonstEinAus(self, sea_dict: dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_sonst_ein_aus&user=' + self.__user,
                 data=sea_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
     update sonstige ein_aus
     '''
    def updateSonstEinAus(self, sea_dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_sonst_ein_aus&user=' + self.__user,
                 data=sea_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete sonstige ein_aus
    '''
    def deleteSonstEinAus(self, sea_id):
        delData = {}
        delData['sea_id'] = str(sea_id)
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=delete_sonst_ein_aus&user=' + self.__user, data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert grundsteuer
    '''
    def insertGrundsteuer(self, gs_dict: dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_grundsteuer&user=' + self.__user,
                 data=gs_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
     update grundsteuer
     '''
    def updateGrundsteuer(self, gs_dict):
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_grundsteuer&user=' + self.__user,
                 data=gs_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete grundsteuer
    '''
    def deleteGrundsteuer(self, gs_id):
        delData = {}
        delData['gs_id'] = str(gs_id)
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=delete_grundsteuer&user=' + self.__user,
                 data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert new rechnung
    '''
    def insertRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_rechnung&user=' + self.__user, data=rgdictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update rechnung
    '''
    def updateRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_rechnung&user=' + self.__user,
                 data=rgdictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete rechnung
    '''
    def deleteRechnung(self, rg_id):
        delData = {}
        delData['rg_id'] = str(rg_id)
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=delete_rechnung&user=' + self.__user, data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete wohnung
    '''
    def deleteWohnung(self, whg_id: int) -> None:
        delData = {
            'whg_id': str(whg_id)
        }
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=delete_wohnung&user=' + self.__user, data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert verwalter
    '''
    def insertVerwalter(self, data:XVerwalter) -> None:
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=insert_verwalter&user=' + self.__user,
                 data=data.getValuesAsDict())

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update verwalter
    '''
    def updateVerwalter(self, data:XVerwalter) -> None:
        resp = self.__session. \
            post(Server.SERVER + 'business.php?q=update_verwalter&user=' + self.__user,
                 data=data.getValuesAsDict())

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    ###########################################################################

    def _getDictCopyIsoDate(self, orig: dict, *keys) -> dict:
        copy = dict(orig)
        for key in keys:
            copy[key] = datehelper.convertEurToIso(copy[key])
        return copy

    def _getDictEurDate(self, origList: list, *keys) -> list:
        for dic in origList:
            for key in keys:
                if dic[key]:
                    dic[key] = datehelper.convertIsoToEur(dic[key])
        return origList

    def _getReadRetValOrRaiseException(self, resp) -> any:
        if resp.status_code != 200:
            serviceError = None
            if resp.status_code == 500:
                msg = 'Requested service not found.\n\n' + self._getStack()
                serviceError = ServiceException(500, msg)
            else:
                msg = resp.text + '\n\n' + self._getStack()
                serviceError = ServiceException( resp.status_code, msg )

            raise serviceError

        ret = None
        try:
            ret = json.loads(resp.content)
        except ValueError as e:
            msg: str = ''.join((str(type(e)), ': ', e.args[0]))
            msg += '\n\n'
            msg += self._getStack()
            raise ServiceException(str(self.JSONERROR), msg)
        except Exception as x:
            msg = '' if not resp.content else resp.content
            msg += '\n\n'
            msg += self._getStack()
            dataError = DataError(resp.status_code, msg)
            raise dataError

        if ret is None:
            msg = 'Service call provided no content (None)\n\n' + self._getStack()
            raise WvException(resp.status_code, msg)

        return ret

    def _getStack(self) -> str:
        stacklist = traceback.format_stack()
        stack = 'Stacktrace:\n'
        start = len(stacklist)
        start = start - 4 if start > 3 else 0
        for e in stacklist[start:]:
            stack += e
            stack += '\n'
        return stack

    def _getWriteRetValOrRaiseException(self, resp):
        if resp.status_code != 200:
            serviceError = ServiceException( resp.status_code, resp.text )
            print(serviceError.toString())
            raise serviceError

        dic = {}
        try:
            dic = json.loads(resp.content)
        except ValueError as e:
            print(e)
            msg: str = ''.join((str(type(e)), ': ', e.args[0]))
            print(msg)
            raise ServiceException(str(self.JSONERROR), msg)

        if dic['rc'] != 0:
            dataError = DataError(dic)
            raise dataError

        return WriteRetVal(dic['rc'], dic['obj_id'])



######### For testing purposes only ########################
#
if __name__ == '__main__':
    prov = DataProvider()
    prov.connect('d02bacec')
    prov.getAnlageVData_49_sonstiges(1, 2018)
    #xvwlist: XVerwalterList = prov.getVerwalterListe()
    #xvmlist: XVermieterList = prov.getVermieterListe()
    #xdata: XWohnungDaten = prov.getWohnungMinStammdaten(1)

    # from datetime import datetime, date
    # s = '2012-3-24'
    # dt = datetime.strptime(s, '%Y-%m-%d')

    xdata: XWohnungDaten = XWohnungDaten()
    xdata.strasse = 'Antonstr. 22'
    xdata.plz = '90429'
    xdata.ort = 'Gostenhof'
    xdata.angeschafft_am = '2000-5-24'
    print(xdata)
    #prov.insertWohnungMin(xdata)

    #prov.deleteWohnung(2)

    #hg = prov.getHausgeld(1, 2018)
    #sonst = prov.getAnlageVData_49_sonstiges(1, 2018)
    # afa = {
    #     'afa_id': 1,
    #     'betrag': 111,
    #     'prozent': 1.23,
    #     'lin_deg_knz': 'l',
    #     'afa_wie_vorjahr': 'J'
    # }
    # prov.updateAfaData(afa)

    # id = prov.getAfaId(1, 2019)
    # print(id)
    #exists: bool = prov.existsAfaData(1, 2018)
    #print(exists)
    # #data = prov.insertAfaData(afa)
    # data = prov.getAfaData(1, 2018)
    # print(data)


    # whg_list = prov.getWohnungsUebersicht()
    # print(whg_list)
    #
    # miete_data = prov.getMieteData(2)
    # print(miete_data)
