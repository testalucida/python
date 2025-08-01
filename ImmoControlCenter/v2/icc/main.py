import os
import sys

from PySide6 import QtCore
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QDialog

sys.path.append( "../../../common" )
sys.path.append( "../../" )
sys.path.append( "../" )
#sys.path.append( "/home/martin/Projects/python/ImmoControlCenter/v2" )
print( "sys.path: ", sys.path )
#from v2.icc.definitions import ROOT_DIR
from v2.icc.mainlogic import MainLogic
from base.messagebox import WarningBox, ErrorBox
from v2.einaus.einauswritedispatcher import EinAusWriteDispatcher
from v2.icc.login import login
from v2.icc.maincontroller import MainController


class ShutDownFilter( QtCore.QObject ):
    def __init__( self, win: QWidget, mainCtrl:MainController, app: QApplication ):
        QtCore.QObject.__init__( self )
        self._win = win
        self._mainCtrl = mainCtrl
        self._app = app

    def eventFilter( self, obj, event ) -> bool:
        if obj is self._win and event.type() == QtCore.QEvent.Type.Close:
            #if self._win.canShutdown():
            if not self.quit_app():
                return False
            event.ignore()
            return True
        return super( ShutDownFilter, self ).eventFilter( obj, event )

    def quit_app( self ) -> bool:
        # if not self._mainCtrl.exportDatabaseOnClose():
        if not self._mainCtrl.exportDatabaseOnCloseWorker(): # Export der Db zum Server hat nicht geklappt
            return False # Anwendung offen lassen - vllt passiert ein Wunder
        geom = self._win.geometry()
        #print( 'CLEAN EXIT. x=%d - y=%d - w=%d - h=%d' % (geom.x(), geom.y(), geom.width(), geom.height()) )
        #writeGeometryOnShutdown( geom.x(), geom.y(), geom.width(), geom.height() )
        self._win.removeEventFilter( self )
        self._app.quit()
        return True

# def saveDatabase() -> None:
#     def try_copyfile():
#         try:
#             copyfile( src, dest )
#         except Exception as ex:
#             box = WarningBox( "Datenbank auf lokalen Datenträger sichern", "Sicherung nicht möglich:\n\n" + str(ex),
#                               "Ist der Datenträger eingehängt?", "Nochmal versuchen", "Beenden" )
#             rc = box.exec_()
#             if rc == QMessageBox.Yes:
#                 try_copyfile()
#     from shutil import copyfile
#     if runningInDev(): return
#     scriptdir = os.path.dirname( os.path.realpath( __file__ ) )
#     src = ROOT_DIR + "/immo.db"
#     if "Vermietung" in scriptdir:
#         print( "Running in REL; try to copy immo.db" )
#         dest = "/media/martin/Elements1/Vermietung_V2/ImmoControlCenter/v2/icc/immo.db"
#         if os.path.isfile( src ):
#             box = QMessageBox()
#             box.setIcon( QMessageBox.Question )
#             box.setWindowTitle( "Sicherung der Datenbank" )
#             box.setText( "Datenbank\n\n   '%s'\n\nsichern in\n\n   '%s'?" % (scriptdir + "/immo.db", dest) )
#             box.setStandardButtons( QMessageBox.Save | QMessageBox.Cancel )
#             r = box.exec_()
#             if r == QMessageBox.Save:
#                 try_copyfile()
#         else:
#             box = ErrorBox( "Datenbank auf lokalen Datenträger sichern", "Sicherung nicht möglich",
#                             "Es gibt keine Datenbank namens immo.db" )
#             box.exec_()


# def createControlFile():
#     try:
#         f = open( "already_running", "x" )
#     except:
#         box = QMessageBox()
#         box.setWindowTitle( "Anwendung kann nicht gestartet werden" )
#         box.setIcon( QMessageBox.Critical )
#         box.setText( "Das ImmoControlCenter kann nicht gestartet werden:\n"
#                      "Die Kontrolldatei kann nicht angelegt werden." )
#         box.exec_()
#         sys.exit( 1 )

# def deleteControlFile():
#     os.remove( "already_running" )

def runningInDev() -> bool:
    scriptdir = os.path.dirname( os.path.realpath( __file__ ) )
    return True if "python" in scriptdir else False

# def terminate_if_running():
#     exists = os.path.exists( "already_running" )
#     if exists:
#         box = QMessageBox()
#         box.setWindowTitle( "Anwendung läuft schon" )
#         box.setIcon( QMessageBox.Critical )
#         box.setText( "Das ImmoControlCenter läuft bereits.\nEs kann nicht mehrfach ausgeführt werden." )
#         box.exec_()
#         sys.exit( 1 )

# def quit_app( self ):
#     saveDatabase()
#     #geom = self._win.geometry()
#     #print( 'CLEAN EXIT. x=%d - y=%d - w=%d - h=%d' % (geom.x(), geom.y(), geom.width(), geom.height()) )
#     #writeGeometryOnShutdown( geom.x(), geom.y(), geom.width(), geom.height() )
#     self._win.removeEventFilter( self )
#     self._app.quit()

def main():
    #os.chdir("~")
    app = QApplication()
    env = "DEVELOP"
    if not runningInDev():
        if not login(): exit( 4 )
        # release version running
        #terminate_if_running()  # one instance only
        #createControlFile()  # flag file showing application is running
        env = "RELEASE"

    # Die one-and-only-Instanz des EinAusWriteDispatchers erzeugen:
    EinAusWriteDispatcher()
    mainCtrl = MainController( env )
    mainwin = mainCtrl.createGui()
    # shutDownFilter = ShutDownFilter( mainwin, mainCtrl, app )
    # mainwin.installEventFilter( shutDownFilter )
    mainwin.show()
    # w = mainwin.getPreferredWidth()
    # h = mainwin.getPreferredHeight()
    mainwin.resize( QSize( 1400, 800 ) )
    icon = QIcon( "./images/houses.png" )
    app.setWindowIcon( icon )
    app.exec()

    # # Die Datenbank vom Server holen:
    # try:
    #     try:
    #         MainLogic.importDatabaseFromServer()
    #     except FileNotFoundError as err:
    #         if MainLogic.checkDatabaseExistsLocal(): # die DB existiert lokal. Vermutlich ist die Anwendung beim
    #                                                 # letzten Mal abgestürzt und konnte die DB nicht mehr zum
    #                                                 # Server übertragen.
    #             box = WarningBox( "Datenbank nicht auf dem Server", "Datenbank existiert nicht "
    #                                                                 "auf dem Server,\naber im lokalen"
    #                                                                 "Verzeichnis.",
    #                               "Soll die lokale Datenbank verwendet werden?\n\n"
    #                               "ACHTUNG: Läuft das ImmoControlCenter vielleicht auf einem anderen Rechner?\n"
    #                               "Dann sollte die Anwendung beendet werden!",
    #                               yesText="Ja, lokale DB verwenden", noText="Nein, lieber Anwendung beenden",
    #                               cancelText=None )
    #             if box.exec_() != QMessageBox.Yes:
    #                 return # Anwendung wird beendet
    #         else: # auch lokal keine Datenbank vorhanden
    #             box = ErrorBox( "Keine Datenbank", "Datenbank weder auf dem Server noch lokal gefunden.",
    #                             "Anwendung wird beendet." )
    #             box.exec_()
    #             return
    #     # Die one-and-only-Instanz des EinAusWriteDispatchers erzeugen:
    #     EinAusWriteDispatcher()
    #     mainCtrl = MainController( env )
    #     mainwin = mainCtrl.createGui()
    #     shutDownFilter = ShutDownFilter( mainwin, mainCtrl, app )
    #     mainwin.installEventFilter( shutDownFilter )
    #     mainwin.show()
    #     # w = mainwin.getPreferredWidth()
    #     # h = mainwin.getPreferredHeight()
    #     mainwin.resize( QSize(1400, 800) )
    #
    #     icon = QIcon( "./images/houses.png" )
    #     app.setWindowIcon( icon )
    #
    #     app.exec()
    # except Exception as ex:
    #     box = ErrorBox( "Fehler beim Download der Datenbank", str( ex ), "Anwendung wird geschlossen." )
    #     box.exec_()

    # if not runningInDev():
    #     deleteControlFile()


if __name__ == "__main__":
    main()