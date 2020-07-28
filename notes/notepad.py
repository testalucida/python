import sys
import tkinter as tk
from tkinter import ttk, FLAT
from tkinter.font import Font, ITALIC, BOLD, NORMAL
sys.path.append('/home/martin/Projects/python/mywidgets')
from mywidgets import MyText2


class Notepad( ttk.Frame ):
    """
    A text editor with some styling buttons
    """

    def __init__( self, parent, *args, **kwargs ):
        ttk.Frame.__init__( self, parent, *args, **kwargs )
        self.rowconfigure( 1, weight=1 )
        self.columnconfigure( 0, weight=1 )

        self.toolbar = ttk.Frame(self)
        self.toolbar.grid( row=0, column=0, sticky='w', padx=3, pady=3 )
        
        self.bold_btn:ttk.Button = None
        self.italic_btn:ttk.Button = None
        self.red_btn:ttk.Button = None
        self.clear_btn:ttk.Button = None
        self.list_tags_btn:ttk.Button = None
        self.text:MyText2 = None
        
        self._create_button_styles()
        self._create_buttons( 1, 1 )
        
       
          # Creates a bold font
        self.normal_font =  Font( family="Times", size=12 )
        self.bold_font = Font( family="Helvetica", size=12, weight="bold" )
        self.italic_font = Font( family="Helvetica", size=12, slant="italic" )
        self.bold_italic_font = Font( family="Helvetica", size=12, weight="bold", slant="italic" )

        
        self._create_text_widget( 1, 1 )
        self._configure_tags()
        
    def _create_button_styles( self ) -> None:
        s = ttk.Style()
        s.configure( "boldbtn.TButton", font=( 'Times', 16, BOLD, ITALIC), relief='flat', highlightthickness=0, borderwidth=0 )
        s.configure( "italicbtn.TButton", font=( 'Times', 16, NORMAL, ITALIC), relief='flat', highlightthickness=0, borderwidth=0 )
        s.configure( "clearbtn.TButton", font=( 'Times', 16, NORMAL ), relief='flat', highlightthickness=0, borderwidth=0 )
        
    def _create_buttons( self, padx, pady ) -> None:
        self.bold_btn = ttk.Button( self.toolbar, text="B", style="boldbtn.TButton", width=2, command=self._make_bold )
        self.bold_btn.grid( row=0, column=0, sticky="w", padx=padx, pady=pady )
        
        self.italic_btn = ttk.Button( self.toolbar, text="I", style="italicbtn.TButton", width=2, command=self._make_italic )
        self.italic_btn.grid( row=0, column=1, sticky="w", padx=padx, pady=pady )

        self.red_btn = ttk.Button( self.toolbar, text="R", width=2, command=self._make_red )
        self.red_btn.grid( row=0, column=2, sticky="w", padx=padx, pady=pady )

        self.clear_btn = ttk.Button( self.toolbar, text="C", style="clearbtn.TButton", width=2, command=self._clear )
        self.clear_btn.grid( row=0, column=3, sticky="w", padx=padx, pady=pady )
        
        self.list_tags_btn = ttk.Button( self.toolbar, text="List", command=self._on_list_tags )
        self.list_tags_btn.grid( row=0, column=4, sticky='w', padx=8, pady=pady )
        
    def _create_text_widget( self, padx, pady ) -> None:
        #self.text = MyText2( self, font=self.normal_font )
        self.text = MyText2( self )
        #self.text = MyText( self )
        self.text.registerModifyCallback( self._on_modified )
        self.text.insert("end", "Select part of text and then click 'Bold'...")
        self.text.focus()
        self.text.grid( row=1, column=0, sticky="nswe", padx=padx, pady=pady )
        
    def _configure_tags( self ) -> None:
        self.text.tag_configure( "BOLD", font=self.bold_font )
        self.text.tag_configure( "ITALIC", font=self.italic_font )
        self.text.tag_configure( "BOLD_ITALIC", font=self.bold_italic_font )
        self.text.tag_configure( "RED", foreground='red' )
        self.text.tag_bind( "BOLD", "<1>", self._on_bold )

    def _make_bold(self):
        # tk.TclError exception is raised if no text is selected
        selections:tuple = self.text.tag_ranges( "sel" )
        if len( selections ) > 0:
            try:
                self.text.tag_add("BOLD", "sel.first", "sel.last")        
            except tk.TclError as err:
                print( err )
           
        
    def _make_italic(self):
        # tk.TclError exception is raised if no text is selected
        try:
            self.text.tag_add("ITALIC", "sel.first", "sel.last")        
        except tk.TclError as err:
            print( err )

    def _make_red( self ):
        # tk.TclError exception is raised if no text is selected
        try:
            self.text.tag_add( "RED", "sel.first", "sel.last" )
        except tk.TclError as err:
            print( err )

    def _clear(self):
        self.text.tag_remove("BOLD",  "1.0", 'end')
        self.text.tag_remove("ITALIC", "1.0", 'end')
        self.text.tag_remove( "RED", "1.0", 'end' )
    
    def _on_bold( self , e, t ):
        print( "on bold" )
    
    def _on_modified( self, event ):
        print( "on modified" )
        
    def _on_list_tags( self ) -> None:
        print( "########## LIST #############" )
        print( "found tag_names: ", self.text.tag_names() )
        print( "tag_ranges BOLD: ", self.text.tag_ranges( "BOLD" ) )
        print( "tag_ranges ITALIC: ", self.text.tag_ranges( "ITALIC" ) )
        ranges = self.text.tag_ranges( "ITALIC" )
        for i in range( 0, len( ranges ), 2 ):
            start = ranges[i]
            end = ranges[i+1]
            print( "ITALIC: ", start, ", ", end, ": ", repr( self.text.get( start, end ) ) )
            
        print( "####################  DUMP  ##################" )
        self.text.dump( "1.0", "end" )


def demo():
    root = tk.Tk()
    Notepad(root).pack(expand=1, fill="both")
    root.mainloop()


if __name__ == "__main__":
    demo()    