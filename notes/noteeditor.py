from tkinter import *
from typing import List
from stylableeditor import StylableEditor, StyleAction
from mywidgets import TextEntry, ToolTip
from note import Note

class NoteEditor( Frame ):
    def __init__( self, parent ):
        Frame.__init__( self, parent )
        self.columnconfigure( 1, weight=1 )
        self.rowconfigure( 1, weight=1 )
        padx = pady = 3
        self._teTitle:TextEntry = self._createTitle( self, 0, 0, padx, pady )
        self._teTitle.registerModifyCallback( self.onTitleOrTagsChanged )
        self._edi:StylableEditor = self._createEditor( self, 1, 0, 2, padx, pady )
        self._teTags:TextEntry = self._createTags( self, 2, 0, padx, pady )
        self._teTags.registerModifyCallback( self.onTitleOrTagsChanged )
        self._note:Note = Note()
        self._isTitleOrTagChanged:bool = False
        self._ctrl_s_callback = None

    def _createTitle( self, parent, row, col, padx, pady ) -> TextEntry:
        Label( parent, text="Caption: " ).grid( row=row, column=col, sticky='nw', padx=padx, pady=pady )
        col += 1
        title = TextEntry( parent )
        title.grid( row=row, column=col, sticky='nwe', padx=padx, pady=pady )
        title.bind( '<Control-s>', self._onCtrlS )
        ToolTip( title, "This caption will be used to display this note in the tree")
        return title

    def _createEditor( self, parent, row, col, colspan, padx, pady ) -> StylableEditor:
        se = StylableEditor( parent )
        se.grid( row=row, column=col, columnspan=colspan, sticky='nswe', padx=padx, pady=pady)
        se.bind( '<Control-s>', self._onCtrlS )
        return se

    def setCtrlSCallback( self, cb ):
        # the given callback function mustn't have any arguments.
        self._ctrl_s_callback = cb

    def onTitleOrTagsChanged( self, *args ) -> None:
        self._isTitleOrTagChanged = True

    def _createTags( self, parent, row, col, padx, pady ):
        Label( parent, text="Tags: " ).grid( row=row, column=col, sticky='nw', padx=padx, pady=pady )
        col += 1
        tags = TextEntry( parent )
        tags.grid( row=row, column=col, sticky='nwe', padx=padx, pady=pady )
        tags.bind( '<Control-s>', self._onCtrlS )
        ToolTip( tags, "Enter as many comma-separated tags as you want" )
        return tags

    def _onCtrlS( self, event ):
        if self._ctrl_s_callback:
            self._ctrl_s_callback()

    def setNote( self, note:Note ) -> None:
        self._note = note
        self._teTitle.setValue( note.header )
        self._edi.setValue( note.text )
        self._teTags.setValue( note.tags )
        self._applyStyle( note.style )
        self.resetModified()

    def triggerStyleAction( self, styleAction:StyleAction ):
        self._edi.triggerStyleAction( styleAction )

    def _applyStyle( self, style:str ) -> None:
        # applies style only after having set a note.
        # don't use this method as style button callback
        self._edi.setStylesFromString( style )

    def getNote( self ) -> Note:
        self._note.header = self._teTitle.getValue()
        self._note.text = self._edi.getValue()
        self._note.tags = self._teTags.getValue()
        self._note.style = self._edi.getStylesAsString()
        return self._note

    def clear( self ) -> None:
        self._note = Note()
        self.setNote( self._note )

    def isModified( self ) -> bool:
        return ( self._edi.isModified or self._isTitleOrTagChanged )

    def resetModified( self ) -> None:
        self._isTitleOrTagChanged = False
        self._edi.resetModified()

def testNoteEditor():
    root = Tk()
    root.columnconfigure( 0, weight=1 )
    root.rowconfigure( 0, weight=1 )
    NoteEditor( root ).grid( row=0, column=0, sticky='nswe', padx=3, pady=3)

    root.mainloop()

if __name__ == '__main__':
    testNoteEditor()