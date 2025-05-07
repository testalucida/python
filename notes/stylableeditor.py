import tkinter as tk
from tkinter import ttk, FLAT, Text, CURRENT, TclError
from tkinter import scrolledtext, font
from tkinter.font import Font, ITALIC, BOLD, NORMAL
from enum import Enum
from typing import List, Tuple, Dict, Sequence, Any
import webbrowser
from functools import partial

import sys
if not 'mywidgets' in sys.path: sys.path.append('/home/martin/Projects/python/mywidgets')

def testa( event ):
    print( "testa" )

BOLD_ITALIC = "bold_italic"
RED = "red"
GREEN = "green"
BLUE = "blue"
BLACK = "black"

###########################################

class StyleAction(Enum):
    BOLD = 1
    ITALIC = 2
    RED_FOREGROUND = 3
    BLUE_FOREGROUND = 4
    GREEN_FOREGROUND = 5
    BLACK_FOREGROUND = 6
    MARK_AS_LINK = 7

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
            startsandstops = self._text.tag_ranges( style )
            for i in range( 0, len( startsandstops ), 2 ):
                s = startsandstops[i]
                e = startsandstops[i+1]
                if self._text.compare( s, "<=", start ) and self._text.compare( e, ">=", tag.range.start ):
                    tag.range.stop = e if self._text.compare( e, "<=", stop ) else stop
                    break
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
        self['wrap'] = tk.WORD
        self['undo'] = True
        self.bind('<<TextModified>>', self._onModify)
        self.bind( '<KeyPress>', self._onKeyPress )
        self.bind( '<KeyPress-minus>', self._onHyphen )
        self.bind( '<KeyPress-Return>', self._onReturn )
        self._indent:bool = False # indentation mode on/off
        self.bind( '<Control-v>', self._onPaste )
        self.isModified:bool = False
        # define some fonts
        self._textfont = Font( self, self.cget( "font" ) )
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
        self.tag_configure( RED, foreground='red' )
        self.tag_configure( GREEN, foreground='green' )
        self.tag_configure( BLUE, foreground='blue' )
        self.tag_configure( "hyper", foreground="blue", underline=1 )
        self.tag_bind( "hyper", "<Enter>", self._enterHyper )
        self.tag_bind( "hyper", "<Leave>", self._leaveHyper )
        self.tag_bind( "hyper", "<Button-1>", self._clickHyper )
        #self.tag_configure( BLACK, foreground='black' )
        self._styleRanges:StyleRanges = StyleRanges( self )

        #text_font = font.nametofont( self.cget( "font" ) )
        bullet_width = self._textfont.measure( "- " )
        em = self._textfont.measure( "m" )
        self.tag_configure( "indented", lmargin1=em, lmargin2=em + bullet_width )

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
        # triggered by <<TextModified>> virtual event.
        # the event arg only contains x and y coordinates.
        # so this method is only used for callback purposes and
        # to set the isModified flag.
        self.isModified = True
        if self._cbfnc:
            self._cbfnc( event )

    def _onKeyPress( self, event ):
        """
        If in indentation mode, check if a char is added to the end of text. If so, expand
        "indented" range appropriate.
        Chars inserted in the mid of text will be taken care of by the Text widget itself.
        """
        if not self._indent: return
        # ignore Backspace and Delete
        if event.keysym in ( "BackSpace", "Delete" ): return
        # ignore insertions in the mid of text
        if not self.index( "end - 1c" ) == self.index( "insert" ): return
        self.insert( "insert", event.char, "indented" )
        return "break"

    def _onHyphen( self, event ) -> None:
        """
        check if the hyphen was entered in column 0.
        If so, we switch to indentation mode,
        where subsequent lines are indented.
        """
        l, c = self.getCaretPosition()
        if c == 0:
            self._indent = True
            print( "indentation mode ON" )

    def _onReturn( self, event ) -> None:
        """Check if in indentation mode. If so, switch it off."""
        print( "_onReturn", event )
        if event.state == 16: # Return pressed without any other key
            self._indent = False
            print( "indentation mode OFF" )

    def _onPaste( self, event ):
        # get the clipboard data, and replace all newlines
        # with the literal string "\n"
        clipboard = self.clipboard_get()
        clipboard = clipboard.replace( "\n", "\\n" )

        # delete the selected text, if any
        try:
            start = self.index( "sel.first" )
            end = self.index( "sel.last" )
            self.delete( start, end )
        except TclError as e:
            # nothing was selected, so paste doesn't need
            # to delete anything
            pass

        # insert the modified clipboard contents
        if self._indent:
            self.insert( "insert", clipboard, "indented" )
        else:
            self.insert( "insert", clipboard )
        #return "break"  # prevents Text widget from inserting text from clipboard.

    def getCaretPosition( self ) -> Tuple[int, int]:
        """returns line and column index of caret"""
        position = self.index( 'insert' )
        l = int( position.split( '.' )[0] )
        c = int( position.split( '.' )[1] )
        return l, c

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
            self._handleFontColor( RED )
        elif styleAction == StyleAction.BLUE_FOREGROUND:
            self._handleFontColor( BLUE )
        elif styleAction == StyleAction.GREEN_FOREGROUND:
            self._handleFontColor( GREEN )
        elif styleAction == StyleAction.BLACK_FOREGROUND:
            self._handleFontColor( BLACK )
        elif styleAction == StyleAction.MARK_AS_LINK:
            self._toggleLink()

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

        return

    def _toggleFontStyle( self, style:str, start:str, stop:str ) -> None:
        if self.isSet( style, start ):
            self._unsetFontStyle( style, start, stop )
        else:
            self._setFontStyle( style, start, stop )

    def isSet( self, style:str, idx:str ) -> bool:
        # seq = self.tag_nextrange( style, idx, idx ) # returns an empty tuple :-o
        # Note: even if style is not set, a tuple of len == 1 will be given.
        # The one and only element of that tuple is the string "None".
        # That contradicts to the tag_nextrange documentation, which pretends to return an empty string.
        #return True if len( seq ) > 1 else False
        stylelist = self.tag_names( idx )
        return True if style in stylelist or ( style in (BOLD, ITALIC) and BOLD_ITALIC in stylelist ) else False

    def _unsetFontStyle( self, style:str, start:str, stop:str ):
        """
        removes the given style within the given range defined by start and stop.
        Takes style "bold_italic" into account: if bold_italic is set and bold is to be removed,
        italic will remain. If italic is to be removed, bold will remain.
        """
        """
        Processing:
        Inspect the different style ranges within start-stop.
            - unset style ranges with matching style
            - ignore style ranges with different style (except BOLD_ITALIC if style to unset is not BOLD_ITALIC)
            - BOLD_ITALIC style ranges: remove BOLD_ITALIC and set ITALIC if style to unset is BOLD or set BOLD 
              if style to unset is ITALIC.
        """
        while self.compare( start, "<", stop ):
            tag = self._styleRanges.getFontStyleAndRange( start, stop )
            if tag.name == style:
                self.tag_remove( style, tag.range.start, tag.range.stop )
            elif tag.name == BOLD_ITALIC:
                self.tag_remove( BOLD_ITALIC, tag.range.start, tag.range.stop )
                self.tag_add( BOLD if style == ITALIC else ITALIC, tag.range.start, tag.range.stop )
            start = tag.range.stop

    def _setFontStyle( self, style: str, start: str, stop: str ):
        """
        applies the given style to the given range.
        start and stop are expected in the form "line.column"
        If bold is already set and italic is to add remove bold and set BOLD_ITALIC.
        If italic is already set and bold is to add remove bold and set BOLD_ITALIC.

        |                                | -> Range to set style
        start                            stop

            |   |         |  |             -> ranges where another style is already set. Replace that style by BOLD_ITALIC
        """
        while self.compare( start, "<", stop ):
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
                        #print( "_setFontStyle: adding bold_italic from %s to %s" % (tag.range.start, tag.range.stop) )
                        self.tag_add( BOLD_ITALIC, tag.range.start, tag.range.stop )
                # BOLD_ITALIC can be ignored.
            start = tag.range.stop

    def _handleFontColor( self, fontcolor:str ) -> None:
        self._unsetFontColors( "sel.first", "sel.last" )
        if fontcolor != BLACK:
            self._setFontColor( fontcolor, "sel.first", "sel.last" )

    def _setFontColor( self, fontcolor:str, start:str, stop:str ):
        self.tag_add( fontcolor, start, stop )

    def _unsetFontColors( self, start:str, stop:str ):
        for color in (BLUE, RED, GREEN):
            try:
                self.tag_remove( color, start, stop )
            except:
                pass

    def _toggleLink( self ):
        start, stop = self._getUrlBoundaries( "insert" )
        tag_names = self.tag_names( start )
        if "hyper" in tag_names:
            self.tag_remove( "hyper", start, stop )
        else:
            self.tag_add( "hyper", start, stop )

    def _openUrl( self, url ):
        webbrowser.open_new_tab( url )

    def _enterHyper( self, event ):
        self.config( cursor="hand2" )

    def _leaveHyper( self, event ):
        self.config( cursor="" )

    def _clickHyper( self, event ):
        start, stop = self._getUrlBoundaries( CURRENT )
        url = self.get( start, stop )
        self._openUrl( url )

    def _getUrlBoundaries( self, idx:Any ) -> Tuple[Any, Any]:
        """
        Returns the complete URL starting from index "insert".
        """
        idxA = idxB = self.index( idx )
        #search to the left 'til a space, tab or new line
        if self.compare( idxA, ">", "1.0" ):
            idxA = self.index( idxA + "-1c" )
            c = ""
            while self.compare( idxA, ">", "1.0" ):
                c = self.get( idxA, self.index( idxA + "+1c" ) )
                if c in (" ", "\n", "\t"):
                    idxA = self.index( idxA + "+1c" )
                    break
                idxA = self.index( idxA + "-1c" )

        #search to the right 'til a space, tab or new line
        c = ""
        while self.compare( idxB, "<", "end" ):
            c = self.get( idxB, self.index( idxB + "+1c" ) )
            if c in ("", "\n", "\t"):
                break
            idxB = self.index( idxB + "+1c" )

        return (idxA, idxB)


    def testIterate( self, start, stop ):
        idx = self.index( start )
        stop = self.index( stop )
        while self.compare( idx,  "<", stop ):
            print( idx )
            idx = self.index( idx + "+1c" )
        print( "READY." )

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
    def click1( url ):
        print( "click 1" )
        webbrowser.open_new_tab( url )

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
    text = (
        "by entering this hyphen (I really mean hyphen, not that bullet "
        "that is automatically generated) the section to be indented starts. "
        "When reaching the right border, a soft wrap is performed (I'm using "
        "wrap=tk.WORD) and the new line should look like it does here."
    )
    ta.insert( "end", "- " + text, "indented" )

    # ta.insert( "1.0", "This is a bloody nonsense test text.\nDelete it or not,\n either one is fine.\n"
    #                   "Look here: " )
    # hp = hyperlink.add( partial( click1, "www.kendelweb.de" ) )
    # ta.tag_add( hp[0], "1.0", "1.4" )
    # ta.tag_add( hp[1], "1.0", "1.4" )
    # ta.insert( "insert", "link", hyperlink.add( partial( click1, "www.kendelweb.de" ) ) )
    #ta.insert( "insert", "\n\n" )

    #ta.testIterate( "1.0", "end" )

    # Placing cursor in the text area
    text_area.focus()
    win.mainloop()

if __name__ == '__main__':
    test()