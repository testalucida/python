from typing import Any, List, Dict

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication, QVBoxLayout

from qtderivates import LineEdit

###################  AnlageV_Zeile_Data  #####################
# class XAnlageV_Zeile_Data:
#     def __init__( self, nr:int=0, feldname:str=None, value:Any=None,bemerkung:str=None ):
#         self.nr:int = nr
#         self.feldname = feldname
#         self.value = value
#         self.bemerkung = value
#         self.printX = 0 # when printing: x-position of value in mm
#         self.printY = 0 # when printing: y-position of value in mm
#         self.printFontsize = 6

#################### NumberLabel ##############################
class NumberLabel( QLabel ):
    def __init__( self, parent=None ):
        QLabel.__init__( self, parent )
        self.setStyleSheet("QLabel { background-color : gray; color : white; }");
        align = self.alignment()
        self.setAlignment( align | Qt.AlignRight )
        font = QFont( "Arial", 14, weight=QFont.Bold )
        self.setFont( font )
        h = self.height()
        self.setFixedSize( 20, h )

################### AnlageV_Zeile ############################
# class AnlageV_ZeileView( QWidget ):
#     def __init__( self, data:XAnlageV_Zeile_Data, parent=None ):
#         QWidget.__init__( self, parent )
#         self._data:XAnlageV_Zeile_Data = data
#         self._layout = QHBoxLayout()
#         self._lblNr = NumberLabel( self )
#         self._lblFeldname = QLabel( self )
#         self._editValue = LineEdit( self )
#         self._lblBemerkung = QLabel( self )
#         self._createGui()
#
#     def _createGui( self ):
#         data = self._data
#
#         if data.nr != 0: self._lblNr.setText( str( data.nr ) )
#         self._layout.addWidget( self._lblNr )
#
#         if data.feldname: self._lblFeldname.setText( data.feldname )
#         self._layout.addWidget( self._lblFeldname )
#
#         if data.value: self._editValue.setValue( data.value )
#         self._layout.addWidget( self._editValue )
#
#         if data.bemerkung: self._lblBemerkung.setText( data.bemerkung )
#         self._layout.addWidget( self._lblBemerkung )
#
#         self.setLayout( self._layout )

################## AnlageV ###################################
# class AnlageV( QWidget ):
#     def __init__( self, parent=None ):
#         QWidget.__init__( self, parent )
#         self._zeilen:List[Dict[Any, AnlageV_ZeileView]] = list()
#         self._layout = QVBoxLayout()
#
#     def addZeile( self, id:Any, data:XAnlageV_Zeile_Data ) -> None:
#         zeile = AnlageV_ZeileView( data )
#         d = { id, zeile }
#         self._zeilen.append( d )
#         self._layout.addWidget( zeile )


######################## TEST #######################################
def test():
    app = QApplication()
    # data = XAnlageV_Zeile_Data( 1, "Name", "Kendel", "Name des Steuerpflichtigen" )
    # z = AnlageV_ZeileView( data )
    # z.show()
    app.exec_()

if __name__ == "__main__":
    test()