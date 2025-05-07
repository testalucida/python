import paramiko
from ftp import FtpIni


class SFTP:
    # see https://docs.couchdrop.io/walkthroughs/using-sftp-clients/using-python-with-sftp
    def __init__(self, hostname, port, user, pwd):
        self._host = hostname
        self._port = port
        self._user = user
        self._pwd = pwd
        self._ssh_client = None
        self._sftp = None

    def openConnection(self):
        # Create an SSH client
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the SFTP server
        self._ssh_client.connect( self._host, self._port, self._user, self._pwd )
        # Create an SFTP session
        self._sftp = self._ssh_client.open_sftp()

    def closeConnection( self ):
        ## close connection
        self._sftp.close()
        self._ssh_client.close()

    def listDirectory(self, directory) -> list:
        """
        :param directory: folder whose contents are to be listed
        :return: list of strings
        """
        files = self._sftp.listdir(directory)
        return files

    def createDirectory( self, new_directory ):
        self._sftp.mkdir(new_directory)

    def upload( self, localFile, remoteFile ):
        """
        :param localFile: complete path and filename of the local file to be uploaded
                    e.g. "/home/martin/documents/myfile.txt"
        :param remoteFile: path and filename of the file beeing uploaded on the server
                    e.g. "/files/martin/documents/myfile.txt"
                         The hostname (sftp.example.com) is not part of the path.
        :return:
        """
        self._sftp.put(localFile, remoteFile)

    def download( self, remoteFile, localFile ):
        """
        :param remoteFile: path and filename of the file beeing uploaded on the server
                    e.g. "/files/martin/documents/myfile.txt"
                         The hostname (sftp.example.com) is not part of the path.
       :param localFile: complete path and filename of the local file to be uploaded
                e.g. "/home/martin/documents/myfile.txt"
        :return:
        """
        print( self._sftp.stat( remoteFile ) ) # force an exception if <remotefile> does not exist.
                                                # Elsewise sftp.get() will be executed and a potentially existing
                                                # local db <localfile> will be overwritten.
        self._sftp.get( remoteFile, localFile )

    def rename( self, oldpathnfile, newpathnfile ):
        """
        renames oldpath to newpath
        :param oldpathnfile: e.g. "/files/martin/text.txt"
        :param newpathnfile: e.g. "/files/martin/text.txt_renamed"
        :return:
        """
        self._sftp.posix_rename( oldpathnfile, newpathnfile )


##############################################################################
###############  TEST TEST TEST TEST  ########################################
#def test_rename():

def test_SFTP2():
    ftpini = FtpIni( "../ImmoControlCenter/v2/icc/ftp_ssl_alfa.ini" )
    user, pwd = ftpini.getUserAndPwd()
    remotepath = ftpini.getRemotePath()
    localpath = ftpini.getLocalPath()
    localdb = localpath + "immo.db"
    remotedb = remotepath + "immo.db"
    sftp = SFTP( ftpini.getServer(), 22, user, pwd )
    sftp.openConnection()
    files = sftp.listDirectory( remotepath )
    sftp.upload( localdb, remotedb )
    sftp.closeConnection()
    print( files )

def test_SFTP():
    # Define SFTP connection parameters
    hostname = "secret"
    port = 22
    username = "secret"
    password = "secret"
    localfile = "/home/martin/kannweg/echo-client.py"
    localfile2 = "/home/martin/kannweg/server_document1"
    remotefile = "/files/martin/echo-client.py"
    remotefile2 = "/files/martin/server_document1"

    sftp = SFTP(hostname, port, username, password)
    sftp.openConnection()
    sftp.rename( remotefile2, "/files/martin/server_document1_renamed" )
    files = sftp.listDirectory("/files/martin/")
    # sftp.upload( localfile, remotefile )
    # sftp.download( remotefile2, localfile2 )
    sftp.closeConnection()
    print( files )

if __name__ == "__main__":
    test_SFTP()