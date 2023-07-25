
from ftp import FtpIni, Ftp
from v2.einaus.einauslogic import EinAusLogic
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

    def exportDatabaseToServer( self, datum:str, text:str ):
        """
        Speichert die immo-Datenbank auf dem Server.
        Vorher werden noch die Daten der letzten Buchung in der Datenbank gespeichert (Tabelle letztebuchung)
        :param datum: Datum der letzten Buchung
        :param text:  Text der letzten Buchung
        :return:
        """
        import os
        path = os.getcwd()
        print( "current work directory: ", path )
        ftpini = FtpIni( "v2/ftp.ini" )
        ftp = Ftp( ftpini )
        # store last booking
        self.saveLetzteBuchung( datum, text )
        try:
            ftp.connect()
            ftp.upload( "immo.db", "immo.db" )
        except Exception as ex:
            raise ex
        finally:
            ftp.quit()

    @staticmethod
    def getFtpLocalPath() -> str:
        ftpini = FtpIni( "ftp.ini" )
        return ftpini.getLocalPath()

    @staticmethod
    def importDatabaseFromServer( localname:str ):
        ftpini = FtpIni( "ftp.ini" )
        ftp = Ftp( ftpini )
        try:
            ftp.connect()
            ftp.download( "immo.db", localname )
        except Exception as ex:
            raise ex
        finally:
            ftp.quit()

    @staticmethod
    def getSummen( jahr:int ) -> XSummen:
        ea_logic = EinAusLogic()
        x = XSummen()
        x.sumEin = round( ea_logic.getEinnahmenSumme( jahr ) )
        x.sumHGV = round( ea_logic.getHGVAuszahlungenSumme( jahr ) )
        x.sumSonstAus = round( ea_logic.getAuszahlungenSummeOhneHGV( jahr ) )
        x.saldo = x.sumEin + x.sumHGV + x.sumSonstAus
        return x