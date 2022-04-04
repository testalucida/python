from PySide2.QtWidgets import QWidget, QLineEdit, QComboBox, QTextEdit


class Clearable:
    def __init__( self ):
        if not isinstance( self, QWidget ):
            raise Exception( "Clearable darf Basisklasse nur für QWidget sein." )

    def clear( self ):
        children = self.findChildren( QWidget, "" )
        for child in children:
            if isinstance( child, QLineEdit ):
                child.clear()
            if isinstance( child, QComboBox ):
                child.setCurrentIndex( -1 )
            if isinstance( child, QTextEdit ):
                child.clear()