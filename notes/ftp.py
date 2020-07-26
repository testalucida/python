import ftplib
from crypt import EncryptDecrypt

class ftp:
    def __init__( self, isRelease:bool=False ):
        self._remotepath = ""
        self._localpath = ""
        self._filename = 'notes.db'
        self._localfile = self._localpath + self._filename
        self._ftp:ftplib.FTP = None

    def login( self ) -> None:
        ftp_infos = self._getFtpInfos()
        self._ftp = ftplib.FTP( ftp_infos['server'] )
        self._remotepath = ftp_infos['remotepath']
        self._localpath = ftp_infos['localpath']
        self._ftp.login( ftp_infos['user'], ftp_infos['pwd'] )
        self._ftp.cwd( self._remotepath )

    def upload( self ) -> None:
        self._ftp.storbinary( 'STOR ' + self._filename, open( self._localfile, 'rb' ) )
        self._ftp.quit()

    def download( self ) -> None:
        self._ftp.retrbinary( "RETR " + self._filename, open( self._localfile, 'wb' ).write )
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
    f.login()
    f.download()

if __name__ == '__main__':
    test()
