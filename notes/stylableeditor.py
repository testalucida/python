import tkinter as tk
from tkinter import ttk, FLAT
from tkinter import scrolledtext 
from tkinter.font import Font, ITALIC, BOLD, NORMAL
import sys
if not 'mywidgets' in sys.path: sys.path.append('/home/martin/Projects/python/mywidgets')


class StylableEditor( scrolledtext.ScrolledText ):
    def __init__(self, parent, **kw):
        scrolledtext.ScrolledText.__init__(self, parent, **kw)
        self._myId = None
        self._cbfnc = None
        self.bind('<<TextModified>>', self._onModify)
        self.isModified:bool = False

        # https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    def setModifyCallback(self, cbfnc) -> None:
        #the given callback function has to take 1 argument:
        #  -  evt: Event
        self._cbfnc = cbfnc

    def _onModify(self, event ):
        print("_onModify")
        self.isModified = True
        if self._cbfnc:
            self._cbfnc( event )

    def getValue(self) -> any:
        """
        #########comment stackoverflow:############
        It is impossible to remove the final newline that is
        automatically added by the text widget.
        – Bryan Oakley Jan 13 '18 at 14:09

        ==> that's why we do it here:
        """
        s = self.get('1.0', 'end')
        return s[:-1]

    def setValue(self, val: str) -> None:
        self.clear()
        if val:
            self.insert('1.0', val)

    def getStyle( self ):
        #todo
        return None

    def resetModified( self ):
        self.isModified = False

    def clear(self) -> None:
        self.delete('1.0', 'end')

    def setFont( self, font ):
        # font example: font = ("Times New Roman", 15)
        pass

    def setSelectionFont( self, font ):
        #font example: font = ("Times New Roman", 15)
        pass

    def setSelectionBold( self, on:bool ) -> None:
        pass

    def setSelectionItalic( self, on:bool ) -> None:
        pass

##################################################################
def test():
    win = tk.Tk()
    win.title("ScrolledText Widget")

    # Title Label
    ttk.Label(win,
              text = "ScrolledText Widget Example",
              font = ("Times New Roman", 15),
              background = 'green',
              foreground = "white").grid(column = 0,
                                         row = 0)

    # Creating scrolled text
    # area widget
    text_area = StylableEditor( win,
                                wrap = tk.WORD,
                                width = 40,
                                height = 10,
                                font = ("Times New Roman",
                                                  15) )

    text_area.grid(column = 0, pady = 10, padx = 10)

    # Placing cursor in the text area
    text_area.focus()
    win.mainloop()

if __name__ == '__main__':
    test()