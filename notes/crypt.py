from cryptography.fernet import Fernet

class EncryptDecrypt:
    def __init__( self ):
        self._key:bytes = None

    def createKey( self ):
        """
        Creates a new crypt key
        """
        self._key = Fernet.generate_key()

    def writeKey( self, pathnfile:str ) -> None:
        """
        writes the previously created crypt key into the given file
        """
        with open( pathnfile, "wb" ) as keyfile:
            keyfile.write( self._key )

    def loadKey( self, pathnfile:str ) -> None:
        """
        Read the crypt key from the given file.
        """
        with open( pathnfile, "rb" ) as keyfile:
            self._key = keyfile.read()

    def encrypt( self, s: str ) -> bytes:
        """
        Encrypts the given string s with the previously loaded key and
        returns it encrypted
        """
        f = Fernet( self._key )
        encoded:bytes = s.encode() #convert s to bytes using utf-8 codec
        encrypted:bytes = f.encrypt( encoded )
        return encrypted

    def writeEncryptedString( self, enc_str:bytes, pathnfile:str ) -> None:
        """
        Writes encrypted string enc_str to file given by path and file name
        """
        with open( pathnfile, "wb" ) as keyfile:
            keyfile.write( enc_str )

    def decryptEncrypted( self, enc_str:bytes ) -> bytes:
        """
        Decrypt encrypted string enc_str using self._key and returns it.
        Previously you have to have called createKey or load key.
        """
        f = Fernet( self._key )
        decrypted:bytes = f.decrypt( enc_str )
        return decrypted

    def getDecryptedAsString( self, pathnfile:str ) -> str:
        """
        Reads file pathnfile and returns its decrypted content which has to be encrypted.
        This file may contain only one string.
        createKey() or loadKey() must have been called previously.
        """
        with open( pathnfile, "rb" ) as keyfile:
            enc = keyfile.read()
        decrypted:bytes = self.decryptEncrypted( enc )
        return decrypted.decode()


def testCreateAndWriteKey():
    ed = EncryptDecrypt()
    ed.createKey()
    ed.writeKey( "testkey.key" )
    print( "Wrote key ", ed._key )

def testEncrypt():
    ed = EncryptDecrypt()
    ed.loadKey( "testkey.key" )
    to_encrypt = "mypassword"
    enc = ed.encrypt( to_encrypt )
    ed.writeEncryptedString( enc, "pwd.enc" )
    print( "Wrote encrypted string ", to_encrypt, ": ", enc )

def testDecrypt():
    ed = EncryptDecrypt()
    ed.loadKey( "testkey.key" )
    pwd = ed.getDecryptedAsString( "pwd.enc")
    print( "Decrypted password: ", pwd )

def encrypt_ftp_user_and_pwd( isRelease:bool ):
    """
    Creates a new key and encrypts user and password (for ftp in this case, but that's not relevant
    only for remembrance purposes.
    """
    user = ""
    pwd = ""
    dir_rel:str = ""
    dir_dev:str = ""
    dir:str = dir_rel if isRelease else dir_dev
    key_file = dir + ""
    user_file = dir + ""
    pwd_file = dir + ""
    ed = EncryptDecrypt()
    ed.createKey()
    ed.writeKey( key_file )
    enc_user: bytes = ed.encrypt( user )
    ed.writeEncryptedString( enc_user, user_file )
    enc_pwd: bytes = ed.encrypt( pwd )
    ed.writeEncryptedString( enc_pwd, pwd_file )

    validate_ftp_user_and_pwd( key_file, user_file, pwd_file )

def validate_ftp_user_and_pwd( key_file, user_file:str, pwd_file:str ):
    ed = EncryptDecrypt()
    ed.loadKey( key_file )
    user = ed.getDecryptedAsString( user_file )
    pwd = ed.getDecryptedAsString( pwd_file )
    print( "Validated: user = %s, pwd = %s" % (user, pwd) )

if __name__ == '__main__':
    #testCreateAndWriteKey()
    #testEncrypt()
    #testDecrypt()
    encrypt_ftp_user_and_pwd( False )
