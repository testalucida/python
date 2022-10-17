import numbers
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Type, Iterable


class XBase:
    """
    Die Mutter aller Interfaces.
    Jedes Interface sollte von XBase abgeleitet werden, z.B. weil es einen DB-Lesezugriff gibt,
    der die gelesenen DB-Spalten einer DB-Row direkt in ein passendes von XBase abgeleitetes Interface verpackt.
    Außerdem werden die get- und setValue Methoden im BaseTableModel benötigt.

    XBase wird *intensivst* vom ImmoControlCenter benutzt, also Vorsicht beim Ändern.
    """
    def __init__( self, valuedict:Dict=None ):
        if valuedict:
            self.setFromDict( valuedict )

    def getValue( self, key ) -> Any:
        return self.__dict__[key]

    def setValue( self, key, value ):
        self.__dict__[key] = value

    def setFromDict( self, d: Dict ):
        _d = self.__dict__
        for k, v in d.items():
            _d[k] = v

    def equals( self, other ) -> bool:
        if other is None: return False
        # for key in self.__dict__.keys():
        #     try:
        #         selfval = self.__dict__[key]
        #         otherval = other.__dict__[key]
        #         if selfval and not otherval: return False
        #         if otherval and not selfval: return False
        #         if selfval and otherval and selfval != otherval: return False
        #     except:
        #         return False
        # return True
        return True if self.__dict__ == other.__dict__ else False

    def getKeys( self ) -> List:
        return list( self.__dict__.keys() )

    def toString( self, printWithClassname=False ) -> str:
        s = ( str( self.__class__ ) + ": " ) if printWithClassname else ""
        s += str( self.__dict__ )
        return s

    def print( self ):
        print( self.toString( printWithClassname=True ) )

class VisibleAttribute:
    #def __init__( self, key:str="", type:Type=str, label:str="", editable=True, nextRow=True ):
    def __init__( self, key:str, type_:Type, label:str, editable=True, widgetWidth=-1, widgetHeight=-1, nextRow=True ):
        self.key = key
        self.type = type_
        self.label = label
        self._comboValues:List[str] = None
        self.editable = editable
        self.nextRow = nextRow
        #self._textrows = 1 # nur für Textfelder interessant:Anzahl der Textzeilen
        self._widgetHeight = widgetHeight # default -1: Qt bestimmt die Höhe
        self._widgetWidth = widgetWidth  # default -1: Qt bestimmt die Breite

    def setTextSpec( self, widgetWidth:int, widgetHeight:int ):
        self._widgetHeight = widgetHeight
        self._widgetWidth = widgetWidth

    def setComboValues( self, valueList:List[str] ):
        self._comboValues = valueList

    def getWidgetHeight( self ) -> int:
        return self._widgetHeight

    def getComboValues( self ) -> List[str]:
        return self._comboValues

    def getWidgetWidth( self ) -> int:
        return self._widgetWidth

class XBaseUI:
    def __init__( self, xbase:XBase ):
        self._xbase = xbase
        self._attrList:List[VisibleAttribute] = list()

    def getXBase( self ) -> XBase:
        return self._xbase

    def addVisibleAttribute( self, attr:VisibleAttribute ):
        self._attrList.append( attr )

    def addVisibleAttributes( self, attrList:Iterable[VisibleAttribute] ):
        for attr in attrList:
            self._attrList.append( attr )

    def getVisibleAttributes( self ) -> List[VisibleAttribute]:
        return self._attrList

class XBaseUI_:
    def __init__( self, xbase:XBase ):
        self._xbase = xbase
        self._editables = list()
        self._visibles = list()
        self._bools = list()
        self._ints = list()
        self._floats = list()
        self._strings = list()

    def getXBase( self ) -> XBase:
        return self._xbase

    def setEditable( self, label:str, key:str, type:Type ):
        self._editables.append( self.__dict__[key] )
        self._setType( key, type )

    def setEditables( self, keyTypeList:Iterable[Iterable] ):
        """
        :param keyTypeList: Eine Liste, die aus kleinen Listen besteht: (label:str, key:str, type:Type)
        :return:
        """
        for l in keyTypeList:
            label, key, type = l[0], l[1], l[2]
            self.setEditable( key )
            self._setType( key, type )

    def _setType( self, key:str, type:Type ):
        if type == str:
            self._strings.append( key )
        elif type == int:
            self._ints.append( key )
        elif type == float:
            self._floats.append( key )
        elif type == bool:
            self._bools.append( key )

    def getEditables( self ) -> List[str]:
        return self._editables

    def setVisible( self, key:str, type:Type ):
        self._visibles.append( key )
        self._setType( key, type )

    def setVisibles( self, keyTypelist:List[List] ):
        """
        :param keyTypeList: Eine Liste, die aus kleinen Listen besteht: (key, type)
        :return:
        """
        for l in keyTypelist:
            key, type = l[0], l[1]
            self.setVisible( key )
            self._setType( key, type )

    def getVisibles( self ) -> List[str]:
        return self._visibles

    def isEditable( self, key:str ) -> bool:
        return key in self._editables

    def isVisible( self, key:str ) -> bool:
        return key in self._visibles

    def getType( self, key:str ) -> Type:
        pass
        

class XAttribute( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )
        self.key = ""
        self.type = "" # one of int, float, string
        self.label = ""
        self.value = None
        self.options = list()
        self.editable = True

####################  XChange  #######################
class Action( Enum ):
    INSERT = 1,
    UPDATE = 2,
    DELETE = 3,
    NONE = 4

    @staticmethod
    def toString( action ) -> str :
        if action == Action.INSERT: return "inserted"
        if action == Action.UPDATE: return "modified"
        if action == Action.DELETE: return "deleted"
        if action == Action.NONE: return "noaction"

# class XChange( XBase ):
#     __count = 0
#     def __init__( self, classtype:Type=None, method="", action:Action=Action.NONE,
#                   x:XBase=None, key:str="", oldval=None, newval=None,
#                   userdata:Any=None ):
#         XBase.__init__( self )
#         XChange.__count += 1
#         self._id = XChange.__count
#         self.type:Type = classtype
#         self.method = method
#         self.action = action
#         self.xbase:XBase = x
#         self.key = key
#         self.oldval = oldval
#         self.newval = newval
#         self.userdata = userdata
#         self.timestamp = datetime.now() # timestamp of instantiation
#         self.saved = False
#
#     def getId( self ) -> int:
#         return self._id
#
#     def getAsString( self, sep="\t", printWholeObject=False ) -> str:
#         ret = "change id: " + str( self.getId() ) + sep
#         ret += "changed in class: " + (str(self.type) if self.type else str(None)) + sep
#         ret += "action: " + ( Action.toString( self.action ) ) + sep
#         ret += "changed object: " + (str( self.xbase.__class__ ) if self.xbase else str( None )) + sep
#         ret += "key: " + str( self.key ) + sep
#         ret += "oldval: " + (str( self.oldval ) if self.oldval else str( None )) + sep
#         ret += "newval: " + (str( self.newval ) if self.newval else str( None )) + sep
#         ret += "userdata: " + (str( self.userdata ) if self.userdata else str( None )) + "\n"
#         if printWholeObject:
#             ret += "\nCHANGED OBJECT: " + str( self.xbase.__class__ ) + "\n" + self.xbase.toString( "\n" )
#         return ret

class TestItem( XBase ):
    def __init__( self ):
        XBase.__init__( self )
        import sys
        print( sys._getframe().f_code.co_name )
        self.nachname = ""
        self.vorname = ""
        self.plz = ""
        self.ort = ""
        self.str = ""
        self.alter = 0
        self.groesse = 0
        self.testi:TestItem = None


def test7():
    t = TestItem()
    t.nachname = "Kendel"
    t.vorname = "Martin"
    t.plz = "91077"
    t.ort = "Kleinsendelbach"
    t.testi = TestItem()
    t2 = t.testi
    t2.nachname = "Müller"
    t2.vorname = "Paul"
    print( t.toString( printWithClassname=True ) )
    #print( t.__dict__ )

def test5():
    import sys
    myname = sys._getframe().f_code.co_name
    print( myname )

def test3():
    def makeInstance( tp:Type ):
        if tp == TestItem:
            return tp()
        else: return None

    t = TestItem()
    print( type( t ) )
    print( str( t.__class__) )
    # tp:Type = XChange
    # print( str(tp) )
    # t2 = makeInstance( tp )
    # print( t2 )

def test2():
    # c1 = XChange()
    # c2 = XChange()
    # c3 = XChange()
    # print( c1.getId() )
    # print( c2.getId() )
    # print( c3.getId() )
    pass


def test():
    ti = TestItem()
    ti.vorname = "Paul"
    ti.nachname = "Schörder"
    # change = XChange( "Person", Action.UPDATE, ti, "vorname", ti.vorname, ti.nachname, "test blabla")
    # print( change.getAsString( "\n", printWholeObject=True ) )