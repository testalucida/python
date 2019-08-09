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

class AbstractWvException(Exception):
    def __init__(self, rc: str, msg: str):
        Exception.__init__(self, rc, msg)
        self.__rc = rc
        self.__msg = msg

    def rc(self):
        return self.__rc

    def message(self):
        return self.__msg

    # @abstractmethod
    # def toString(self):
    #     pass

#+++++++++++++++++++++++++++++++++++++++++++++

class ConnectException(AbstractWvException):
    def __init__(self, rc: str, msg: str):
        Exception.__init__(self, rc, msg)
        self.__rc = rc
        self.__msg = msg

    # def message(self):
    #     return self.__msg
    #

    # def toString(self):
    #     pass

#+++++++++++++++++++++++++++++++++++++++++++++

class ServiceException(AbstractWvException):
    def __init__(self, rc, msg):
        AbstractWvException.__init__(self, rc, msg)


#+++++++++++++++++++++++++++++++++++++++++++++

class DataError(AbstractWvException):
    def __init__(self, retVal: dict):
        AbstractWvException.__init__(self, retVal['rc'], retVal['errormsg'])
        self.__retVal = retVal

    def toString(self):
        s: str = '+++++DataError+++++\n'
        for k, v in self.__retVal.items():
            s = s + k + ': ' + str(v) + '\n'
        return s

#+++++++++++++++++++++++++++++++++++++++++++++

class ValidationError(AbstractWvException):
    def __init__(self, msg: str):
        AbstractWvException.__init__(self, '-1', msg)

    def toString(self):
        return self.message()

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

    def _checkException(self, resp, cls: type, additionalText: str = None) -> None:
        if resp.status_code != 200:
            msg = resp.text
            if additionalText:
                msg = ''.join((msg, '\n', additionalText))
            ex = cls(resp.status_code, msg)
            raise ex

    def connect(self, user, pwd) -> None:
        self.__user = user
        d = {'user':user, 'password':pwd}
        resp = self.__session.post('http://localhost/kendelweb/dev/php/login.php', data=d )
        self._checkException(resp, ConnectException, ''.join(('user: ', user)))

    def getWohnungsUebersicht(self) -> list:
        """
        :return: a list of dictionaries, e.g.:
        <class 'list'>: [{'whg_id': '3', 'plz': '90429', 'ort': 'Nürnberg', 'strasse': 'Austr. 22', 'whg_bez': '2. OG'},
                         {'whg_id': '2', 'plz': '90429', 'ort': 'Nürnberg', 'strasse': 'Mendelstr. 24', 'whg_bez': '3. OG links'},
                         {'whg_id': '1', 'plz': '90429', 'ort': 'Nürnberg', 'strasse': 'Mendelstr. 24', 'whg_bez': '3. OG rechts'}]
        """
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_wohnungen&' +
                'user=' + self.__user)
        self._checkException(resp, ServiceException)
        whg_list = json.loads(resp.content)
        return whg_list

    def getWohnungDetails(self, whg_id ):
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=detail&id=' + whg_id + '&user=' +
                self.__user )
        return resp

    def getWohnungIdentifikation(self, whg_id ):
        resp = self.__session.\
            get('http://localhost/kendelweb/dev/php/business.php?q=wohnung_kurz&id=' + whg_id + '&user=' +
                self.__user )
        return resp

    def getRechnungsUebersicht( self, whg_id: int ) -> list:
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=uebersicht_rechnungen&id=' +
                str( whg_id ) + '&user=' + self.__user)
        self._checkException(resp, ServiceException)
        rg_list = json.loads(resp.content)
        rg_list = self._getDictEurDate(rg_list, 'rg_datum', 'rg_bezahlt_am')
        return rg_list

    def getMtlEinAusData(self, whg_id: int):
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=mtl_ein_aus_data&id=' +
                str(whg_id) + '&user=' + self.__user)
        self._checkException(resp, ServiceException)
        mea_data = json.loads(resp.content)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    def getCurrentAndFutureMtlEinAus(self, whg_id:int) -> list:
        resp = self.__session. \
            get('http://localhost/kendelweb/dev/php/business.php?q=current_future_mtl_ein_aus&id=' +
                str(whg_id) + '&user=' + self.__user)
        self._checkException(resp, ServiceException)
        mea_data = json.loads(resp.content)
        mea_data = self._getDictEurDate(mea_data, 'gueltig_ab', 'gueltig_bis')
        return mea_data

    '''
    insert mtl ein_aus
    '''
    def insertMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update mtl ein_aus
    '''
    def updateMtlEinAus(self, mea_dict):
        meadictcopy = self._getDictCopyIsoDate(mea_dict, 'gueltig_ab', 'gueltig_bis')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_mtl_ein_aus&user=' + self.__user,
                 data=meadictcopy)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    terminate mtl ein_aus
    '''
    def terminateMtlEinAus(self, mea_id, gueltig_bis):
        d = {'mea_id': mea_id, 'gueltig_bis': gueltig_bis}
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=terminate_mtl_ein_aus&user=' + self.__user,
                 data=d)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete mtl ein_aus
    '''
    def deleteMtlEinAus(self, mea_id):
        d = {'mea_id': mea_id}
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_mtl_ein_aus&user=' + self.__user, data=d)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    insert new rechnung
    '''
    def insertRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=insert_rechnung&user=' + self.__user, data=rgdictcopy)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    update rechnung
    '''
    def updateRechnung(self, rg_dict):
        rgdictcopy = self._getDictCopyIsoDate(rg_dict, 'rg_datum', 'rg_bezahlt_am')
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=update_rechnung&user=' + self.__user,
                 data=rgdictcopy)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    '''
    delete rechnung
    '''
    def deleteRechnung(self, rg_id):
        delData = {}
        delData['rg_id'] = str(rg_id)
        resp = self.__session. \
            post('http://localhost/kendelweb/dev/php/business.php?q=delete_rechnung&user=' + self.__user, data=delData)

        retval = self.__getWriteRetValOrRaiseException(resp)

        return retval

    def _getDictCopyIsoDate(self, orig: dict, *keys) -> dict:
        copy = dict(orig)
        for key in keys:
            copy[key] = datehelper.convertEurToIso(copy[key])
        return copy

    def _getDictEurDate(self, origList: list, *keys) -> dict:
        for rgdict in origList:
            for key in keys:
                rgdict[key] = datehelper.convertIsoToEur(rgdict[key])
        return origList

    def __getWriteRetValOrRaiseException(self, resp):
        if resp.status_code != 200:
            serviceError = ServiceException( resp.status_code, resp.text )
            print(serviceError.toString())
            raise serviceError

        dic = {}
        try:
            dic = json.loads(resp.content)
        except ValueError as e:
            msg: str = "+++++++++JSON Decode Error+++++++++\n" + e + \
                       "\nresp.content:\n" + resp.content + \
                       "\n+++++++++++++++++++++++++++++++++++\n"
            print(msg)
            raise ServiceException(self.JSONERROR, msg)

        if dic['rc'] != 0:
            dataError = DataError(dic)
            raise dataError

        return WriteRetVal(dic['rc'], dic['obj_id'])



######### For testing purposes only ########################
#
# prov = DataProvider()
# prov.connect('martin', 'fuenf55')
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