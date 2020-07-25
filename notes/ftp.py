import ftplib

class ftp:
    def __init__( self, isRelease:bool=False ):
        self._remotepath_dev = '/notes_dev/'
        self._remotepath_rel = '/notes_rel/'
        self._remotepath = self._remotepath_rel if isRelease else self._remotepath_dev
        self._localpath_dev = '/home/martin/Projects/python/notes/'
        self._localpath_rel = '/home/martin/notes/'
        self._localpath = self._localpath_rel if isRelease else self._localpath_dev
        self._filename = 'notes.db'
        self._localfile = self._localpath + self._filename
        self._ftp = ftplib.FTP( "85.13.141.232" )

    def login( self, user:str, pwd:str ) -> None:
        self._ftp.login( user, pwd )
        self._ftp.cwd( self._remotepath )

    def upload( self ) -> None:
        self._ftp.storbinary( 'STOR ' + self._filename, open( self._localfile, 'rb' ) )
        self._ftp.quit()

    def download( self ) -> None:
        self._ftp.retrbinary( "RETR " + self._filename, open( self._localfile, 'wb' ).write )
        self._ftp.quit()


def test():
    f = ftp()
    f.login( "w00e41b7", "X64cppmm" )
    f.download()

if __name__ == '__main__':
    test()