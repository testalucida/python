from cryptography.fernet import Fernet

class EncryptDecrypt:
    def __init__( self ):
        pass

    def createKeyAndSave( self, pathnfile:str ):
        """
        Creates a new crypt key and saves it to the given pathnfile.
        The file may only have one line which contains the key.
        Needs to be run only once. Read the file (the key) whenever you want to decrypt
        a string previously encrypted using this key.
        """
        key:bytes = Fernet.generate_key()
        with open( pathnfile, "wb", ) as key_file:
            key_file.write( key )

    def getKey( self, pathnfile:str ) -> bytes:
        """
        Read the crypt key from the given file.
        """
        with open( pathnfile, "rb" ) as keyfile:
            return keyfile.read()

    def encryptAndStore( self, key: bytes, strToEncrypt: str, pathnfile: str ):
        """
        Encrypts <strToEncrypt> using <key> and stores it to <pathnfile>
        :param key:
        :param strToEncrypt:
        :param pathnfile:
        :return: None
        """
        with open( pathnfile, "wb" ) as file_enc:
            file_enc.write( self.encrypt( key, strToEncrypt ) )

    # def encryptAndStore(self, key: bytes, *strings2Encrypt, pathnfile: str):
    #     """
    #     Encrypts each string contained in <strings2Encrypt> using <key> and stores them to <pathnfile>
    #     Each string will create a new line in <pathnfile>
    #     :param key:
    #     :param strings2Encrypt: Variable Argumentliste
    #     :param pathnfile:
    #     :return: None
    #     """
    #     with open(pathnfile, "wb") as file_enc:
    #         for string in strings2Encrypt:
    #             file_enc.write( self.encrypt(key, string ))

    def encrypt( self, key:bytes, strToEncrypt: str ) -> bytes:
        """
        Encrypts the given string <strToEncrypt> using  key and returns it encrypted
        """
        f = Fernet( key )
        encoded:bytes = strToEncrypt.encode() #convert s to bytes using utf-8 codec
        encrypted:bytes = f.encrypt( encoded )
        return encrypted

    def decryptEncrypted( self, key:bytes, enc_str:bytes ) -> bytes:
        """
        Decrypts an encrypted string enc_str using key and returns the decrypted bytes.
        """
        f = Fernet( key )
        return f.decrypt( enc_str )

    def getDecryptedFromFile( self, key:bytes, enc_pathnfile:str ) -> bytes:
        """
        Reads a file containing an encrypted content and decrypts this content using key.
        """
        with open( enc_pathnfile, "rb" ) as enc_file:
            encrypted = enc_file.read()
        return self.decryptEncrypted( key, encrypted )


def createEncryptAndSave():
    ed = EncryptDecrypt()
    path = "/home/martin/secrets/"
    key = ed.getKey( path + "icc_ftp.key" )
    # ed.encryptAndStore( key, "web27784572", pathnfile=path + "icc_ftpalfa_user.enc"  )
    # ed.encryptAndStore( key, "Aaaa111#", pathnfile=path + "icc_ftpalfa_pwd.enc"  )
    ed.encryptAndStore( key, "web27784572@alfa3074", pathnfile=path + "icc_sftpalfa_user.enc"  )
    ed.encryptAndStore( key, "Aaaa111#", pathnfile=path + "icc_sftpalfa_pwd.enc"  )
    # Kontrolle:
    user = ed.getDecryptedFromFile(key, path + "icc_sftpalfa_user.enc").decode()
    pwd = ed.getDecryptedFromFile(key, path + "icc_sftpalfa_pwd.enc").decode()
    print(user, ": ", pwd)


# createEncryptAndSave()

def test():
    path = ""
    keyfile = ""
    userfile = ""
    pwdfile = ""
    crypt = EncryptDecrypt()
    key = crypt.getKey( path + keyfile )
    user = crypt.getDecryptedFromFile( key, path + userfile ).decode()
    pwd = crypt.getDecryptedFromFile( key, path + pwdfile ).decode()
    print( user, ": ", pwd )