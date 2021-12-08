class MietobjektUcc:
    """
    Sammelbecken für alle Mietobjekt-Prozesse.
    """
    def __init__( self):
        pass

    def getMietobjekte( self, mv_id:str ) -> str:
        """
        Liefert einen JSON-String, der eine Liste aller Mietobjekte enthält.
        :param mv_id:
        :return: JSON-String
        """
        raise NotImplementedError( "MietobjektUcc.getMietobjekte()")