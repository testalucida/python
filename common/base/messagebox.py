from platform import system

###################  MessageBox  #######################
from PySide6 import QtCore
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QMessageBox, QWidget, QApplication


class MessageBox_( QMessageBox ):
    """
    Implementierung eines Ja- / Nein- / Abbrechen Dialogs.
    Das Ergebnis von exec_() kann mit rc == QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel abgefragt werden.
    """
    class ShutDownFilter( QtCore.QObject ):
        def __init__( self, win: QWidget ):
            QtCore.QObject.__init__( self )
            self._win = win

        def eventFilter( self, obj, event ) -> bool:
            if obj is self._win and event.type() == QtCore.QEvent.Type.Close:
                return False
            return super( MessageBox_.ShutDownFilter, self ).eventFilter( obj, event )

    def __init__( self, title:str, msg:str, more:str, yesText:str, noText:str=None, cancelText:str=None ):
        QMessageBox.__init__( self )
        self._rc = None
        self.setWindowTitle( title )
        self._shutDownFilter = MessageBox_.ShutDownFilter( self )
        self.installEventFilter( self._shutDownFilter )
        self.setText( msg )
        if more:
            self.setInformativeText( more )
        # Damit die Button-Reihenfolge wie gewünscht erscheint (OK, NEIN, ABBRECHEN), müssen
        # wir die Rollen umbiegen. Sie werden für die Rückgabe des Ergebnisses wieder zurückgebogen.
        # self.addButton( yesText, QMessageBox.RejectRole )
        # if noText:
        #     self.addButton( noText, QMessageBox.NoRole )
        # if cancelText:
        #     self.addButton( cancelText, QMessageBox.YesRole )

    def moveToCursor( self ):
        crsr = QCursor.pos()
        self.move( crsr.x(), crsr.y() )

    def exec_(self) -> int:
        self._rc = QMessageBox.exec_( self )
        rc = self._rc
        print( "rc: ", rc )
        print( "OK" if rc == QMessageBox.Ok else "NOT OK" )
        print( "YES" if rc == QMessageBox.Yes else "NOT YES" )
        print( "NO" if rc == QMessageBox.No else "NOT NO" )
        print( "CANCEL" if rc == QMessageBox.Cancel else "NOT CANCEL" )
        # print( "Yes: ", int(QMessageBox.Yes) )
        # print( rc == QMessageBox.Yes )
        # if rc == 0: #Yes-Button
        #     return QMessageBox.Yes
        # if rc == 1: #No-Button
        #     return QMessageBox.No
        # else: #Cancel-Button
        #     return QMessageBox.Cancel
###############################################################
###############################################################
# PySide6 kennt diese Konstanten nicht mehr. Ich verstehe auch nicht, welcher Logik die Rückgaben
# von QMessageBox folgen. Deshalb dieser grauenhafte Hack:
QMessageBox.Yes = 2
QMessageBox.No = 3
QMessageBox.Cancel = 4
class MessageBox( QMessageBox ):
    """
    Implementierung eines Ja- / Nein- / Abbrechen Dialogs.
    Das Ergebnis von exec_() kann mit rc == QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel abgefragt werden.
    """
    class ShutDownFilter( QtCore.QObject ):
        def __init__( self, win: QWidget ):
            QtCore.QObject.__init__( self )
            self._win = win

        def eventFilter( self, obj, event ) -> bool:
            if obj is self._win and event.type() ==  QtCore.QEvent.Type.Close:
                self._win.X_clicked = True
                return True
            return super( MessageBox.ShutDownFilter, self ).eventFilter( obj, event )

    def __init__( self, title:str, msg:str, more:str, yesText:str, noText:str=None, cancelText:str=None ):
        QMessageBox.__init__( self )
        self.X_clicked = False # True: User hat auf Schließebox geklickt
        self.setWindowTitle( title )
        self._shutDownFilter = MessageBox.ShutDownFilter( self )
        self.installEventFilter( self._shutDownFilter )
        self.setText( msg )
        if more:
            self.setInformativeText( more )
        # Damit die Button-Reihenfolge wie gewünscht erscheint (OK, NEIN, ABBRECHEN), müssen
        # wir die Rollen umbiegen. Sie werden für die Rückgabe des Ergebnisses wieder zurückgebogen.
        # ==> Nein, mit Umstieg auf PySide6 nicht mehr. Keine Ahnung, warum die ganze Scheiße funktioniert.
        self.addButton( yesText, QMessageBox.ButtonRole.RejectRole )
        if noText:
            self.addButton(noText, QMessageBox.ButtonRole.NoRole)
        if cancelText:
            self.addButton(cancelText, QMessageBox.ButtonRole.YesRole)

    def moveToCursor( self ):
        crsr = QCursor.pos()
        self.move( crsr.x(), crsr.y() )

    def exec_(self) -> int:
        rc = QMessageBox.exec( self )
        print( "rc: ", rc )
        if self.X_clicked: # geschlossen über Schließebox
            return -1
        if rc == QMessageBox.Yes:
            return QMessageBox.Yes
        if rc == QMessageBox.No:
            return QMessageBox.No
        if rc == QMessageBox.Cancel:
            return QMessageBox.Cancel
        else:
            box = ErrorBox( "MessageBox.exec() liefert unbekannten Returncode ('%d').\nAnwendung wird beendet." % rc )
            box.exec_()
            import sys
            sys.exit()

    def exec( self ):
        return self.exec_()

########################################################################
class MessageBoxT( QMessageBox ):
    """
    Implementierung eines Ja- / Nein- / Abbrechen Dialogs.
    Das Ergebnis von exec_() kann mit rc == QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel abgefragt werden.
    """
    class ShutDownFilter( QtCore.QObject ):
        def __init__( self, win: QWidget ):
            QtCore.QObject.__init__( self )
            self._win = win

        def eventFilter( self, obj, event ) -> bool:
            if obj is self._win and event.type() ==  QtCore.QEvent.Type.Close:
                self._win.X_clicked = True
                return True
            return super( MessageBox.ShutDownFilter, self ).eventFilter( obj, event )

    def __init__( self, title:str, msg:str, more:str, yesText:str, noText:str=None, cancelText:str=None ):
        QMessageBox.__init__( self )
        self.X_clicked = False # True: User hat auf Schließebox geklickt
        self.setWindowTitle( title )
        self._shutDownFilter = MessageBox.ShutDownFilter( self )
        self.installEventFilter( self._shutDownFilter )
        self.setText( msg )
        if more:
            self.setInformativeText( more )
        if cancelText:
            self.addButton(cancelText, QMessageBox.ButtonRole.RejectRole)
        if noText:
            self.addButton(noText, QMessageBox.ButtonRole.NoRole)
        self.addButton( yesText, QMessageBox.ButtonRole.YesRole )


    def moveToCursor( self ):
        crsr = QCursor.pos()
        self.move( crsr.x(), crsr.y() )

    def exec_(self):
        rc = QMessageBox.exec( self )
        print( "rc: ", rc )
        if self.X_clicked: # geschlossen über Schließebox
            return -1
        return rc


#########################  InfoBox  ########################
class InfoBox( MessageBox ):
    def __init__( self, title:str, info:str, more:str="", yesText="OK" ):
        MessageBox.__init__( self, title, info, more, yesText )
        self.setIcon( QuestionBox.Information )

# #########################  InfoBox2  ########################
# class InfoBox2( MessageBox ):
#     def __init__( self, title:str, info:str ):
#         MessageBox.__init__( self, title, info, "", "OK" )
#         self.setIcon( QuestionBox.Information )

#########################  QuestionBox  ########################
class QuestionBox( MessageBox ):
    def __init__( self, title:str, question:str, yesText, noText, cancelText:str=None ):
        MessageBox.__init__( self, title, question, "", yesText, noText, cancelText )
        self.setIcon( QuestionBox.Question )

#########################  WarningBox  ########################
class WarningBox( MessageBox ):
    def __init__( self, title:str, warning:str, more:str, yesText, noText, cancelText:str=None ):
        MessageBox.__init__( self, title, warning, more, yesText, noText, cancelText )
        #self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        self.setIcon( QuestionBox.Warning )

#########################  CriticalMessageBox  ########################
class ErrorBox( MessageBox ):
    def __init__( self, title:str, msg:str, more:str=""  ):
        MessageBox.__init__( self, title, msg, more, "OK", )
        self.setIcon( QuestionBox.Critical )



#########################################################################
def test5():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    mb = WarningBox( "Warnung", "Das könnte daneben gehen.\n\n>> Ein if-Zweig ist offen!", "Soll er geschlossen werden?", "Schließen", "Offen lassen", "Leck mich" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )

def test4():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    mb = ErrorBox( "Kritisch!!", "Jetzt hast du echt einen Fehler gemacht", "Du hast vergessen, die Datenbank abzuschließen" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )

def test3():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    mb = InfoBox( "Info", "Hier ist die Hölle.", "...und der Satan ist auch schon hier.", "Ja, ich habe es schon befürchtet." )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )


def test2():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    mb = QuestionBox( "Frage", "Gibt es hier Geld?", "Ja, viel!", "Nein, keines" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )
    app.exec_()

def test():
    from PySide6.QtWidgets import QApplication
    app = QApplication()
    #mb2 = QMessageBox( )
    mb = MessageBox( "Titel", "Hier ist eine Message", "Mehr Text", "JA", "NEIN", "CANCEL" )
    rc = mb.exec_()
    #print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )

    # if rc == QMessageBox.Yes: print( "YES" )
    # if rc == QMessageBox.No: print( "NO" )
    # if rc == QMessageBox.Cancel: print( "CANCEL" )
    # if rc == QMessageBox.Rejected: print( "REJECTED" )

if __name__ == "__main__":
    test()