from abc import abstractmethod, ABC

from generictable_stuff.xbasetablemodel import XBaseTableModel
from generictable_stuff.customtableview import EditableTableViewWidget
#from iccview import IYearSpecific

class IYearSpecific( ABC ):
    """
    Interface, das die Methode addJahr() definiert
    Wird für die Views benötigt, die jahresspezifische Daten ausweisen.
    (Zahlungen, Abrechnungen, ...)
    """
    @abstractmethod
    def addJahr( self, jahr:int ) -> None:
        pass

class IccTableEditorMeta( type(EditableTableViewWidget), type( IYearSpecific ) ):
    pass

class IccTableEditor( EditableTableViewWidget, IYearSpecific, metaclass=IccTableEditorMeta ):
    def __init__( self, model:XBaseTableModel=None ):
        EditableTableViewWidget.__init__( self, model, isEditable=True )

    @abstractmethod
    def addJahr( self, jahr: int ) -> None:
        raise NotImplementedError( "IccTableEditor.addJahr()" )


