from tkinter import *
from typing import List
from stylableeditor import StylableEditor
from mywidgets import TextEntry

class NoteEditor( Frame ):
    def __init__( self, parent ):
        Frame.__init__( self, parent )
        self.columnconfigure( 1, weight=1 )
        self.rowconfigure( 1, weight=1 )
        padx = pady = 3
        self._teTitle:TextEntry = self._createTitle( self, 0, 0, padx, pady )
        self._edi:StylableEditor = self._createEditor( self, 1, 0, 2, padx, pady )
        self._tags:List[str] = self._createTags( self, 2, 0, padx, pady )

    def _createTitle( self, parent, row, col, padx, pady ) -> TextEntry:
        Label( parent, text="Caption: " ).grid( row=row, column=col, sticky='nw', padx=padx, pady=pady )
        col += 1
        title = TextEntry( parent )
        title.grid( row=row, column=col, sticky='nwe', padx=padx, pady=pady )
        return title

    def _createEditor( self, parent, row, col, colspan, padx, pady ) -> StylableEditor:
        se = StylableEditor( parent )
        se.grid( row=row, column=col, columnspan=colspan, sticky='nswe', padx=padx, pady=pady)
        return se

    def _createTags( self, parent, row, col, padx, pady ):
        Label( parent, text="Tags: " ).grid( row=row, column=col, sticky='nw', padx=padx, pady=pady )
        col += 1
        tags = TextEntry( parent )
        tags.grid( row=row, column=col, sticky='nwe', padx=padx, pady=pady )
        return tags

def testNoteEditor():
    root = Tk()
    root.columnconfigure( 0, weight=1 )
    root.rowconfigure( 0, weight=1 )
    NoteEditor( root ).grid( row=0, column=0, sticky='nswe', padx=3, pady=3)

    root.mainloop()

if __name__ == '__main__':
    testNoteEditor()