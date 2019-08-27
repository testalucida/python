#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import urllib.request
import requests
import json
from abc import ABC, abstractmethod
import datehelper

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

#+++++++++++++++++++++++++++++++++++++++++++++

class DataProvider:
    JSONERROR: int = -2

    def __init__(self ):
        self.__session = requests.Session()
        self.__user = ''

    def _checkException(self, resp, additionalText: str = None) -> None:
        if resp.status_code != 200 or not resp.content:
            msg = resp.text
            if additionalText:
                msg = ''.join((msg, '\n', additionalText))
            ex = ServiceException(resp.status_code, msg)
            raise ex

    def connect(self, user, pwd) -> None:
        self.__user = user
        d = {'user':user, 'password':pwd}
        resp = self.__session.post('http://localhost/kendelweb/dev/php/login.php', data=d )
        if resp.status_code != 200:
            msg = ''.join(('Error on connecting user ', user, '\nServer says: ', resp.text))
            raise ServiceException(resp.status_code, msg)

    def getWohnungsUebersicht(self) -> list:
        """
        :return: a list of dictionaries of that kind:
        {
            'whg_id': '3',
            'plz': '90429',
            'ort': 'Nürnberg',
            'strasse': 'Austr. 22',
            'whg_bez': '2. OG'
        """
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_wohnungen&' +
                'user=' + self.__user)
        whg_list = self._getReadRetValOrRaiseException(resp)
        return whg_list

    def getWohnungDetails(self, whg_id ):
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=detail&id=' + whg_id + '&user=' +
                self.__user )
        return resp

    def getWohnungIdentifikation(self, whg_id: int ):
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=wohnung_kurz&id=' +
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
            'angeschafft_am': None}
        """
        if data['angeschafft_am']:
            data['angeschafft_am'] = datehelper.convertIsoToEur(data['angeschafft_am'])
        return data

    def getRechnungsUebersicht( self, whg_id: int ) -> list:
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_rechnungen&id=' +
                str( whg_id ) + '&user=' + self.__user)
        # self._checkException(resp)
        # rg_list = json.loads(resp.content)
        rg_list = self._getReadRetValOrRaiseException(resp)
        rg_list = self._getDictEurDate(rg_list, 'rg_datum', 'rg_bezahlt_am')
        return rg_list

    def getMtlEinAusData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=mtl_ein_aus_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        # self._checkException(resp)
        # mea_data = json.loads(resp.content)
        mea_data = self._getReadRetValOrRaiseException(resp)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    def getSonstigeEinAusData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=sonst_ein_aus_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        # self._checkException(resp)
        # sea_data = json.loads(resp.content)
        sea_data = self._getReadRetValOrRaiseException(resp)
        return sea_data

    def getSonstigeEinAusArten(self) -> list:
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=sonst_ein_aus_arten' +
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
            get('http://localhost/kendelweb/dev/php/business.php?q=current_future_mtl_ein_aus&id=' +
                str(whg_id) + '&user=' + self.__user)
        self._checkException(resp)
        mea_data = json.loads(resp.content)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    def getGrundsteuerData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=grundsteuer_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        gs_data = self._getReadRetValOrRaiseException(resp)
        return gs_data

    def getVermieterData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=vermieter_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        v_data = self._getReadRetValOrRaiseException(resp)
        return v_data

    def getVerwalterData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=verwalter_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        v_data = self._getReadRetValOrRaiseException(resp)
        return v_data

    def getVeranlagungData(self, whg_id: int, vj: int) -> dict:
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=veranl_data&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        veranl_data = self._getReadRetValOrRaiseException(resp)
        self._translateVeranlagung(veranl_data)
        return veranl_data

    def getAfaData(self, whg_id: int, vj: int) -> dict:
        """
        Note: this method will provide afa data
        whose vj_ab is equal *or earlier* than the given vj
        :param whg_id:
        :param vj:
        :return:
        """
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=afa_data&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        afa_data = self._getReadRetValOrRaiseException(resp)
        self._translateVeranlagung(afa_data)
        return afa_data

    def _translateVeranlagung(self, data: dict):
        if data:
            data['art_afa'] = 'linear' if data['lin_deg_knz'] == 'l' else 'degressiv'
            if 'angeschafft_am' in data and data['angeschafft_am']:
                data['angeschafft_am'] = \
                    datehelper.convertIsoToEur(data['angeschafft_am'])

    def existsAfaData(self, whg_id: int, vj: int) -> bool:
        """
        Note: this methods will check for a vj_ab which is *equal* to the given vj
        as opposed to method getAfaData
        :param whg_id:
        :param vj:
        :return:
        """

        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=exists_afa_data&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        exists = self._getReadRetValOrRaiseException(resp)
        return exists

    def getAfaId(self, whg_id: int, vj: int) -> int:
        """
        Note: this methods will check for a record whose vj_ab
        is *equal* to the given vj as opposed to method getAfaData
        :param whg_id:
        :param vj:
        :return:
        """

        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=afa_id&id=' +
                str(whg_id) + '&vj=' + str(vj) + '&user=' + self.__user)
        iddict = self._getReadRetValOrRaiseException(resp)
        return 0 if iddict is None else int(iddict['afa_id'])

    '''
    insert afa
    '''
    def insertAfaData(self, afa_dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_afa&user=' + self.__user,
                 data=afa_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update afa
    '''
    def updateAfaData(self, afa_dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_afa&user=' + self.__user,
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
            'einhwert_az': xxxxxxxxxxxxxxx
        }
        :return:
        """
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_whg_veranlag&user=' + self.__user,
                 data=data)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval


    '''
    insert mtl ein_aus
    '''
    def insertMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update mtl ein_aus
    '''
    def updateMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    terminate mtl ein_aus
    '''
    def terminateMtlEinAus(self, mea_id, gueltig_bis):
        d = {'mea_id': mea_id, 'gueltig_bis': gueltig_bis}
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=terminate_mtl_ein_aus&user=' + self.__user,
                 data=d)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete mtl ein_aus
    '''
    def deleteMtlEinAus(self, mea_id):
        d = {'mea_id': mea_id}
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_mtl_ein_aus&user=' + self.__user, data=d)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert sonstige ein_aus
    '''
    def insertSonstEinAus(self, sea_dict: dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_sonst_ein_aus&user=' + self.__user,
                 data=sea_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
     update sonstige ein_aus
     '''
    def updateSonstEinAus(self, sea_dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_sonst_ein_aus&user=' + self.__user,
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
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_sonst_ein_aus&user=' + self.__user, data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert grundsteuer
    '''
    def insertGrundsteuer(self, gs_dict: dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_grundsteuer&user=' + self.__user,
                 data=gs_dict)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
     update grundsteuer
     '''
    def updateGrundsteuer(self, gs_dict):
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_grundsteuer&user=' + self.__user,
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
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_grundsteuer&user=' + self.__user,
                 data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert new rechnung
    '''
    def insertRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_rechnung&user=' + self.__user, data=rgdictcopy)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update rechnung
    '''
    def updateRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_rechnung&user=' + self.__user,
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
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_rechnung&user=' + self.__user, data=delData)

        retval = self._getWriteRetValOrRaiseException(resp)

        return retval

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
                serviceError = ServiceException(500, 'Requested service not found.')
            else:
                serviceError = ServiceException( resp.status_code, resp.text )
            print(serviceError.toString())
            raise serviceError

        ret = None
        try:
            ret = json.loads(resp.content)
        except ValueError as e:
            print(e)
            msg: str = ''.join((str(type(e)), ': ', e.args[0]))
            print(msg)
            raise ServiceException(str(self.JSONERROR), msg)

        except Exception as x:
            dataError = DataError(resp.status_code, resp.content)
            raise dataError

        return ret

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
    prov.connect('martin', 'fuenf55')
    afa = {
        'afa_id': 1,
        'betrag': 111,
        'prozent': 1.23,
        'lin_deg_knz': 'l',
        'afa_wie_vorjahr': 'J'
    }
    prov.updateAfaData(afa)

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

# def getWohnungsUebersicht( ):
#     f = urllib.request.urlopen('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_wohnungen')
#     js = f.read().decode( 'utf-8' )
#     print(js)
#
#     dec = json.loads( js ) #dec is a list now
#
#     l = len(dec)
#     print( "Länge: ", l )
#     l = len( dec[1] )
#     print( "Länge des zweiten Eintrags: ", l )
#     print( dec[1] )
#     print( dec[1]['ort'] )
#     return dec



# r = testRequests()
# print( r.content )