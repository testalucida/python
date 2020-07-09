from tkinter import *
from tkinter.font import families
from tkinter import PhotoImage
from mainframe import MainFrame
from controller import Controller

print ('sys.version: ', sys.version)
print ('sys.executable: ', sys.executable)
print ('sys.path: ', sys.path)


def main():
    root = Tk()
    root.title( "Notes" )
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    f = MainFrame(root)
    f.grid( row=0, column=0, sticky='nswe', padx=3, pady=3)
    Controller( f ).startWork()

    root.mainloop()



def dummy_callback():
    print( "callback" )

def testPng():
    root = Tk()
    root.geometry( "960x600" )
    root.title( "Show a .png image" )
    # root.rowconfigure( 0, weight=1 )
    # root.columnconfigure( 0, weight=1 )
    img = PhotoImage( file="/home/martin/Projects/python/notes/images/save_30.png" )
    btn = Button( root, image=img, relief=FLAT )
    btn.image = btn
    btn.grid( row=0, column=0, sticky='nw', padx=3, pady=3 )
    btn['command'] = dummy_callback

    root.mainloop()

def testFont():
    root = Tk()
    root.title( "Finally Pycharm working with tkinter" )
    available = families()
    print( len(available) )
    print( "availabe: ", available)
    f = MainFrame(root)
    f.grid( row=0, column=0)

    root.mainloop()


if __name__ == "__main__":
    #testPng()
    main()