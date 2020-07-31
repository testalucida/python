import tkinter as tk
from tkinter import ttk, FLAT, Text
from tkinter import scrolledtext 
from tkinter.font import Font, ITALIC, BOLD, NORMAL
from enum import Enum
from typing import List, Tuple, Dict, Sequence
import sys
if not 'mywidgets' in sys.path: sys.path.append('/home/martin/Projects/python/mywidgets')

def testa( event ):
    print( "testa" )

BOLD_ITALIC = "bold_italic"

###########################################

class StyleAction(Enum):
    BOLD = 1,
    ITALIC = 2,
    RED_FOREGROUND = 3,
    BLUE_FOREGROUND = 4,
    GREEN_FOREGROUND = 5

###########################################

class Range:
    def __init__( self, start:str="", stop:str="" ):
        self.start: str = start  # index like "1.2"
        self.stop: str = stop  # index like "1.8"

class Tag:
    def __init__( self, name="", start="", stop="" ):
        self.name:str = name
        self.range:Range = Range( start, stop )


class StyleRanges:
    def __init__( self, text:Text ):
        self._text:Text = text
        self._styles = {BOLD:[], ITALIC:[], BOLD_ITALIC:[]}
        self._indexes:Dict[str, List[str]] = dict() # key = index, value = list of applied styles (fontstyles and fontcolors)

    def _add( self, style:str, startstop:Tuple ) -> None:
        """
        adds a style range.
        style must be one of BOLD, ITALIC, BOLD_ITALIC
        start and stop must be passed like "1.2"
        """
        #self._styles[style].append( (startstop[0], startstop[1]) )
        rng:Range = Range( startstop[0], startstop[1] )
        self._styles[style].append( rng )

    def _addStyleAtIndex( self, idx:str, tagname:str ) -> None:
        self._indexes[idx].append( tagname )

    def getRanges( self, style:str ) -> List[Range]:
        """
        returns all ranges of style add()ed previously
        """
        return self._styles[style]

    def getRangesWithin( self, style:str, start:str, stop:str ) -> List[Range]:
        """
        returns the ranges of the given style - if any - within the given sequence determined by start and stop
        """
        self._collectFontStylesInRange( (style,), start, stop )
        return self._styles[style]

    def getFontStyleAt( self, idx:str ) -> str:
        """
        Returns the fontstyle (one of BOLD, ITALIC, BOLD_ITALIC) applied to index idx
        Pls note that only one style at a time can be applied to a given index
        """
        tag_names = self._text.tag_names( idx )
        tag_names = [x for x in tag_names if x in (BOLD, ITALIC, BOLD_ITALIC)]
        return "" if len( tag_names ) == 0 else tag_names[0]

    def getFontStyleAndRange( self, start:str, stop:str ) -> Tag:
        """
        Returns a tag object referring to the style found at index start. That style's end will be
        detected and provided to the returned tag object.
        If no style is applied at all, the returned tag object's name will be an empty string.
        It's irrelevant if that style starts before start, start will be returned as start index.
        Even if style ends after stop, stop will be provided as end point of the returned tag's range.
        Pls note that 0 or 1 fontstyle may be applied to a given index (BOLD, ITALIC or BOLD_ITALIC), not more.
        """
        style = self.getFontStyleAt( start )  # BOLD, ITALIC, BOLD_ITALIC or ""
        tag = Tag( style )
        tag.range.start = start
        if style == "":
            # no style applied.
            # Check for the start of the first applied style which marks the end of
            # the range no style is applied to.
            tag.range.stop = stop
            for style in ( BOLD, ITALIC, BOLD_ITALIC ):
                seq = self._text.tag_nextrange( style, start, stop )
                if len( seq ) > 1 and seq[0] < tag.range.stop:
                    tag.range.stop = seq[0]
        else:
            seq = self._text.tag_nextrange( style, start, stop )
            print( "style: ", style, "seq: ", seq )
            tag.range.stop = seq[1]
        return tag


    def getFontStyles( self, start:str, stop:str ) -> Dict[str, List[Range]]:
        """
        returns a dictionary whose key is a style name and whose value is a list containing all ranges
        the style is applied to.
        """
        self._collectFontStylesInRange( (BOLD, ITALIC, BOLD_ITALIC), start, stop )
        return self._styles

    def _collectFontStylesInRange( self, styleList:tuple, start:str, stop:str ) :
        """
        collects the given font styles within the given range for further processing
        styleList may contain one or more of (BOLD, ITALIC, BOLD_ITALIC)
        """
        txt = self._text
        for tagname in styleList:
            seq = txt.tag_nextrange( tagname, start, stop )
            while len( seq ) > 1:
                self._add( tagname, seq )
                idx = txt.index( seq[0] ) # begin of sequence
                eos = seq[1] # end of sequence
                while idx < eos:
                    self._addStyleAtIndex( idx, tagname )
                    idx = txt.index( idx + "+1c" )
                start = eos
                seq = txt.tag_nextrange( tagname, start, stop )



###############################################

class StylableEditor( scrolledtext.ScrolledText ):
    def __init__(self, parent, **kw):
        scrolledtext.ScrolledText.__init__(self, parent, **kw)
        self._myId = None
        self._cbfnc = None
        self.bind('<<TextModified>>', self._onModify)
        #self.bind( '<Control-s>', testa )
        self.isModified:bool = False
        # define some fonts
        self._boldfont = Font( self, self.cget( "font" ) )
        self._boldfont.configure( weight="bold" )
        self._italicfont = Font( self, self.cget( "font" ) )
        self._italicfont.configure( slant="italic" )
        self._bolditalicfont = Font( self, self.cget( "font" ) )
        self._bolditalicfont.configure( weight="bold", slant="italic" )
        # configure tags
        self.tag_configure( "bold", font=self._boldfont )
        self.tag_configure( "italic", font=self._italicfont )
        self.tag_configure( "bold_italic", font=self._bolditalicfont )
        self.tag_configure( "RED", foreground='red' )
        self.tag_configure( "GREEN", foreground='green' )
        self.tag_configure( "BLUE", foreground='blue' )
        self._styleRanges:StyleRanges = StyleRanges( self )

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
            self._handleFontStyle( "bold" )
        elif styleAction == StyleAction.ITALIC:
            self._handleFontStyle( "italic" )
        elif styleAction == StyleAction.RED_FOREGROUND:
            pass
        elif styleAction == StyleAction.BLUE_FOREGROUND:
            pass
        elif styleAction == StyleAction.GREEN_FOREGROUND:
            pass

    def _handleFontStyle( self, style:str ) -> None:
        """
        # style may be "bold" or "italic".
        # Basically the style action to take is determined by the first character
        # in the selected range. If style is set, unset it. If not set, set it.
        # It's more complicated if e.g. "bold" is to be set and "italic" is already set:
        #    - compare the ranges of the two styles and take proper action, eg:

                |      italic    |   -> set
                4                15
                        |      bold      |  -> to set according to selection
                        8               20
                ==> from 8 to 15: make italic and bold (tag "bold_italic")
                ==> from 16 to 20: make bold (tag "bold")
        """
        if style in (BOLD, ITALIC, BOLD_ITALIC):
            self._toggleFontStyle( style, self.index( "sel.first" ), self.index( "sel.last" ) )

        #
        return
        try:
            current_tags = self.tag_names( "sel.first" )
            if style in current_tags:
                # first char is bold, so unbold the range
                self.tag_remove( style, "sel.first", "sel.last" )
            else:
                # first char is normal, so bold the whole selection
                self.tag_add( style, "sel.first", "sel.last" )
            #TEST
            #self.getStylesAsString()
        except:
            return

    def _toggleFontStyle( self, style:str, start:str, stop:str ) -> None:
        if self.isSet( style, start ):
            self._unsetFontStyle( style, start, stop )
        else:
            self._setFontStyle( style, start, stop )

    def isSet( self, style:str, idx:str ) -> bool:
        seq = self.tag_nextrange( style, idx, idx )
        # Note: even if style is not set, a tuple of len == 1 will be given.
        # The one and only element of that tuple is the string "None".
        # That contradicts to the tag_nextrange documentation, which pretends to return an empty string.
        return True if len( seq ) > 1 else False

    def _unsetFontStyle( self, style:str, start:str, stop:str ):
        """
        removes the given style within the given range defined by start and stop.
        Takes style "bold_italic" into account: if bold_italic is set and bold is to be removed,
        italic will remain. If italic is to be removed, bold will remain.
        """
        self.tag_remove( style, start, stop )
        if style in (BOLD, ITALIC):
            rangelist:List[Range] = self._styleRanges.getRangesWithin( BOLD_ITALIC, start, stop )
            if len( rangelist ) > 0:
                styleToSet:str = ITALIC if style == BOLD else BOLD
                """
                |                     |    --> in this sequence style BOLD or ITALIC was removed
                start                 stop
                
                  |     |    |  |          --> in this sequences BOLD_ITALIC was set. We have to set styleToSet here
                  r1    r1   r2 r2
                """
                for rng in rangelist:
                    self.tag_add( styleToSet, rng.start, rng.stop )

    def _setFontStyle( self, style: str, start: str, stop: str ):
        """
        applies the given style to the given range.
        If bold is already set and italic is to add remove bold and set BOLD_ITALIC.
        If italic is already set and bold is to add remove bold and set BOLD_ITALIC.

        |                                | -> Range to set style
        start                            stop

            |   |         |  |             -> ranges where another style is already set. Replace that style by BOLD_ITALIC
        """
        while self.index( start ) < self.index( stop ):
            tag = self._styleRanges.getFontStyleAndRange( start, stop )
            if tag.name == "":
                # no style applied at start. Apply style.
                self.tag_add( style, tag.range.start, tag.range.stop )
            else:
                # BOLD, ITALIC or BOLD_ITALIC set
                if tag.name in ( BOLD, ITALIC ):
                    if tag.name != style:
                        # if BOLD or ITALIC, remove it and set BOLD_ITALIC
                        self.tag_remove( tag.name, tag.range.start, tag.range.stop )
                        print( "_setFontStyle: adding bold_italic from %s to %s" % (tag.range.start, tag.range.stop) )
                        self.tag_add( BOLD_ITALIC, tag.range.start, tag.range.stop )
                # BOLD_ITALIC can be ignored.
            start = tag.range.stop

    def testIterate( self, start, stop ):
        idx = start
        while idx < stop:
            print( idx )
            idx = self.index( idx + "+1c" )

    def getStylesAsString( self ) -> str:
        tagstring:str = ""
        tagnames = self.tag_names() # get a tuple of tagnames
        for tagname in tagnames:
            if tagname != "sel":
                ranges = self.tag_ranges( tagname )
                if len( ranges ) > 0:
                    tagstring += ( tagname + ":" )
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
        if not stylesstr: return

        styles = stylesstr.split( "$" ) # -> bold:1.3,1.6;2.2.,3.4
        for style in styles:
            parts = style.split( ":") #parts[0]: bold  parts[1]:1.3,1.6;2.2,3.4
            ranges = parts[1].split( ";" ) # -> ranges: 1.2,1.6
            for range in ranges:
                startstop = range.split( "," )
                start = startstop[0]
                stop = startstop[1]
                self.tag_add( parts[0], start, stop )

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
    ta = text_area
    ta.insert( "1.0", "This is a bloody nonsense test text. Delete it or not, either one is fine." )
    ta.testIterate( "1.3", "1.5" )

    # Placing cursor in the text area
    text_area.focus()
    win.mainloop()

if __name__ == '__main__':
    test()