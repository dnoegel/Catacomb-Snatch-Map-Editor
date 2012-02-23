# coding: utf-8

import gtk
import gobject
import math

from csnatch_editor_modules import TILES

## My drawing area
class DrawThingy(gtk.DrawingArea):    
    def __init__(self, settings, parent):
        gtk.DrawingArea.__init__(self)

        self.main = parent

        self.set_events(gtk.gdk.EXPOSURE_MASK
                            | gtk.gdk.LEAVE_NOTIFY_MASK
                            | gtk.gdk.BUTTON_PRESS_MASK
                            | gtk.gdk.SCROLL_MASK
                            | gtk.gdk.POINTER_MOTION_MASK
                            | gtk.gdk.POINTER_MOTION_HINT_MASK )
        self.connect("expose_event", self.expose_event)
        self.connect("scroll_event", self.scroll_event)
        self.connect("configure_event", self.configure_event)
        self.connect("motion_notify_event", self.motion_notify_event)
        self.connect("button_press_event", self.button_press_event)
        self.connect('realize',       self.realize_event)
        
        self.settings = settings
        
        self.pixmap = None
        self.current_object = "Wall"

        self.set_default_map()

    def set_default_map(self):
        self.points = {}
        for i in xrange(0, self.settings.SIZE_X):
            self.points[(i, 0)] = TILES["Wall"]
            self.points[(i, self.settings.SIZE_Y-1)] = TILES["Wall"]
        for i in xrange(0, self.settings.SIZE_Y):
            self.points[(0, i)] = TILES["Wall"]
            self.points[(self.settings.SIZE_X-1, i)] = TILES["Wall"]
        for i in [0, 47]:
            self.points[(22, i)] = TILES["Floor"]
            self.points[(23, i)] = TILES["Rail"]
            self.points[(24, i)] = TILES["Floor"]
            
            

    ## Set the name of the current tile
    def set_object(self, obj):
        self.current_object = obj
        self.set_color(TILES[obj])

    ## Set the current color (gc)
    def set_color(self, color):
        #~ self.current_gc = self.pixmap.new_gc()
        self.current_gc.set_foreground(self.get_colormap().alloc_color(color))
        #~ self.current_gc = gc

    ## Draws the grid
    def draw_grid(self, da):
        self.current_gc.set_line_attributes(self.settings.GRID_WIDTH, gtk.gdk.LINE_SOLID,
                                        gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        offset = int(self.settings.GRID_WIDTH / 2.0)
        self.set_color("#000000")
        for i, x in enumerate(w for w in range(0, self.settings.WIDTH, (self.settings.MULTI+self.settings.GRID_WIDTH))):
            da.window.draw_line(self.current_gc, x+offset, 0, x+offset, self.settings.WIDTH)
            da.window.draw_line(self.current_gc, 0, x++offset, self.settings.HEIGHT, x+offset)

    ## Draw all the points stored in self.points
    def draw_points(self, da):
        for x, y in self.points:
            self.set_color(self.points[(x, y)])
            da.window.draw_rectangle(self.current_gc, True, x*self.settings.MULTI+(x+1)*self.settings.GRID_WIDTH, y*self.settings.MULTI+(y+1)*self.settings.GRID_WIDTH, self.settings.MULTI, self.settings.MULTI)

    ## Draw a single point
    def draw_point(self, da, x, y, delete = False):
        real_x, real_y = int(math.floor(x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
        
        # Do not allow drawing outside the grid
        if real_x >= self.settings.SIZE_X or real_y >= self.settings.SIZE_Y: return
        # Only allow modifying the border, when the correspinding option was set
        if not self.settings.allow_modifying_borders and (real_x == 0 or real_y == 0 or real_x == (self.settings.SIZE_X-1) or real_y == (self.settings.SIZE_Y-1)) : return
        
        x, y = real_x*self.settings.MULTI+(real_x+1)*self.settings.GRID_WIDTH, real_y*self.settings.MULTI+(real_y+1)*self.settings.GRID_WIDTH
        
        if delete:
            tmp = self.current_object
            self.current_object = "Floor"
            self.set_color("#ffffff")
        da.window.draw_rectangle(self.current_gc, True, x, y, self.settings.MULTI, self.settings.MULTI)
        #~ da.queue_draw_area(x, y, self.settings.MULTI, self.settings.MULTI)
        
        self.points[(real_x, real_y)] = TILES[self.current_object]
        
        if delete:
            self.set_object(tmp)
    
    #
    # Callbacks
    #
    
    def realize_event(self, da):
        self.current_gc = da.window.new_gc()
        self.set_color("#000000")
        

    def configure_event(self, da, event):
        #~ x, y, width, height = da.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(da.window, self.settings.WIDTH, self.settings.HEIGHT)
        self.pixmap.draw_rectangle(da.get_style().white_gc, True, 0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        
        
        return True
    
    def expose_event(self, da, event):
        
        
        x , y, width, height = event.area
        da.window.draw_drawable(self.current_gc, self.pixmap, x, y, x, y, width, height)
        
        
        self.draw_grid(da)
        self.draw_points(da)
        
        return False
        
    def motion_notify_event(self, da, event):
        #~ if event.x >= self.settings.WIDTH: return
        real_x, real_y = int(math.floor(event.x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(event.y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
        self.emit("position", real_x, real_y)
        
        if event.state & gtk.gdk.BUTTON1_MASK and self.pixmap:
            self.draw_point(da, event.x, event.y)
        elif event.state & gtk.gdk.BUTTON3_MASK and self.pixmap:
            self.draw_point(da, event.x, event.y, delete=True)
        
        return True
        
    def button_press_event(self, da, event):
        
        #~ if event.x >= self.settings.WIDTH: return
        if event.button == 1 and self.pixmap:
            self.draw_point(da, event.x, event.y)
        elif event.button == 3 and self.pixmap:
            self.draw_point(da, event.x, event.y, delete=True)
        else:
            print event.button
        return True
        
    def scroll_event(self, da, event):
        if event.state  & gtk.gdk.CONTROL_MASK:
            if event.direction & gtk.gdk.SCROLL_DOWN:
                self.settings.MULTI-=1
            elif not event.direction | gtk.gdk.SCROLL_UP:
                self.settings.MULTI+=1
                
            self.set_size_request(self.settings.WIDTH, self.settings.HEIGHT)
            da.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        
## Register custom signals
gobject.type_register(DrawThingy)
gobject.signal_new("position", DrawThingy, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (int, int, ))
