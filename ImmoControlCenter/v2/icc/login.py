import urllib.request
from typing import Callable, Dict

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QApplication, QDialog
from logindialog import LoginDialog

# login_success = Signal()
# login_failed = Signal()

def checkCredentials___( user, pwd ) -> Dict:
    # leider unbrauchbar, da ich versehentlich den Account kendel-bueroservice im Jan. 2025 gelöscht habe :-(
    url = "https://www.cgiref.kendel-bueroservice.de/check.py?"
    url_step1 = url + "user=" + user
    resp = urllib.request.urlopen( url_step1 ).read()
    resp_dec = resp.decode()
    # remove leading and trailing line breaks:
    resp_dec = resp_dec[1:-1]
    dic = eval( resp_dec )
    if dic["rc"] != "0":
        #return "Login failed. Message from server is '%s', RC = '%s'." % (dic["msg"], dic["rc"] )
        return dic
    sessionId = dic["msg"]
    url_step2 = url + "session_id=" + sessionId + "&user=" + user + "&pwd=" + pwd
    resp = urllib.request.urlopen( url_step2 ).read().decode()
    resp = resp[1:-1]
    return eval( resp )

def checkCredentials( user, pwd ) -> Dict:
    # Billig-Ersatzversion für checkCredentials___(..)
    dicRc = {
        "rc": "0",
        "msg": ""
    }
    if not (user == "martin" and pwd == "Iiii999"):
        dicRc["rc"] = "-1"
        dicRc["msg"] = "User oder Passwort falsch."
    return dicRc

def showError( msg:str ) -> None:
    box = QMessageBox()
    box.setWindowTitle( "Login failed" )
    box.setText( msg )
    box.exec_()

def login() -> bool:
    def onOk():
        user = dlg.getUser()
        pwd = dlg.getPwd()
        if "" in (user, pwd):
            showError( "You loser failed." )
        else:
            resp: Dict = checkCredentials( user, pwd )
            if resp["rc"] != "0":
                showError( resp["msg"] + "ErrNo=" + resp["rc"] )
            else:
                dlg.accept()
        print( user )
        print( pwd )

    def onCancel():
        dlg.reject()

    #app = QApplication()
    dlg = LoginDialog()
    dlg.ok_pressed.connect( onOk )
    dlg.cancel_pressed.connect( onCancel )
    rc = dlg.exec_()

    return True if rc == QDialog.Accepted else False

if __name__ == "__main__":
    import sys
    sys.path.append( "../common" )
    app = QApplication()
    if login():
        print( "YEP" )
    else: print( "NOPE" )
    #app.exec_()
