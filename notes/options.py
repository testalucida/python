
class Options:
    def __init__( self ):
        pass

    def getOption( self, option_name:str ) -> str:
        with open( "app.ini" ) as inifile:
            for line in inifile:
                parts = line.split( "=" )
                if parts[0] == option_name:
                    return parts[1]
        return ""

