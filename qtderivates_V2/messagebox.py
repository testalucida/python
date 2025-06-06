from qt_imports import *

###################  MessageBox  #######################
class MessageBox( QMessageBox ):
    """
    Implementierung eines Ja- / Nein- / Abbrechen Dialogs.
    Das Ergebnis von exec_() kann mit rc == QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel abgefragt werden.
    """
    def __init__( self, title:str, msg:str, more:str, yesText:str, noText:str=None, cancelText:str=None ):
        QMessageBox.__init__( self )
        self.setWindowTitle( title )
        self.setText( msg )
        if more:
            self.setInformativeText( more )
        # Damit die Button-Reihenfolge wie gewünscht erscheint (OK, NEIN, ABBRECHEN), müssen
        # wir die Rollen umbiegen. Sie werden für die Rückgabe des Ergebnisses wieder zurückgebogen.
        self.addButton( yesText, QMessageBox.RejectRole )
        if noText:
            self.addButton( noText, QMessageBox.NoRole )
        if cancelText:
            self.addButton( cancelText, QMessageBox.YesRole )

    def exec_(self) -> int:
        rc = QMessageBox.exec_( self )
        if rc == 0: #Yes-Button
            return QMessageBox.Yes
        if rc == 1: #No-Button
            return QMessageBox.No
        else: #Cancel-Button
            return QMessageBox.Cancel

#########################  InfoBox  ########################
class InfoBox( MessageBox ):
    def __init__( self, title:str, info:str, more:str, yesText ):
        MessageBox.__init__( self, title, info, more, yesText )
        self.setIcon( QuestionBox.Information )

#########################  QuestionBox  ########################
class QuestionBox( MessageBox ):
    def __init__( self, title:str, question:str, yesText, noText, cancelText:str=None ):
        MessageBox.__init__( self, title, question, "", yesText, noText, cancelText )
        self.setIcon( QuestionBox.Question )

#########################  WarningBox  ########################
class WarningBox( MessageBox ):
    def __init__( self, title:str, warning:str, more:str, yesText, noText, cancelText:str=None ):
        MessageBox.__init__( self, title, warning, more, yesText, noText, cancelText )
        self.setIcon( QuestionBox.Warning )

#########################  CriticalMessageBox  ########################
class ErrorBox( MessageBox ):
    def __init__( self, title:str, msg:str, more:str  ):
        MessageBox.__init__( self, title, msg, more, "OK", )
        self.setIcon( QuestionBox.Critical )



#########################################################################
def test5():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    mb = WarningBox( "Warnung", "Das könnte daneben gehen.\n\n>> Ein if-Zweig ist offen!", "Soll er geschlossen werden?", "Schließen", "Offen lassen", "Leck mich" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )

def test4():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    mb = ErrorBox( "Kritisch!!", "Jetzt hast du echt einen Fehler gemacht", "Du hast vergessen, die Datenbank abzuschließen" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )

def test3():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    mb = InfoBox( "Info", "Hier ist die Hölle.", "...und der Satan ist auch schon hier.", "Ja, ich habe es schon befürchtet." )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )


def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    mb = QuestionBox( "Frage", "Gibt es hier Geld?", "Ja, viel!", "Nein, keines" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )
    app.exec_()

def test():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    #mb2 = QMessageBox( )
    mb = MessageBox( "Titel", "Hier ist eine Message", "Mehr Text", "JA", "NEIN", "CANCEL" )
    rc = mb.exec_()
    print( "rc=", rc )
    if rc == QMessageBox.Yes: print( "YES" )
    if rc == QMessageBox.No: print( "NO" )
    if rc == QMessageBox.Cancel: print( "CANCEL" )
    if rc == QMessageBox.Rejected: print( "REJECTED" )
    app.exec_()

if __name__ == "__main__":
    test5()