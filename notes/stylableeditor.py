import tkinter as tk
from tkinter import ttk, FLAT
from tkinter import scrolledtext 
from tkinter.font import Font, ITALIC, BOLD, NORMAL
from enum import Enum
import sys
if not 'mywidgets' in sys.path: sys.path.append('/home/martin/Projects/python/mywidgets')

def testa( event ):
    print( "testa" )

class StyleAction(Enum):
    BOLD = 1,
    ITALIC = 2

class StylableEditor( scrolledtext.ScrolledText ):
    def __init__(self, parent, **kw):
        scrolledtext.ScrolledText.__init__(self, parent, **kw)
        self._myId = None
        self._cbfnc = None
        self.bind('<<TextModified>>', self._onModify)
        #self.bind( '<Control-s>', testa )
        self.isModified:bool = False
        self._boldfont = Font( self, self.cget( "font" ) )
        self._boldfont.configure( weight="bold" )
        self.tag_configure( "bold", font=self._boldfont )

        # https://stackoverflow.com/questions/40617515/python-tkinter-text-modified-callback
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        try:
            result = self.tk.call(cmd)
        except:
            return

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    def setModifyCallback(self, cbfnc) -> None:
        #the given callback function has to take 1 argument:
        #  -  evt: Event
        self._cbfnc = cbfnc

    def _onModify(self, event ):
        #print("_onModify")
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

    def triggerStyleAction( self, styleAction:StyleAction ) -> None:
        """
        Applies or removes the triggered style to the selected text.
        """
        if styleAction == StyleAction.BOLD:
            self._toggleBoldAction()
        #todo

    def _toggleBoldAction( self ):
        """
        Toggle the bold state of the selected text
        """
        # toggle the bold state based on the first character
        # in the selected range. If bold, unbold it. If not
        # bold, bold it.
        try:
            current_tags = self.tag_names( "sel.first" )
            if "bold" in current_tags:
                # first char is bold, so unbold the range
                self.tag_remove( "bold", "sel.first", "sel.last" )
            else:
                # first char is normal, so bold the whole selection
                self.tag_add( "bold", "sel.first", "sel.last" )
                #self.tag_add( "bold", "1.2", "1.5" )
            #TEST
            self.getStyle()
        except:
            return

    def getStylesAsString( self ) -> str:
        tagstring:str = ""
        tagnames = self.tag_names() # get a tuple of tagnames
        for tagname in tagnames:
            if tagname != "sel":
                tagstring += ( tagname + ":" )
                ranges = self.tag_ranges( tagname )
                for i in range( 0, len( ranges ), 2 ):
                    start:str = str( ranges[i] )
                    stop:str = str( ranges[i + 1] )
                    tagstring += (start + "," + stop + ";")
                tagstring = tagstring[:-1] #remove trailing ";"
                tagstring += "$"
        if len( tagstring ) > 0:
            tagstring = tagstring[:-1] #remove trailing "$"
        #print( "tagstring: ", tagstring )
        return tagstring

    def setStylesFromString( self, stylesstr:str ) -> None:
        styles = stylesstr.split( "$" )
        #todo

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