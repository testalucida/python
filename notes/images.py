from tkinter import PhotoImage

"""
class Singleton:
   __instance = None
   @staticmethod 
   def getInstance():
      ### Static access method. "
      if Singleton.__instance == None:
         Singleton()
      return Singleton.__instance
   def __init__(self):
      ### Virtually private constructor. 
      if Singleton.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         Singleton.__instance = self
"""
class ImageFactory:
    __instance = None

    @staticmethod
    def getInstance():
        ### Static access method. "
        if ImageFactory.__instance == None:
            ImageFactory()
        return ImageFactory.__instance

    def __init__( self ):
        ### Virtually private constructor.
        if ImageFactory.__instance != None:
            raise Exception( "This class is a singleton!" )
        else:
            ImageFactory.__instance = self
            self.imgNote:PhotoImage =  PhotoImage( file="/home/martin/Projects/python/notes/images/note_16.png" )
            self.imgFolder:PhotoImage = PhotoImage( file="/home/martin/Projects/python/notes/images/folder_16.png" )
