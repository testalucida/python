from generictable_stuff.xbasetablemodel import XBaseTableModel
from icctableeditor import IccTableEditor
from iccview import IccTableEditorView


class GeplantView( IccTableEditorView ):
    def __init__( self, model:XBaseTableModel=None ):
        IccTableEditorView.__init__( self, model )
        self.save.connect( self.onSave )

    def addJahr( self, jahr: int ) -> None:
        raise NotImplementedError( "GeplantView.addJahr()" )

    def clear( self ):
        raise NotImplementedError( "GeplantView.clear()" )

    def onSave( self ):
        raise NotImplementedError( "GeplantView.onSave")