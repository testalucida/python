#! /usr/bin/env python3
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# In this prototype/example a QTreeView is created. Then it's populated with
# three containers and all containers are populated with three rows, each
# containing three columns.
# Then the last container is expanded and the last row is selected.
# The container items are spanned through the all columns.
# Note: this requires > python-3.2
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys, os, pprint, time
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class TreeTableModel( QStandardItemModel ):
    def __init__( self ):
        QStandardItemModel.__init__( self )

    def data( self, index: QModelIndex, role=Qt.DisplayRole ):
        if index.isValid():
            # if role in (Qt.DisplayRole, Qt.EditRole,):
            #     node = index.internalPointer()
            #     print( node )
            #     return node.name()
            if role == Qt.SizeHintRole:
                return QSize( 40, 40 )
            else:
                return super().data( index, role )

class TreeView( QTreeView ):
    def __init__( self, parent ):
        QTreeView.__init__( self, parent )
        self.setUniformRowHeights( True )
        self.setAlternatingRowColors( True )

######################################################################################
######################################################################################

def test():
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    app = QApplication(sys.argv)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # init widgets
    tv = TreeView()
    tv.setGeometry( 2100, 100, 500, 300 )
    #tv.setSelectionBehavior( QAbstractItemView.SelectRows )
    model = TreeTableModel() #QStandardItemModel()
    #model.setHorizontalHeaderLabels(['Kreditor', 'Objekt', 'Identifikation'])
    model.setHorizontalHeaderLabels(["Kreditor und Objekt auswählen"])
    tv.setModel( model )
    #tv.setUniformRowHeights( True )
    tv.setColumnWidth( 0, 300 )
    #tv.setAlternatingRowColors( True )
    #tv.setRootIsDecorated( False )
    #tv.setStyleSheet( "QTreeView::item:border-bottom { 1px solid #6d6d6d; }" )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # populate data
    # for i in range(3):
    #     parent1 = QStandardItem('Family {}. Some long status text for sp'.format(i))
    #     for j in range(3):
    #         child1 = QStandardItem('Child {}'.format(i*3+j))
    #         child2 = QStandardItem('row: {}, col: {}'.format(i, j+1))
    #         child3 = QStandardItem('row: {}, col: {}'.format(i, j+2))
    #         parent1.appendRow([child1, child2, child3])
    #     model.appendRow(parent1)
    #     # span container columns
    #     view.setFirstColumnSpanned(i, view.rootIndex(), True)

    parent1 = QStandardItem( "ABC Finance Köln" )
    child = QStandardItem( "NK_Kleist" )
    parent1.appendRow( [child,] )
    model.appendRow( parent1 )

    parent2 = QStandardItem( "EVS Abfall" )
    child2 = QStandardItem( "ILL_Eich (eich_01)" )
    child21 = QStandardItem( "V12345" )
    child2.appendRow( [child21,])
    parent2.appendRow( [child2,] )
    child3 = QStandardItem( "ILL_Eich (eich_03)" )
    parent2.appendRow( [child3,] )
    # c3 = QStandardItem( "ILL_Eich" )
    # c31 = QStandardItem( "Vnr 123456" )
    # jan = QStandardItem( "jan" )
    # feb = QStandardItem( "feb" )
    # mrz = QStandardItem( "mrz" )
    # c3.appendRow( [c31, jan, feb, mrz] )
    # parent2.appendRow( [c3,] )
    model.appendRow( parent2 )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # expand third container
    index = model.indexFromItem(parent1)
    tv.expand( index )
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # select last row
    selmod = tv.selectionModel()
    #index2 = model.indexFromItem(child)
    #selmod.select(index2, QItemSelectionModel.Select|QItemSelectionModel.Rows)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    tv.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    test()