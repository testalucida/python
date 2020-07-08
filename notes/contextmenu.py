import tkinter # Tkinter -> tkinter in Python 3

class FancyListbox(tkinter.Listbox):
    def __init__(self, parent, *args, **kwargs):
        tkinter.Listbox.__init__(self, parent, *args, **kwargs)

        self.popup_menu = tkinter.Menu(self, relief=tkinter.FLAT)
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_selected)
        self.popup_menu.add_command(label="Select All",
                                    command=self.select_all)

        self.bind("<Button-3>", self.popup) # Button-2 on Aqua

    def popup(self, event):
        self.popup_menu.tk_popup( event.x_root, event.y_root, 0 )
        # try:
        #     self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        # finally:
        #     self.popup_menu.grab_release()

    def delete_selected(self):
        for i in self.curselection()[::-1]:
            self.delete(i)
        self.popup_menu.grab_release()
        self.popup_menu.destroy()

    def select_all(self):
        self.selection_set(0, 'end')

def test2():
    from tkinter import Tk, Label, Menu, Button

    root = Tk()

    w = Label( root, text="Right-click to display menu", width=40, height=20 )
    w.pack()

    # create a menu
    popup = Menu( root, tearoff=1, title=" ", relief=tkinter.FLAT )
    popup.add_command( label="Next" )  # , command=next) etc...
    popup.add_command( label="Previous" )
    popup.add_separator()
    popup.add_command( label="Home" )

    def do_popup( event ):
        # display the popup menu
        try:
            popup.tk_popup( event.x_root, event.y_root, 0 )
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            popup.grab_release()

    w.bind( "<Button-3>", do_popup )

    b = Button( root, text="Quit", command=root.destroy )
    b.pack()

    root.mainloop()

def test():
    root = tkinter.Tk()
    flb = FancyListbox(root, selectmode='multiple')
    for n in range(10):
        flb.insert('end', n)
    flb.pack()
    root.mainloop()

if __name__ == '__main__':
    test2()