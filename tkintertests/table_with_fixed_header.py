import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar
#-----------------------------------------------------------------------------
# Scroll entry boxes with mouse wheel
#     canvas1, frame1
#
# Header row is on a separate canvas and will not scroll with entry boxes.
#     canvas2, frame2
#
# Could not align header and entries unless different fonts were used.
# Play with variable "font_choice" to see how it works
#-----------------------------------------------------------------------------
# define fonts and other preliminary things

font_choice = 1
if(font_choice == 1): # using same font sizes does not align well
    Label_Font = "Arial 10"
    Entry_Font = "Arial 10"
if(font_choice == 2): # using different font sizes not exactly aligned, but close
    Label_Font = "Arial 9 bold"
    Entry_Font = "Arial 10"
if(font_choice == 3): # this does not align well
    Label_Font = "Helvetica 10"
    Entry_Font = "Helvetica 10"
if(font_choice == 4): # this aligns pretty well (surprisingly)
    Label_Font = "Helvetica 14"
    Entry_Font = "Helvetica 14"

width_priority = 10
width_time_estimate = 15
width_description_1 = 90

Labels = ["Priority", "Time Est. (mins)", "Description 1"]

Widths = [width_priority, width_time_estimate, width_description_1]

Label_Colors = ["misty rose", "lavender", "lightcoral"]

list_length = 25

canvas_width = 1300
header_height = 25
#------------------------------------------------------------------------------
def populate1(framex):
    global entrys_1
    global entrys_2
    global entrys_3

    label_flag = 0 # 1 or 2 are options, 0 is off

    ijk_col = 0
    if(label_flag == 1):
        tttk.Label(framex, text=Labels[ijk_col]).grid(row=0, column=ijk_col)
    if(label_flag== 2):
        xy1 = tttk.Label(framex, text=Labels[ijk_col], font=Label_Font)
        xy1.grid(row=0, column=ijk_col)
        xy1.config(width=Widths[ijk_col], borderwidth="1", background=Label_Colors[ijk_col])
    entrys_1 = []
    variables_1 = []
    ii = 0
    for row in range(list_length):
        rowx = row + 1
        variables_1.append(StringVar())
        entrys_1.append(tttk.Entry(framex, textvariable=variables_1[ii], font=Entry_Font))
        entrys_1[-1].config(width=Widths[ijk_col], borderwidth="1")
        entrys_1[-1].grid(row=rowx, column=ijk_col)
        entrys_1[-1].config(fg="black", bg=Label_Colors[ijk_col])
        entrys_1[-1].delete(0, ttk.END)
        entrys_1[-1].insert(0, "Placeholder")
        ii += 1

    ijk_col = 1
    if(label_flag == 1):
        tttk.Label(framex, text=Labels[ijk_col]).grid(row=0, column=ijk_col)
    if(label_flag== 2):
        xy2 = tttk.Label(framex, text=Labels[ijk_col], font=Label_Font)
        xy2.grid(row=0, column=ijk_col)
        xy2.config(width=Widths[ijk_col], borderwidth="1", background=Label_Colors[ijk_col])
    entrys_2 = []
    variables_2 = []
    ii = 0
    for row in range(list_length):
        rowx = row + 1
        variables_2.append(StringVar())
        entrys_2.append(tttk.Entry(framex, textvariable=variables_2[ii], font=Entry_Font))
        entrys_2[-1].config(width=Widths[ijk_col], borderwidth="1")
        entrys_2[-1].grid(row=rowx, column=ijk_col)
        entrys_2[-1].config(fg="black", bg=Label_Colors[ijk_col])
        entrys_2[-1].delete(0, tttk.END)
        entrys_2[-1].insert(0, "Placeholder")
        ii += 1

    ijk_col = 2
    if(label_flag == 1):
        tttk.Label(framex, text=Labels[ijk_col]).grid(row=0, column=ijk_col)
    if(label_flag== 2):
        xy3 = tttk.Label(framex, text=Labels[ijk_col], font=Label_Font)
        xy3.grid(row=0, column=ijk_col)
        xy3.config(width=Widths[ijk_col], borderwidth="1", background=Label_Colors[ijk_col])
    entrys_3 = []
    variables_3 = []
    ii = 0
    for row in range(list_length):
        rowx = row + 1
        variables_3.append(StringVar())
        entrys_3.append(tttk.Entry(framex, textvariable=variables_3[ii], font=Entry_Font))
        entrys_3[-1].config(width=Widths[ijk_col], borderwidth="1")
        entrys_3[-1].grid(row=rowx, column=ijk_col)
        entrys_3[-1].config(fg="black", bg=Label_Colors[ijk_col])
        entrys_3[-1].delete(0, tttk.END)
        entrys_3[-1].insert(0, "Placeholder")
        ii += 1

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))
#-----------------------------------------------------------------------------
root = tk.Tk()
root.title("StackOverflow_Label_Entry_Align")
#---------------------------------
# set up canvas that scrolls for entries, header on separate canvas that does not scroll

canvas1 = tk.Canvas(root, borderwidth=0, background="#ffffff", height=400, width=canvas_width)
frame1 = ttk.Frame(canvas1, background="#ffffff")

xscrollbar = ttk.Scrollbar(root, orient=ttk.HORIZONTAL, command=canvas1.xview)
yscrollbar = ttk.Scrollbar(root, orient=ttk.VERTICAL, command=canvas1.yview)

yscrollbar.pack(side=ttk.RIGHT, fill=ttk.Y)
xscrollbar.pack(side=ttk.BOTTOM, fill=ttk.X)

canvas1.configure(xscrollcommand=xscrollbar.set)
canvas1.configure(yscrollcommand=yscrollbar.set)

canvas1.pack(side="bottom", fill="both", expand=True)
canvas1.create_window((4,4), window=frame1, anchor="nw")

frame1.bind("<Configure>", lambda event, canvas=canvas1: onFrameConfigure(canvas))

def _on_mousewheel(event):
    canvas1.yview_scroll(-1*(event.delta/120), "units")
canvas1.configure(yscrollincrement='20') # adjust sensitivity
canvas1.bind_all("<MouseWheel>", _on_mousewheel) # Oakley has a post on this

canvas1.focus_set() # key to making canvas bind to left, right keys
#-----------------------------------------------------------------------------
# set up separate canvas for header row that will not scroll

canvas2 = ttk.Canvas(root, borderwidth=0, background="#ffffff", height=header_height, width=canvas_width)
frame2 = ttk.Frame(canvas2, background="#ffffff")

canvas2.pack(side="top", fill="both", expand=True)
canvas2.create_window((0,0), window=frame2, anchor="nw", height=header_height)

x1 = ttk.Label(frame2, text=Labels[0], font=Label_Font)
x1.grid(row=0, column=0)
x1.config(width=Widths[0], borderwidth="1", background=Label_Colors[0])

x2 = ttk.Label(frame2, text=Labels[1], font=Label_Font)
x2.grid(row=0, column=1)
x2.config(width=Widths[1], borderwidth="1", background=Label_Colors[1])

x3 = ttk.Label(frame2, text=Labels[2], font=Label_Font)
x3.grid(row=0, column=2)
x3.config(width=Widths[2], borderwidth="1", background=Label_Colors[2])
#-----------------------------------------------------------------------------
populate1(frame1) # add entry boxes
#-----------------------------------------------------------------------------
root.mainloop()