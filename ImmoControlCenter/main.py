import os
import shutil
import sys
from typing import Dict
from PySide2.QtGui import QIcon

sys.path.append( "../common" )

from ftp import FtpIni, Ftp
from messagebox import ErrorBox, QuestionBox, InfoBox, WarningBox
from screen import setScreenSize
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
from icc.iccmainwindow import IccMainWindow
from maincontroller import MainController


def downloadDatabase() -> bool:
    """
    ******************
    NO! function not used. Server database has to be downloaded manually if need be.
    ******************
    get immo.db from server
    :return: True if
        - download was successful OR
        - download was not successful but user chose "Start Application Anyway".
    """
    ftpini = FtpIni( "ftp.ini" )
    ftp = Ftp( ftpini )
    try:
        ftp.connect()
        ftp.download( "immo.db", "immo.db" )
    except Exception as ex:
        box = ErrorBox( "File Transfer failed", "FTP failed.\n", str( ex ) )
        box.exec_()
        box = QuestionBox( "ICC", "Start ImmoControlCenter anyway (using local database)?", "YES", "NO" )
        rc = box.exec_()
        if rc == QMessageBox.No:
            return False
    return True

def uploadDatabase() -> bool:
    """
    upload immo.db to server
    :return: True if upload was successful
    """
    ftpini = FtpIni( "ftp.ini" )
    ftp = Ftp( ftpini )
    try:
        ftp.connect()
        ftp.upload( "immo.db", "immo.db" )
        return True
    except Exception as ex:
        box = ErrorBox( "File Transfer failed", "FTP failed.\n", str( ex ) )
        box.exec_()
        return False


class ShutDownFilter( QtCore.QObject ):
    def __init__( self, win: QWidget, app: QApplication ):
        QtCore.QObject.__init__( self )
        self._win = win
        self._app = app

    def eventFilter( self, obj, event ) -> bool:
        if obj is self._win and event.type() == QtCore.QEvent.Close:
            if self._win.canShutdown():
                self.quit_app()
            event.ignore()
            return True
        return super( ShutDownFilter, self ).eventFilter( obj, event )

    def quit_app( self ):
        saveDatabase()
        geom = self._win.geometry()
        #print( 'CLEAN EXIT. x=%d - y=%d - w=%d - h=%d' % (geom.x(), geom.y(), geom.width(), geom.height()) )
        writeGeometryOnShutdown( geom.x(), geom.y(), geom.width(), geom.height() )
        self._win.removeEventFilter( self )
        self._app.quit()


def getGeometryOnLastShutdown() -> Dict:
    f = open( "icc/icc_settings.txt", "r" )
    s = f.read()
    parts = s.split( "," )
    d = dict()
    d["x"] = int( parts[0] )
    d["y"] = int( parts[1] )
    d["w"] = int( parts[2] )
    d["h"] = int( parts[3] )
    return d


def writeGeometryOnShutdown( x, y, w, h ) -> None:
    f = open( "icc/icc_settings.txt", "w" )
    s = str( x ) + "," + str( y ) + "," + str( w ) + "," + str( h )
    f.write( s )


def saveDatabase() -> None:
    def try_copyfile():
        try:
            copyfile( src, dest )
        except Exception as ex:
            box = WarningBox( "Datenbank auf lokalen Datenträger sichern", "Sicherung nicht möglich",
                              "Ist der Datenträger eingehängt?", "Nochmal versuchen", "Beenden" )
            rc = box.exec_()
            if rc == QMessageBox.Yes:
                try_copyfile()
    from shutil import copyfile
    if runningInDev(): return
    scriptdir = os.path.dirname( os.path.realpath( __file__ ) )
    src = "./immo.db"
    if "Vermietung" in scriptdir:
        print( "Running in REL; try to copy immo.db" )
        dest = "/media/martin/Elements1/Vermietung/ImmoControlCenter/immo.db"
        if os.path.isfile( src ):
            box = QMessageBox()
            box.setIcon( QMessageBox.Question )
            box.setWindowTitle( "Sicherung der Datenbank" )
            box.setText( "Datenbank\n\n   '%s'\nsichern in\n\n   '%s'?" % (scriptdir + "/immo.db", dest) )
            box.setStandardButtons( QMessageBox.Save | QMessageBox.Cancel )
            r = box.exec_()
            if r == QMessageBox.Save:
                try_copyfile()
        else:
            box = ErrorBox( "Datenbank auf lokalen Datenträger sichern", "Sicherung nicht möglich",
                            "Es gibt keine Datenbank namens immo.db" )
            box.exec_()


def createControlFile():
    try:
        f = open( "already_running", "x" )
    except:
        box = QMessageBox()
        box.setWindowTitle( "Anwendung kann nicht gestartet werden" )
        box.setIcon( QMessageBox.Critical )
        box.setText( "Das ImmoControlCenter kann nicht gestartet werden:\n"
                     "Die Kontrolldatei kann nicht angelegt werden." )
        box.exec_()
        sys.exit( 1 )


def deleteControlFile():
    os.remove( "already_running" )


def runningInDev() -> bool:
    scriptdir = os.path.dirname( os.path.realpath( __file__ ) )
    return True if "python" in scriptdir else False


def terminate_if_running():
    exists = os.path.exists( "already_running" )
    if exists:
        box = QMessageBox()
        box.setWindowTitle( "Anwendung läuft schon" )
        box.setIcon( QMessageBox.Critical )
        box.setText( "Das ImmoControlCenter läuft bereits.\nEs kann nicht mehrfach ausgeführt werden." )
        box.exec_()
        sys.exit( 1 )

def main():
    app = QApplication()

    setScreenSize( app )
    env = "DEVELOP"
    if not runningInDev():
        # release version running
        terminate_if_running() # one instance only
        # if not downloadDatabase(): ######### NO!! database on server might be older than local database.
        #                                      If use of server database is necessary it must be downloaded manually.
        #     # download not successful. Message not necessary, was provided by method downloadDatabase()
        #     sys.exit( 2 )
        createControlFile()
        env = "RELEASE"
    win = IccMainWindow( env )
    # see: https://stackoverflow.com/questions/53097415/pyside2-connect-close-by-window-x-to-custom-exit-method
    shutDownFilter = ShutDownFilter( win, app )
    win.installEventFilter( shutDownFilter )
    win.show()
    try:
        pos_size = getGeometryOnLastShutdown()
        win.move( pos_size["x"], pos_size["y"] )
        #win.resize( pos_size["w"], pos_size["h"] )
        win.setFixedWidth( 1100 )
        win.setFixedHeight( 63 )
    except:
        win.resize( 1900, 1000 )

    ctrl = MainController( win )
    # ctrl.showStartViews()

    icon = QIcon( "./images/houses.png" )
    app.setWindowIcon( icon )

    app.exec_()
    if not runningInDev():
        if uploadDatabase():
            box = InfoBox( "FTP Upload of Immo-Database successful", "Database was stored to server.", "", "OK" )
            box.exec_()
        else:
            box = InfoBox( "FTP Upload of Immo-Database failed.", "No need to panic.\nApplication will be terminated normally.",
                           "Database has to be uploaded manually, if need be.", "OK" )
            box.exec_()
        deleteControlFile()


def testUploadDatabase():
    if not uploadDatabase():
        print( "FTP failed." )

def testDownloadDatabase():
    app = QApplication()
    if not downloadDatabase():
        sys.exit( 2 )
    app.quit()

def testSaveDatabase():
    app = QApplication()
    saveDatabase()
    app.exec_()


def testSaveDatabasePermission() -> None:
    # from shutil import copyfile
    src = "/home/martin/Projects/python/ImmoControlCenter/immo.db"
    dest = "/media/martin/Elements1/immoTEST.db"
    # dest = "/home/martin/kannweg/immo.db"
    if os.path.isfile( src ):
        try:
            shutil.copy2( src, dest )
        except Exception as ex:
            print( str( ex ) )


if __name__ == '__main__':
    # testSaveDatabasePermission()
    # testSaveDatabase()
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
