
from tkinter import *
from tkinter import ttk
from mywidgets import ScrollableView

# class ScrollableView(Frame):
#     """
#     This is a Frame containing a Canvas and two Scrollbar objects.
#     !!!!!!!
#     NOTE: you must not add widgets to this ScrollableView,
#           instead use ScrollableView.clientarea!
#     !!!!!!!
#     """
#     def __init__(self, parent):
#         Frame.__init__(self, parent)
#         self.rowconfigure(0, weight=1)
#         self.columnconfigure(0, weight=1)
#         # parent.bind_all("<Button-4>", self._on_mousewheel)
#         # parent.bind_all("<Button-5>", self._on_mousewheel)
#
#         self.xsc = Scrollbar(self, orient=HORIZONTAL)
#         self.xsc.grid(row=1, column=0, sticky='we')
#
#         self.ysc = Scrollbar(self)
#         self.ysc.grid(row=0, column=1, sticky='ns')
#
#         c = Canvas(self, bg="#ffffff",
#                          xscrollcommand=self.xsc.set,
#                          yscrollcommand=self.ysc.set)
#         c.grid(row=0, column=0, sticky='nswe', padx=0, pady=0)
#
#         self.clientarea = Frame(c)
#         c.create_window((4, 4), window=self.clientarea, anchor="nw",
#                         tags="self.clientarea")
#
#         self.clientarea.bind("<Configure>", self._onFrameConfigure)
#         self.clientarea.bind('<Enter>', self._bound_to_mousewheel)
#         self.clientarea.bind('<Leave>', self._unbound_to_mousewheel)
#
#         self.xsc.config(command=c.xview)
#         self.ysc.config(command=c.yview)
#         self.canvas = c
#
#     def _onFrameConfigure(self, event):
#         """Reset the scroll region to encompass the inner frame"""
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))
#
#     def _bound_to_mousewheel(self, event):
#         self.canvas.bind_all("<Button-4>", self._on_mousewheel)
#         self.canvas.bind_all("<Button-5>", self._on_mousewheel)
#
#     def _unbound_to_mousewheel(self, event):
#         self.canvas.unbind_all("<Button-4>")
#         self.canvas.unbind_all("<Button-5>")
#
#     def _on_mousewheel(self, event):
#         print("_on_mousewheel")
#         self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

def populate(sv:ScrollableView):
    c = sv.clientarea
    #c = sv.innerframe
    for r in range(100):
        l = Label(c, text=str(r))
        l.grid(row=r, column=0, sticky='nswe', padx=3, pady=3)
        l = Label(c, text="Nasty text besides the number in the first column")
        l.grid(row=r, column=1, sticky='nswe', padx=3, pady=3)

def test():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.geometry('400x400')
    f = Frame(root)
    f.rowconfigure(0, weight=1)
    f.columnconfigure(0, weight=1)
    f.grid(row=0, column=0, sticky='nswe', padx=2, pady=2)

    sv = ScrollableView(f)
    sv.grid(row=0, column=0, sticky='nswe', padx=3, pady=3)
    populate(sv)

    sv2 = ScrollableView(f)
    sv2.grid(row=1, column=0, sticky='nswe', padx=3, pady=3)
    populate(sv2)

    # c1 = ScrolledCanvas(root)
    # c1.grid(row=0, column=0, sticky='nswe', padx=3, pady=3)
    # c1.testpopulate()
    #
    # c2 = ScrolledCanvas(root)
    # c2.grid(row=1, column=0, sticky='nswe', padx=3, pady=3)
    # c2.testpopulate()

    root.mainloop()

if __name__ == '__main__':
    test()