from tkinter import *
from functools import partial
from typing import List, Tuple

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

class Controller:
    def __init__( self, canvas:MyCanvas ):
        self.canvas = canvas
        self.canvas.bind( "<Button-1>", self.onCanvasLeftMouse )
        self._selections:List[id] = list()
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
        #todo: remove focus rects
        self._selections.clear()

    def _select( self, id ):
        self._drawFocusRect( id )
        self._selections.append( id )

    def _unselect( self, id ):
        #todo: redraw polygon id
        self._selections.remove( id )

    def onMouseEnter( self, id:int, evt:Event ):
        print( "onEnter: ", id )

        # self.canvas["cursor"] = "fleur" # ok for moving object around
        # self.canvas["cursor"] = "sizing" # ok for resizing at the edges
        #self.canvas["cursor"] = "sb_v_double_arrow" # for resizing at top and bottom side
        # self.canvas["cursor"] = "sb_h_double_arrow"  # for resizing at left and right side
        # self.canvas["cursor"] = "bottom_right_corner" # OK! dragging bottom right corner
        # self.canvas["cursor"] = "top_left_corner"
        # self.canvas["cursor"] = "center_ptr"
        #self.canvas["cursor"] = "double_arrow" # same as center_ptr and fleur


    def onMouseLeave( self, id:int, evt:Event ):
        print( "onLeave: ", id )
        self.canvas["cursor"] = "arrow"

    def onMouseMove( self, id: int, evt: Event ):
        print( "onMove: ", id )
        #self.canvas["cursor"] = "fleur"
        self._setCursor( id, evt.x, evt.y )

    def onLeftMouse( self, id:int, evt:Event ) -> None:
        """
        callback function for left mouse clicked polygons
        :param id: id of polygon selected
        :param evt: mouse pressed event.
            state: 0 == Mouse pressed w/o any key pressed
            state: 1 == Shift
            state: 4 == Ctrl
        """
        print( "onLeftMouse: ", id, " -- event: ", evt, "; state=", evt.state )
        if evt.state & 1 == 1 or evt.state & 4 == 4: #Shift or Ctrl pressed
            self._select( id )
        else:
            self._clearSelections()
            self._select( id )
        #coords:List[float] = self.canvas.coords( id )
        #print( coords )
        """
        unfortunately, this event is propagated to Canvas and this controller's onCanvasLeftMouse is callback'ed.
        That results in clearing the selection list. To prevent that we set _event_handled to True.
        """
        self._event_handled = True


    def onDrag( self, id:int, evt:Event ):
        print( "drag %d: x_root=%d, x=%d -- y_root=%d, y=%d" % (id, evt.x_root, evt.x, evt.y_root, evt.y) )

    def _drawFocusRect( self, id:int ) -> None:
        vertices:Tuple[Tuple[float,float]] = self._getFocusRectCoords( id )
        print( vertices )

    def _getFocusRectCoords( self, id:int ) -> Tuple[Tuple[float,float]]:
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
        return( (xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax) )

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
        self.canvas.tag_bind( poly, "<Enter>", partial( self.onMouseEnter, poly ) )
        self.canvas.tag_bind( poly, "<Leave>", partial( self.onMouseLeave, poly ) )
        self.canvas.tag_bind( poly, "<Motion>", partial( self.onMouseMove, poly ) )
        self.canvas.tag_bind( poly, "<Button-1>", partial( self.onLeftMouse, poly ) )
        self.canvas.tag_bind( poly, "<B1-Motion>", partial( self.onDrag, poly ) )

def test():
    root = Tk()
    root.rowconfigure( 0, weight=1 )
    root.columnconfigure( 0, weight=1 )

    dp = MyCanvas( root )
    dp.grid( row=0, column=0, sticky='nswe', padx=3, pady=3 )

    cntrl = Controller( dp )
    # a square
    xy = [(20, 20), (70, 20), (70, 70), (20, 70)]
    cntrl.createPolygon( xy )

    xy = [(100, 20), (80, 70), (120, 70)]
    cntrl.createPolygon( xy )

    root.mainloop()

if __name__ == '__main__':
    test()