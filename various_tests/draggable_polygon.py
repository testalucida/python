from tkinter import *
from functools import partial
from typing import List, Tuple, Dict

from mywidgets import ScrollableView

class MyCanvas( Canvas ):
    def __init__( self, parent ):
        Canvas.__init__( self, parent )
        self['bg'] = "white"

class DrawingPane( ScrollableView ):
    def __init__( self, parent ):
        ScrollableView.__init__( self, parent )
        self['bg'] = "yellow"
        self.canvas = Canvas( self.clientarea )
        self.canvas['bg'] = "black"
        self._startX = 0
        self._startY = 0


class Controller:
    def __init__( self, canvas:MyCanvas ):
        self.canvas = canvas
        self.canvas.bind( "<Button-1>", self.onCanvasLeftMouse )
        self._selections:Dict[int, int] = {} # key: id of selected object; value: id of selection rectangle
        self._connections:Dict[int,List[int]] = {} # key: object id; value: list of line id's related to key object
        self._event_handled:bool = False

    def onCanvasLeftMouse( self, evt:Event ):
        if not self._event_handled:
            self._clearSelections()
        else:
            self._event_handled = False

    def _clearSelections( self ) -> None:
        """
        Set all selected polygons to unselected.
        - remove focus rets
        - clear selection list
        :return:
        """
        ids = list( self._selections.keys() )
        for id in ids:
            self._unselect( id )

    def _select( self, id ):
        rect:int = self._drawFocusRect( id )
        self._selections[id] = rect

    def _unselect( self, id ):
        sel_rect:int = self._selections[id]
        self.canvas.delete( sel_rect )
        self._selections.pop( id )

    def isSelected( self, id:int ) -> bool:
        return ( id in self._selections )

    def onMouseEnter( self, id:int, evt:Event ):
        self.canvas["cursor"] = "hand2"

        # self.canvas["cursor"] = "fleur" # ok for moving object around
        # self.canvas["cursor"] = "sizing" # ok for resizing at the edges
        #self.canvas["cursor"] = "sb_v_double_arrow" # for resizing at top and bottom side
        # self.canvas["cursor"] = "sb_h_double_arrow"  # for resizing at left and right side
        # self.canvas["cursor"] = "bottom_right_corner" # OK! dragging bottom right corner
        # self.canvas["cursor"] = "top_left_corner"
        # self.canvas["cursor"] = "center_ptr"
        #self.canvas["cursor"] = "double_arrow" # same as center_ptr and fleur


    def onMouseLeave( self, id:int, evt:Event ):
        self.canvas["cursor"] = "arrow"

    def onMouseMove( self, id: int, evt: Event ):
        #self.canvas["cursor"] = "fleur"
        #self._setCursor( id, evt.x, evt.y )
        pass

    def onLeftMouse( self, id:int, evt:Event ) -> None:
        """
        callback function for left mouse clicked polygons
        :param id: id of polygon selected
        :param evt: mouse pressed event.
            state: 0 == Mouse pressed w/o any key pressed
            state: 1 == Shift
            state: 4 == Ctrl
        """
        #print( "onLeftMouse: ", id, " -- event: ", evt, "; state=", evt.state )
        if not self.isSelected( id ):
            if evt.state & 1 == 1 or evt.state & 4 == 4: #Shift or Ctrl pressed
                self._select( id )
            else:
                self._clearSelections()
                self._select( id )
        self._startX = evt.x
        self._startY = evt.y
        """
        unfortunately, this event is propagated to Canvas and this controller's onCanvasLeftMouse is callback'ed.
        That results in clearing the selection list. To prevent that we set _event_handled to True.
        """
        self._event_handled = True


    def onDrag( self, id:int, evt:Event ):
        #print( "drag %d: x_root=%d, x=%d -- y_root=%d, y=%d" % (id, evt.x_root, evt.x, evt.y_root, evt.y) )
        # drag amount
        dx = evt.x - self._startX
        dy = evt.y - self._startY
        #drag item
        self.canvas.move( id, dx, dy )
        #drag selection rectangle
        rect = self._selections[id]
        self.canvas.move( rect, dx, dy )
        #update connections
        self._updateConnections( id, dx, dy )
        # update startX and startY
        self._startX += dx
        self._startY += dy

    def _updateConnections( self, id:int, dx, dy ) -> None:
        # get center of item's surrounding rectangle
        selrect_coords:Tuple[Tuple[float,float]] = self._getSelectionRectCoords( id )
        conn_list:List[int] = self._connections[id]
        for conn in conn_list:
            # get coords of connection line
            coords:List[float] = self.canvas.coords( conn )
            xy:Tuple[float,float] = (coords[0], coords[1])
            if self._isPointInRect( xy, selrect_coords ):
                coords[0] += dx
                coords[1] += dy
                self.canvas.coords( conn, coords )

    def _isPointInRect( self, point:Tuple[float,float], rect:Tuple[Tuple[float,float]] ) -> bool:
        px = point[0]
        py = point[1]
        if px >= rect[0][0] and px <= rect[1][0] and \
           py >= rect[0][1] and px <= rect[1][1]:
           return True
        return False

    def _drawFocusRect( self, id:int ) -> int:
        vertices:Tuple[Tuple[float,float]] = self._getSelectionRectCoords( id )
        sel:int = self.canvas.create_rectangle( vertices, outline='yellow', width=2 )
        return sel

    def _getSelectionRectCenter( self, id:int ):
        rect:Tuple[Tuple[float,float]] = self._getSelectionRectCoords( id )
        x1:float = rect[0][0]
        x2: float = rect[1][0]
        y1: float = rect[0][1]
        y2: float = rect[1][1]
        x = ( x1 + x2 ) / 2
        y = ( y1 + y2 ) / 2
        return ( x, y )

    def _getSelectionRectCoords( self, id:int ) -> Tuple[Tuple[float, float]]:
        polycoords:List[float] = self.canvas.coords( id )
        xmin, ymin = 9999, 9999
        xmax, ymax = 0, 0
        n = 0
        for val in polycoords:
            if n == 0:
                # x value
                if val < xmin: xmin = val
                elif val > xmax: xmax = val
                n = 1
            else:
                # y value
                if val < ymin: ymin = val
                elif val > ymax: ymax = val
                n = 0
        #define focus rect coordinates from min and max x and y values
        return( (xmin, ymin), (xmax, ymax) )

    def _setCursor( self, id:int, mouse_x:int, mouse_y:int ) -> None:
        crsr = ""
        xy = self.canvas.coords( id )
        x0 = xy[0]
        x1 = xy[2]
        y0 = xy[1]
        y1 = xy[2]
        if mouse_x < x0 + 5 or mouse_x > x1 - 5:
            crsr = "sb_h_double_arrow"
        elif mouse_y < y0 + 5 or mouse_y > y1 - 5:
            crsr = "sb_v_double_arrow"

        self.canvas["cursor"] = crsr

    def createPolygon( self, vertices:List[Tuple[int,int]] ):
        poly = self.canvas.create_polygon( vertices )
        self._bind( poly )
        return poly

    def createOval( self, topLeftX:float, topLeftY:float, bottomRightX:float, bottomRightY:float, **kw ) -> int:
        """kw e.g. fill='red' """
        oval = self.canvas.create_oval( topLeftX, topLeftY, bottomRightX, bottomRightY, kw )
        self._bind( oval )
        return oval

    def createLine( self, *args, **kw ) -> int:
        """Create line with coordinates x1,y1,...,xn,yn."""
        line = self.canvas.create_line( args, kw )
        self._bind( line )
        return line

    def connect( self, id1:int, id2:int, conn_name:str="" ) -> int:
        x1, y1 = self._getSelectionRectCenter( id1 )
        x2, y2 =  self._getSelectionRectCenter( id2 )
        line = self.createLine( x1, y1, x2, y2 )
        # connect id1 and id2 with line
        self._connect( id1, line )
        self._connect( id2, line )
        return line

    def _connect( self, id:int, line:int ) -> None:
        if id in self._connections.keys(): self._connections[id].append( line )
        else: self._connections[id] = [ line, ]
        if line in self._connections.keys(): self._connections[line].append( id )
        else: self._connections[line] = [ id, ]

    def _bind( self, id:int ):
        self.canvas.tag_bind( id, "<Enter>", partial( self.onMouseEnter, id ) )
        self.canvas.tag_bind( id, "<Leave>", partial( self.onMouseLeave, id ) )
        self.canvas.tag_bind( id, "<Motion>", partial( self.onMouseMove, id ) )
        self.canvas.tag_bind( id, "<Button-1>", partial( self.onLeftMouse, id ) )
        self.canvas.tag_bind( id, "<B1-Motion>", partial( self.onDrag, id ) )

def test():
    root = Tk()
    root.rowconfigure( 0, weight=1 )
    root.columnconfigure( 0, weight=1 )

    dp = MyCanvas( root )
    dp.grid( row=0, column=0, sticky='nswe', padx=3, pady=3 )

    cntrl = Controller( dp )
    # a square
    xy = [(20, 20), (70, 20), (70, 70), (20, 70)]
    poly1 = cntrl.createPolygon( xy )

    xy = [(100, 20), (80, 70), (120, 70)]
    poly2 = cntrl.createPolygon( xy )

    cntrl.createOval( 100, 100, 300, 150, fill='yellow' )

    cntrl.connect( poly1, poly2 )

    root.mainloop()

if __name__ == '__main__':
    test()