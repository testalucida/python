import tkinter as tk
from typing import Dict
from functools import partial

class PopupMenu:
    def __init__( self, parent ):
        self._parent = parent
        self._popmen : tk.Menu = None
        self._commandDict:Dict = {}
        #self._parent.bind( "<Button-3>", self.show )

    def addCommand( self, label:str, command, insertSeparator:bool=False ):
        self._commandDict[label] = (command, insertSeparator)

    def show( self, event ):
        self._popmen = tk.Menu( master=self._parent, tearoff=1, relief=tk.FLAT )
        for lbl, val_list in self._commandDict.items():
            cmd = val_list[0]
            sep:bool = val_list[1]
            self._popmen.add_command( label=lbl, command=partial( self._triggered, cmd ) )
            if sep:
                self._popmen.add_separator()
        try:
            self._popmen.tk_popup( event.x_root, event.y_root, 0 )
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self._popmen.grab_release()

    def _triggered( self, command ):
        self._popmen.destroy()
        self._popmen = None
        command()


def onCommand():
    print( "onCommand" )

def test3():
    root = tk.Tk()
    root.geometry( '400x400' )
    root.columnconfigure( 0, weight=1 )
    root.columnconfigure( 1, weight=1 )
    root.rowconfigure( 0, weight=1 )
    f1 = tk.Frame( root, background='#000000' )
    f1.grid( row=0, column=0, sticky='nswe' )
    f2 = tk.Frame( root, background='#ffffff' )
    f2.grid( row=0, column=1, sticky='nswe' )

    p = PopupMenu( f2 )
    p.addCommand( "item 1", onCommand, True )
    p.addCommand( "item 2", onCommand )

    root.mainloop()


if __name__ == '__main__':
    test3()