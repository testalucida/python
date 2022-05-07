import os
import shutil
import sys
from typing import Dict
from PySide2.QtGui import QIcon

import datehelper

sys.path.append( "../common" )

from ftp import FtpIni, Ftp
from messagebox import ErrorBox, QuestionBox, InfoBox, WarningBox
from screen import setScreenSize
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
from icc.iccmainwindow import IccMainWindow
from maincontroller import MainController

class ImmoState:
    def __init__(self):
        self.isInUse = False
        self.lastUpdate = ""

class IccStateHandler:
    """
    IccFileTransfer handles all ftp up- and downloads concerning the ImmoControlCenter application.
    - beauskunftet den Status der immo-Datenbanken
        a) auf dem Server
        b) lokal
        using file immo_state.
        Uploads and downloads immo_state and immo.db.
        Structure of file immo_state:
            state=not_in_use
            last_update=2021-04-22
    - processes up- and donwloads as needed
    """
    attributename_state = "state"
    attributename_lastupdate = "last_update"
    state_in_use = "in_use"
    state_not_in_use = "not_in_use"
    state_last_update_unknown = "unknown"
    immostate_sep = "="
    def __init__( self, ftpini_pathnfile:str ):
        self._ftpini_pathnfile = ftpini_pathnfile
        self.immostate_filename = "immo_state" # remote and local filename
        self.immostate_localfilename_tmp = "immo_state.tmp" # local name after download
        self.immo_dbname = "immo.db" # remote and local filename
        self._ftp:Ftp = None
        self._ftpini:FtpIni = None
        self.currentState:ImmoState = None

    def startApplication( self ):
        """
        Connects to FTP-Server.
        Checks state.
        Downloads database.
        Might throw exception.
        Don't forget calling stopApplication before exiting the application.
        :return:
        """
        if self._ftp: # FTP connection already established
            return
        # get paths and filenames needed to establish a FTP connection:
        self._ftpini = FtpIni( self._ftpini_pathnfile )
        # initialize Ftp class and connect to FTP server
        self._ftp = Ftp( self._ftpini )
        self._ftp.connect()
        # for comparing purposes download serverside immo_state
        try:
            serverstate:ImmoState = self._getServerState()
        except Exception as ex:
            raise Exception( "IccStateHandler.startApplication():\nCan't get serverside state:\n%s" % str(ex) )
        if serverstate.isInUse:
            raise Exception( "IccStateHandler.startApplication():\nCan't start application - Database is in use" )
        try:
            localstate:ImmoState = self._getLocalState()
        except Exception as ex:
            raise Exception( "IccStateHandler.startApplication():\nCan't get local state:\n%s" % str( ex ) )
        # compare serverside and locas last updates and raise exception if local last update is newer than
        # serverside last update
        if serverstate.lastUpdate < localstate.lastUpdate:
            raise Exception( "IccStateHandler.startApplication():\n"
                             "Expected serverside last update to be newer than local last update but found:\n"
                             "serverside = %s -- local = %s" % ( serverstate.lastUpdate, localstate.lastUpdate ) )
        else:
            # Everything is okay. We may download the serverside database now for local use.
            try:
                self._ftp.download( self.immo_dbname, self.immo_dbname )
            except Exception as ex:
                raise Exception( "IccStateHandler.startApplication():\n"
                                 "Download of serverside immo.db failed:\n%s" % str(ex) )
            # Set is-in-use state in local and serverside immo_state files.
            # Attribute last_update remains unchanged.
            localstate.isInUse = True
            try:
                self._setStateAndSave( localstate )
            except Exception as ex:
                raise Exception( "IccStateHandler.startApplication():\n"
                                 "After download of serverside immo.db:\nFailed to set state:\n%s" % str( ex ) )

    def stopApplication( self ):
        """
        Uploads database
        Sets state and last_update attributes in immo_state.
        Uploads immo_state
        Disconnects from FTP-Server
        Might throw exception.
        :return:
        """
        try:
            self._ftp.upload( self.immo_dbname, self.immo_dbname )
        except Exception as ex:
            raise Exception( "IccStateHandler.stopApplication():\n"
                             "Upload immo.db failed:\n%s" % str(ex) )
        state = ImmoState()
        state.isInUse = False
        state.lastUpdate = datehelper.getCurrentTimestampIso()
        try:
            self._setStateAndSave( state )
        except Exception as ex:
            raise Exception( "IccStateHandler.stopApplication():\n"
                             "After upload of local immo.db:\nFailed to set state:\n%s" % str( ex ) )
        self._ftp.quit()
        self._ftp = None

    def _getServerState( self ) -> ImmoState:
        self._ftp.download( self.immostate_filename, self.immostate_localfilename_tmp )
        localpathnfile_tmp = self._ftpini.getLocalPath() + self.immostate_localfilename_tmp
        serverstate:ImmoState = self._readAttributesFromState( localpathnfile_tmp )
        return serverstate

    def _setStateAndSave( self, immoState:ImmoState ) -> None:
        state = self.state_in_use if immoState.isInUse else self.state_not_in_use
        last_update = immoState.lastUpdate
        stateline = self.attributename_state + self.immostate_sep + state
        lastupdateline = self.attributename_lastupdate + self.immostate_sep + last_update
        self._setLocalAndServerStateAndSave( [stateline, "\n", lastupdateline] )

    def _setLocalAndServerStateAndSave( self, lines:list ) -> None:
        """

        :param lines: attribute names and values to write into immo_state
        :return:
        """
        pathnfile = self._ftpini.getLocalPath() + self.immostate_filename
        try:
            with open( pathnfile, "w" ) as statefile:
                for line in lines:
                    statefile.write( line )
        except Exception as ex:
            raise Exception( "IccStateHandler._setLocalAndServerStateAndSave():\n"
                             "Local storage of file immo_state failed.\n%s" % str(ex) )
        try:
            self._ftp.upload( self.immostate_filename, self.immostate_filename )
        except Exception as ex:
            raise Exception("IccStateHandler._setLocalAndServerStateAndSave():\n"
                             "Serverside storage of file immo_state failed.\n%s" % str(ex))

    def _getLocalState( self ) -> ImmoState:
        """
        gets state attributes from local immo_state file
        :return:
        """
        localpathnfile = self._ftpini.getLocalPath() + self.immostate_filename
        localstate:ImmoState = self._readAttributesFromState( localpathnfile )
        return localstate

    def _readAttributesFromState( self, pathnfile:str ) -> ImmoState:
        """
        provides informations "database last update" and "database is in use" from file <pathnfile>
        :param pathnfile: immo_state file server or local side in the prescribed structure (see class comment)
        :return: an ImmoState object containing the attributes found in <pathnfile>
        """
        immostate = ImmoState()
        serverstatefile = open( pathnfile, "r" )
        content = serverstatefile.read()
        serverstatefile.close()
        lines = content.splitlines()
        for line in lines:
            parts = line.split( self.immostate_sep ) # list like so: ['state', 'not_in_use']
            if len( parts ) != 2:
                raise Exception( "IccFileTransfer._readAttributesFromState: Attribute invalid\n"
                                 "Expected <attribute_name>=<attribute_value> -- found: %s" % parts )
            if parts[0] == self.attributename_state:
                immostate.isInUse = True if  parts[1] == self.state_in_use else False
            elif parts[0] == self.attributename_lastupdate:
                immostate.lastUpdate = parts[1]
        return immostate


def testStartStopApplication():
    iccftp = IccStateHandler( "ftp.ini" )
    try:
        iccftp.startApplication()
    except Exception as ex:
        print( str( ex ) )
        return
    try:
        iccftp.stopApplication()
    except Exception as ex:
        print( str(ex) )

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
            box.setText( "Datenbank\n\n   '%s'\n\nsichern in\n\n   '%s'?" % (scriptdir + "/immo.db", dest) )
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
    iccstate = IccStateHandler( "ftp.ini")
    setScreenSize( app )
    env = "DEVELOP"
    if not runningInDev():
        # release version running
        terminate_if_running() # one instance only
        try:
            iccstate.startApplication() # download immo.db from server and set is-in-use flag
        except Exception as ex:
            print( str(ex) )
            box = ErrorBox( "ImmoControlCenter", "Failed starting application", str( ex ) )
            box.exec_()
            return
        createControlFile() # flag file showing application is running
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

    MainController( win )

    icon = QIcon( "./images/houses.png" )
    app.setWindowIcon( icon )

    app.exec_()

    if not runningInDev():
        try:
            iccstate.stopApplication() # upload immo.db to server and set not-in-use flag
        except Exception as ex:
            print( str(ex) )
            box = ErrorBox( "ImmoControlCenter", "Failed starting application", str( ex ) )
            box.exec_()
        finally:
            deleteControlFile()


def testUploadDatabase():
    if not uploadDatabase():
        print( "FTP failed." )

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
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
