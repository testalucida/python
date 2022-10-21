from v2.icc.iccwidgets import IccTableView, IccTableViewFrame

##################   EinAusTableView   ###############
class EinAusTableView( IccTableView ):
    def __init__( self ):
        IccTableView.__init__( self )
        self.setAlternatingRowColors( True )

##################   EinAusTableViewFrame   ##############
class EinAusTableViewFrame( IccTableViewFrame ):
    def __init__( self, tableView:IccTableView, withEditButtons=False ):
        IccTableViewFrame.__init__( self, tableView, withEditButtons )

