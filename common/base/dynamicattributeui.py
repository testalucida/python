import copy
from typing import Type, List

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QWidget, QDialog

from base.baseqtderivates import BaseWidget, BaseGridLayout, BaseEdit, LineEdit, MultiLineEdit, BaseCheckBox, IntEdit, \
    BaseLabel, FloatEdit, BaseComboBox, BaseDialogWithButtons, getOkCancelButtonDefinitions
from base.interfaces import XBase, XBaseUI, VisibleAttribute


class DynamicAttributeView( BaseWidget ):
    def __init__(self, xbaseui:XBaseUI, title="", parent=None, flags=Qt.WindowFlags()):
        BaseWidget.__init__( self, parent, flags )
        self.setWindowTitle( title )
        self._xbaseui = xbaseui
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._widgets:List[BaseWidget] = list()
        self._firstEditableWidget:QWidget = None
        self._createUI()

    def _createUI( self ):
        row, col = 0, 0
        attrlist = self._xbaseui.getVisibleAttributes()
        for attr in attrlist:
            lbl = BaseLabel( attr.label )
            self._layout.addWidget( lbl, row, col )
            col += 1
            w = self._createWidget( attr.key, attr.type, attr.editable, attr.getWidgetWidth(), attr.getWidgetHeight() )
            self._widgets.append( w )
            self._layout.addWidget( w, row, col )
            value = self._xbaseui.getXBase().getValue( attr.key )
            w.setValue( value )
            if attr.nextRow:
                row += 1
                col = 0
            else:
                col += 1

    def _createWidget( self, key:str, type_:Type, editable:bool, widgetWidth:int=-1, widgetHeight=-1 ) -> QWidget:
        w:QWidget = type_()
        w.setObjectName( key )
        w.setEnabled( editable )
        if editable and self._firstEditableWidget is None:
            self._firstEditableWidget = w
        if widgetWidth > 0:
            w.setFixedWidth( widgetWidth )
        if widgetHeight > 0:
            w.setFixedHeight( widgetHeight )
        return w

    def setFocusToFirstEditableWidget( self ):
        self._firstEditableWidget.setFocus()

    def getXBaseUI( self ) -> XBaseUI:
        return self._xbaseui

    def getXBase( self ) -> XBase:
        return self._xbaseui.getXBase()

    def getXBaseCopy( self ) -> XBase:
        """
        returns a copy of the wrapped XBase-Object
        :return: a copy of the wrapped XBase-Object
        """
        return copy.deepcopy( self._xbaseui.getXBase() )

    def updateData( self ):
        """
        updates the wrapped XBase-Object with the (modified) values of the edit fields.
        :return:
        """
        xbase = self._xbaseui.getXBase()
        for w in self._widgets:
            key = w.objectName()
            val = w.getValue()
            xbase.setValue( key, val )

#################   DynamicAttributeDialog   #######################
class DynamicAttributeDialog( BaseDialogWithButtons ):
    def __init__(self,  xbaseui:XBaseUI, title="Ändern eines Datensatzes" ):
        BaseDialogWithButtons.__init__( self, title=title,
                                        buttonDefinitions=getOkCancelButtonDefinitions( self.accept, self.reject ) )
        self._view = DynamicAttributeView( xbaseui )
        self.setMainWidget( self._view )
        self._view.setFocusToFirstEditableWidget()

    def getDynamicAttributeView( self ):
        return self._view


def test():
    class XTest( XBase ):
        def __init__(self):
            XBase.__init__( self )
            self.master = "SB_Kaiser"
            self.mobj_id = "kaiser_22"
            self.mv_id = "marion_decker"
            self.jahr = 2022
            self.monat = "jun"
            self.betrag = 234.56
            self.umlegbar = False
            self.text = "Testtext"

    def onOk():
        print( "Okee" )
        v = d.getDynamicAttributeView()
        xcopy = v.getXBaseCopy()
        v.updateData()
        x = v.getXBase()
        equal = x.equals( xcopy )
        print( equal )
        # dicx = x.__dict__
        # dicxcopy = xcopy.__dict__
        # print( dicx == dicxcopy )
        # valsx = list( dicx.values() )
        # valscopy = list( dicxcopy.values() )
        # print( valsx == valscopy )
        # print( "modified: ", "no" if not x.equals( xcopy ) else "yes" )


    x = XTest()
    xui = XBaseUI( x )
    #xui.setEditables( (("betrag", float), ("umlegbar",bool), ("text", str) ) )
    vislist = ( VisibleAttribute( "master", BaseEdit, "Master: ", editable=False, nextRow=False ),
                VisibleAttribute( "mobj_id", BaseEdit, "Wohnung: ", editable=False ),
                VisibleAttribute( "betrag", FloatEdit, "Betrag: ", editable=True, widgetWidth=60 ) )
    xui.addVisibleAttributes( vislist )
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    d = DynamicAttributeDialog( xui )
    if d.exec_() == QDialog.Accepted:
        onOk()
    else:
        print( "Cancelled" )
    #d.okClicked.connect( onOk )
    #d.show()
    # v = DynamicAttributeView( xui, "View zum Testen" )
    # v.show()
    #app.exec_()

def test2():
    from PySide2.QtWidgets import QApplication
    app = QApplication()
    type_ = BaseComboBox
    inst = type_()
    print( inst )