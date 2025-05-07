import os

# from paramiko.sftp_client import SFTP
from sftp import SFTP
import datehelper
from ftp import FtpIni
#from sftp import SFTP
from v2.einaus.einauslogic import EinAusLogic
from v2.icc.definitions import ROOT_DIR
from v2.icc.iccdata import IccData
from v2.icc.icclogic import IccLogic
from v2.icc.interfaces import XSummen


class MainLogic( IccLogic ):
    def __init__( self ):
        IccLogic.__init__( self )

    @staticmethod
    def saveLetzteBuchung( datum:str, text:str ):
        """
        speichert die Daten der letzten Buchung.
        :param datum: Datumstring im ISO-Format
        :param text:
        :return: None
        """
        data = IccData()
        data.deleteLetzteBuchung()
        data.insertLetzteBuchung( datum, text )
        data.commit()

    @staticmethod
    def exportDatabaseToServer( deleteLocalDb:bool=True ):
        """
        Lädt die immo-Datenbank auf den Server.
        Löscht die lokale Db, wenn <deleteLocalDb> == True
        :return:
        """
        ######## ALT -- all-inkl
        # ftpini = FtpIni( ROOT_DIR + "/ftp.ini" )
        # ftp = Ftp( ftpini )
        # try:
        #     ftp.connect()
        #     ftp.upload( "immo.db", "immo.db" )
        ######## NEU -- alfa
        ftpini = FtpIni( ROOT_DIR + "/ftp_ssl_alfa.ini" )
        user, pwd = ftpini.getUserAndPwd()
        remotepath = ftpini.getRemotePath()
        localpath = ftpini.getLocalPath()
        localdb = localpath + "immo.db"
        remotedb = remotepath + "immo.db"
        print( "Upload " + localdb + " to " + remotedb )
        try:
            sftp = SFTP( ftpini.getServer(), 22, user, pwd )
            sftp.openConnection()
            sftp.upload( localdb, remotedb )
            sftp.closeConnection()
            os.remove( localdb )
        except Exception as ex:
            raise ex

    # @staticmethod
    # def getFtpLocalPath() -> str:
    #     ftpini = FtpIni( "ftp.ini" )
    #     return ftpini.getLocalPath()

    @staticmethod
    def importDatabaseFromServer():
        """
        Lädt die Datenbank vom Server ins lokale Verzeichnis.
        Benennt die remote Datenbank um in "immo.db_2025-04-05:12.34.56.123456" (Name + Timestamp)
        :return:
        """
        ftpini = FtpIni( ROOT_DIR + "/ftp_ssl_alfa.ini" )
        user, pwd = ftpini.getUserAndPwd()
        remotepath = ftpini.getRemotePath()
        localpath = ftpini.getLocalPath()
        localdb = localpath + "immo.db"
        remotedb = remotepath + "immo.db"
        print( "Download " + remotedb + " to " + localdb )
        try:
            sftp = SFTP( ftpini.getServer(), 22, user, pwd )
            sftp.openConnection()
            sftp.download( remotedb, localdb )
            ts = datehelper.getCurrentTimestampIso()
            sftp.rename(remotedb, remotedb + "_" + ts )
            sftp.closeConnection()
        except Exception as ex:
            print( "MainLogic.importDatabaseFromServer(): \n" + str(ex) )
            sftp.closeConnection()
            raise ex

    @staticmethod
    def checkDatabaseExistsLocal() -> bool:
        dbpathnfile = ROOT_DIR + "/immo.db"
        return os.path.isfile( dbpathnfile )

    @staticmethod
    def getSummen( jahr:int ) -> XSummen:
        ea_logic = EinAusLogic()
        x = XSummen()
        x.sumEin = round( ea_logic.getEinnahmenSumme( jahr ) )
        x.sumHGV = round( ea_logic.getHGVAuszahlungenSumme( jahr ) )
        x.sumSonstAus = round( ea_logic.getAuszahlungenSummeOhneHGV( jahr ) )
        x.saldo = x.sumEin + x.sumHGV + x.sumSonstAus
        return x