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

class Connection:
    def __init__( self, item_id:int, conn_id:int, endpoint:int ):
        self.item_id:int = item_id # item id
        self.conn_id:int = conn_id # connection id
        self.endpoint:int = endpoint #may be 1 or 2 and indicates which pair of coords() of the connection line
        # belongs to the given item


class Point:
    def __init__( self, x:float, y:float ):
        self.x = x
        self.y = y


class BoundingRect:
    def __init__( self, item_id:int, rect_id:int, topLeft:Point, bottomRight:Point ):
        self.item_id:int = item_id
        self.rect_id:int = rect_id
        self.topLeft:Point = topLeft
        self.bottomRight:Point = bottomRight


class Controller:
    def __init__( self, canvas:MyCanvas ):
        self.canvas = canvas
        self.canvas.bind( "<Button-1>", self.onCanvasLeftMouse )
        self._selections:Dict[int, BoundingRect] = {} # key: id of selected object; value: id and coords of selection rectangle
        self._connections:Dict[int,List[Connection]] = {} # key: object id; value: list of collections referring to object id
        self._event_handled:bool = False
        #self._affected_conns:Tuple[Tuple[int,int]] = () # stores connections affected by dragging an item in order to
        # update them properly. The first Integer stores the id of the connection, the second the point to update.
        self._startX = 0
        self._startY = 0

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
        rect:int = self._createSelectionRect( id )


    def _unselect( self, id ):
        sel_rect:BoundingRect = self._selections[id]
        self.canvas.delete( sel_rect.rect_id )
        self._selections.pop( id )

    def isSelected( self, id:int ) -> bool:
        return ( id in self._selections.keys() )

    def onMouseEnter( self, id:int, evt:Event ):
        if self.canvas.type( id ) == "line": return

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
        if id not in self._selections.keys(): return
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
        if self.canvas.type( id ) == "line": return

        if not self.isSelected( id ):
            if evt.state & 1 == 1 or evt.state & 4 == 4: #Shift or Ctrl pressed
                self._select( id )
            else:
                self._clearSelections()
                self._select( id )

        # remember event position for dragging
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
        self.canvas.move( rect.rect_id, dx, dy )
        #update connections
        self._updateConnections( id, dx, dy )
        # update startX and startY
        self._startX += dx
        self._startY += dy

    def _updateConnections( self, id:int, dx, dy ) -> None:
        conn_list:List[Connection] = self._connections[id]
        for conn in conn_list:
            # get coords of connection line
            coords:List[float] = self.canvas.coords( conn.conn_id )
            idx1, idx2 = (0, 1) if conn.endpoint == 1 else (2, 3)
            xy:Tuple[float,float] = (coords[idx1], coords[idx2])
            coords[idx1] += dx
            coords[idx2] += dy
            #print( "conn: update coords by dx=%d, dy=%d: " % (dx, dy), ": ", coords )
            self.canvas.coords( conn.conn_id, coords )

    def _isPointInRect( self, point:Tuple[float,float], rect:Tuple[Tuple[float,float]] ) -> bool:
        px = point[0]
        py = point[1]
        if rect[0][0] <= px <= rect[1][0] and \
           rect[0][1] <= py <= rect[1][1]:
            return True

        return False

    def _createSelectionRect( self, id:int ) -> int:
        vertices:Tuple[Tuple[float,float]] = self._getSelectionRectCoords( id )
        sel:int = self.canvas.create_rectangle( vertices, outline='yellow', width=2 )
        topleft:Point = Point( vertices[0][0], vertices[0][1] )
        bottomright: Point = Point( vertices[1][0], vertices[1][1] )
        boundRect:BoundingRect = BoundingRect( id, sel, topleft, bottomright )
        self._selections[id] = boundRect
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
        self._connect( id1, line, 1 )
        self._connect( id2, line, 2 )
        return line

    def _connect( self, id:int, line:int, coord_number:int ) -> None:
        conn:Connection = Connection( id, line, coord_number )
        if id in self._connections.keys():
            self._connections[id].append( conn )
        else:
            self._connections[id] = [ conn, ]
        if line in self._connections.keys():
            self._connections[line].append( conn )
        else:
            self._connections[line] = [ conn, ]

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

    #cntrl.createOval( 100, 100, 300, 150, fill='yellow' )

    cntrl.connect( poly1, poly2 )

    xy = [(80, 90), (160, 90), (160, 160), (80, 160)]
    poly3 = cntrl.createPolygon( xy )
    cntrl.connect( poly1, poly3 )

    root.mainloop()

if __name__ == '__main__':
    test()