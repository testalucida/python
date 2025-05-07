import ftplib
import os
from crypt import EncryptDecrypt

class ftp:
    def __init__( self ):
        self._remotepath = ""
        self._localpath = ""
        self._filename = 'notes.db'
        self._localfile = self._localpath + self._filename
        self._ftp:ftplib.FTP = None

    def _login( self ) -> None:
        ftp_infos = self._getFtpInfos()
        self._ftp = ftplib.FTP( ftp_infos['server'] )
        self._remotepath = ftp_infos['remotepath']
        self._localpath = ftp_infos['localpath']
        self._ftp.login( ftp_infos['user'], ftp_infos['pwd'] )
        self._ftp.cwd( self._remotepath )

    def _checkLoggedIn( self ) -> None:
        if not self._ftp:
            self._login()

    def upload( self ) -> None:
        self._checkLoggedIn()
        self._ftp.storbinary( 'STOR ' + self._filename, open( self._localfile, 'rb' ) )
        self._ftp.quit()

    def download( self ) -> None:
        """
        Downloads note.db from server.
        Maybe the server file doen't not yet exist, that's not an error but probably a first access problem.
        The downloaded file is named xxx.tmp and only if no error occurred it will be renamed.
        """
        self._checkLoggedIn()
        try:
            tmpfile = self._localfile + ".tmp"
            savfile = self._localfile + ".sav"
            self._ftp.retrbinary( "RETR " + self._filename, open( tmpfile, 'wb' ).write )
            # still here - download ok. Save the old database, rename the downloaded one.
            try:
                os.remove( savfile )
            except Exception as x:
                print( "ftp.download(): couldn't delete %s:\n%s\nProceeding." % (savfile, x) )

            try:
                os.rename( self._filename, savfile )
            except Exception as x:
                print( "ftp.download(): couldn't rename %s to %s:\n%s" % (self._filename, savfile, x ) )
                raise x

            try:
                os.rename( tmpfile, self._filename )
            except Exception as x:
                print( "ftp.download(): couldn't rename %s to %s:\n%s" % (tmpfile, self._filename, x) )
                raise x
        except Exception as x:
            print( "ftp.download(): Download %s to %s failed:\n%s" % (self._filename, self._localfile, x ) )
        self._ftp.quit()

    def _getFtpInfos( self ) -> dict:
        infos: dict = { }
        with open( "ftp.ini" ) as inifile:
            for line in inifile:
                parts = line.split( "=" )
                infos[parts[0]] = parts[1].rstrip()

        user, pwd = self._getUserAndPwd( infos['key_file'], infos['enc_user_file'], infos['enc_pwd_file'] )
        infos['user'] = user
        infos['pwd'] = pwd
        return infos

    def _getUserAndPwd( self, key_file:str, enc_user_file:str, enc_pwd_file:str ) -> (str, str):
        ed = EncryptDecrypt()
        ed.loadKey( key_file )
        user:str = ed.getDecryptedAsString( enc_user_file )
        pwd:str = ed.getDecryptedAsString( enc_pwd_file )
        return (user, pwd)

def test():
    f = ftp()
    #f.login()
    f.download()

if __name__ == '__main__':
    test()
