import ftplib
import os

from mycrypt import EncryptDecrypt

class FtpIni:
    def __init__( self, ini_pathnfile:str ):
        """
        structure of ini file:
            server=nn.nn.nn.nnn
            remotepath=server path (not: file name) specifying the folder the local file is to be uploaded to
                        resp.the remote file to be downloaded is located
            localpath=local path (not: file name) specifying the folder the remote file is to be downloaded to
                        resp. the file to be uploaded is located
            key_file=path and name of the file containing the key (and only the key)
            enc_user_file=path and name of the file containing the encrypted user name (and only this item)
            enc_pwd_file=path and name of the file containing the encrypted password (and only that)
        :param ini_pathnfile: path and file to ftp ini file.
        """
        self._ini_pathnfile = ini_pathnfile  # path and name to ftp.ini file
        self._server: str = ""
        self._remotepath = ""
        self._localpath = ""
        self._key_file = ""
        self._enc_user_file = ""
        self._enc_pwd_file = ""
        self._readIniFile()

    def _readIniFile( self ):
        infos: dict = { }
        with open( self._ini_pathnfile ) as inifile:
            for line in inifile:
                parts = line.split( "=" )
                infos[parts[0]] = parts[1].rstrip()
        self._server = infos["server"]
        self._remotepath = infos["remotepath"]
        self._localpath = infos["localpath"]
        self._key_file = infos["key_file"]
        self._enc_user_file = infos["enc_user_file"]
        self._enc_pwd_file = infos["enc_pwd_file"]

    def getServer( self ) -> str:
        return self._server

    def getLocalPath( self ) -> str:
        return self._localpath

    def getRemotePath( self ) -> str:
        return self._remotepath

    def getUserAndPwd( self ) -> (str,str):
        crypt = EncryptDecrypt()
        key = crypt.getKey( self._key_file )
        user:bytes = crypt.getDecryptedFromFile( key, self._enc_user_file )
        pwd:bytes = crypt.getDecryptedFromFile( key, self._enc_pwd_file )
        return ( user.decode(), pwd.decode() )

class Ftp:
    def __init__( self, ftpIni:FtpIni ):
        self._ftpIni = ftpIni
        self._ftp: ftplib.FTP = None

    def connect( self ):
        """
        needs to be called before first up- or download
        :return:
        """
        self._ftp: ftplib.FTP = ftplib.FTP( self._ftpIni.getServer() )
        user_and_pwd = self._ftpIni.getUserAndPwd()
        self._ftp.login( user_and_pwd[0], user_and_pwd[1] )

    def quit( self ):
        """
        needs to be called after last up- or download
        :return:
        """
        self._ftp.quit()

    def upload( self, localfilename:str, remotefilename:str ) -> None:
        """
        stores file <localfilename> from folder self._ftpIni.getLocalPath() as file <remotefilename> to
        folder self._ftpIni.getRemotePath()
        :param localfilename:
        :param remotefilename:
        :return:
        """
        io = open( self._ftpIni.getLocalPath() + localfilename, 'rb' )
        self._ftp.cwd( self._ftpIni.getRemotePath() )
        self._ftp.storbinary( 'STOR ' + remotefilename, io )

    def download( self, remotefilename:str, localfilename:str ) -> None:
        """
        Downloads file <remotefilename> in folder self._ftpIni.getRemotePath() as file <localfilename>
        to folder self._ftpIni.getLocalPath()
        Maybe the server file doesn't exist yet, that might be not an error but probably a first access problem.
        The downloaded file is named xxx.tmp and only if no error occurred it will be renamed.
        1.) download <remotefilename> and save it as <localfilename.tmp>
        2.) if exists <localfilename.sav>: delete it
        3.) if exists <localfilename>: rename it to <localfilename.sav>
        4.) rename <localfilename.tmp> to localfilename
        """
        remotepathnfile = self._ftpIni.getRemotePath() + remotefilename
        localpathnfile = self._ftpIni.getLocalPath() + localfilename
        try:
            tmpfile = localpathnfile + ".tmp"
            savfile = localpathnfile + ".sav"
            # step 1:
            self._ftp.retrbinary( "RETR " + remotepathnfile, open( tmpfile, 'wb' ).write )
            # still here - download ok. Save the old file, rename the downloaded one.
            try:
                # step 2:
                if os.path.exists( savfile ):
                    os.remove( savfile )
            except Exception as x:
                # no problem - there was no .sav file
                print( "ftp.download(): couldn't delete %s:\n%s\nProceeding." % (savfile, str( x ) ) )
            try:
                if os.path.exists( localpathnfile ):
                    os.rename( localpathnfile, savfile )
            except Exception as x:
                print( "ftp.download(): couldn't rename %s to %s:\n%s" % ( localpathnfile, savfile, str( x ) ) )
                raise x

            try:
                os.rename( tmpfile, localpathnfile )
            except Exception as x:
                print( "ftp.download(): couldn't rename %s to %s:\n%s" % (tmpfile, localpathnfile, str( x ) ) )
                raise x
        except Exception as x:
            # delete (empty) tmp file:
            os.remove( tmpfile )
            raise( x )
            #raise( Exception( "ftp.download(): Download %s to %s failed:\n%s" % ( remotepathnfile, localpathnfile, str( x ) ) ) )




def testUpAndDownload():
    ftpIni = FtpIni( "../ImmoControlCenter/ftp.ini" )
    ftp = Ftp( ftpIni )
    ftp.connect()
    #ftp.upload( "immo.db", "immodb.test" )
    ftp.download( "immo_state", "immo_state" )
    ftp.quit()

