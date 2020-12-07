from abc import ABC, abstractmethod

class MdiChildController( ABC ):
    def __init__( self ):
        pass

    @abstractmethod
    def save( self ):
        pass