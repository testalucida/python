from PySide2.QtCore import QModelIndex, Qt, QSize
from PySide2.QtGui import QStandardItemModel
from interfaces import XSonstAus
from typing import List, Dict

class ServiceTreeModel( QStandardItemModel ):
    """
    Ein TreeModel, das vor allem die Serviceleister und ihre Dienstleistungen des kommunalen Sektors enthält.
    """
    def __init__( self ):
        QStandardItemModel.__init__( self )

    def data( self, index: QModelIndex, role=Qt.DisplayRole ):
        if index.isValid():
            # if role in (Qt.DisplayRole, Qt.EditRole,):
            #     node = index.internalPointer()
            #     print( node )
            #     return node.name()
            if role == Qt.SizeHintRole:
                return QSize( 40, 30 )
            else:
                return super().data( index, role )