# coding: utf-8


import gtk
import gobject
import math

from csnatch_editor_modules import *
import csnatch_editor_modules.tiles 


## My drawing area
class DrawThingy(gtk.DrawingArea):    
    def __init__(self, settings, parent):
        gtk.DrawingArea.__init__(self)

        self.main = parent
        self.settings = settings
        
        
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
        
        
        self.pixmap = None
        self.current_object = WALL
        self.set_double_buffered(True)
        #~ self.realize()
        

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
        if self.settings.GRID_WIDTH == 0: return
        self.current_gc.set_line_attributes(self.settings.GRID_WIDTH, gtk.gdk.LINE_SOLID,
                                        gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        offset = int(self.settings.GRID_WIDTH / 2.0)
        self.set_color("#000000")
        for i, x in enumerate(w for w in range(0, self.settings.WIDTH, (self.settings.MULTI+self.settings.GRID_WIDTH))):
            da.window.draw_line(self.current_gc, x+offset, 0, x+offset, self.settings.WIDTH)
            da.window.draw_line(self.current_gc, 0, x++offset, self.settings.HEIGHT, x+offset)

    ## Draw all the points stored in self.points
    def draw_points(self, da):
        print "draw points"
        for x in xrange(0, (self.settings.SIZE_X)):
            for y in xrange(0, (self.settings.SIZE_Y)):
                #~ print x, y
                tile = self.tiles.points[(x, y)]
                tile_obj = self.tiles.place_tile(tile.tile, tile.x, tile.y)
                self.__draw_pixbuf(da, tile_obj.pixbuf, tile_obj.x, tile_obj.y, offset=tile_obj.offset)
                
        da.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        return
        print "points"
        for x in xrange(0, self.settings.SIZE_X):
            for y in xrange(0, self.settings.SIZE_Y):
                obj = self.points.get((x, y), None)
                if  obj is None: continue
                obj = COLORS[obj]                
                self.set_color(self.points[(x, y)])
                da.window.draw_rectangle(self.current_gc, True, x*self.settings.MULTI+(x+1)*self.settings.GRID_WIDTH, y*self.settings.MULTI+(y+1)*self.settings.GRID_WIDTH, self.settings.MULTI, self.settings.MULTI)
                
                c = 0
                values = [1, 2, 4, 8]
                for v, i in enumerate([(0, -1), (-1, 0), (1, 0), (0, 1)]):
                    x1, y1 = x+i[0], y+i[1]
                    t = self.points.get((x1, y1), None)
                    if t and COLORS[t] == "Rail":
                        c += values[v]
                        
                
                _x, _y = x*self.settings.MULTI+(x+1)*self.settings.GRID_WIDTH, y*self.settings.MULTI+(y+1)*self.settings.GRID_WIDTH
                if obj == "Rail":
                    offset, sub = self.tiles.get_tile(obj, self.settings.MULTI, self.settings.MULTI, c)
                else:
                    offset, sub = self.tiles.get_tile(obj, self.settings.MULTI, self.settings.MULTI)
                da.window.draw_pixbuf(None, sub, 0, 0, _x, _y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)        
    
    def draw_point(self, da, tile_x, tile_y, tile, force=False, update_neighbours=True, expose=False):
        #~ print "draw", tile_x, tile_y, TILE_NAMES[tile]
        
        # Do not allow drawing outside the grid
        if tile_x >= self.settings.SIZE_X or tile_y >= self.settings.SIZE_Y: return
        # Only allow modifying the border, when the correspinding option was set
        if not (self.settings.allow_modifying_borders or force) and (tile_x == 0 or tile_y == 0 or tile_x == (self.settings.SIZE_X-1) or tile_y == (self.settings.SIZE_Y-1)) : return


        ## fix top tile if the current one was a big tile
        # Not needed if triggered by expose event
        if not expose:
            old_tile =  self.tiles.points[(tile_x, tile_y)]
            old_neighbor = old_tile.get_neighbour(TOP)
            if old_neighbor and old_tile.tile in BIG_TILES:
                tile_obj = self.tiles.place_tile(old_neighbor.tile, old_neighbor.x, old_neighbor.y)
                self.__draw_pixbuf(da, tile_obj.pixbuf, tile_obj.x, tile_obj.y, offset=tile_obj.offset)


        
        if tile in NEED_GROUND:
            tile_ground = self.tiles.place_tile(FLOOR, tile_x, tile_y)
            self.__draw_pixbuf(da, tile_ground.pixbuf, tile_x, tile_y, offset=tile_ground.offset)

        tile_obj = self.tiles.place_tile(tile, tile_x, tile_y)
        self.__draw_pixbuf(da, tile_obj.pixbuf, tile_x, tile_y, offset=tile_obj.offset)



        ## As the big-tile fix is slow, we don't need it after expose
        # events, as the tiles are set from top left to bottom right
        # so that no tiles will be overwritten
        if expose: return
        
        self.emit("changed")
        
        ## Fix bottom tile if it was a big tile
        neighbour =  tile_obj.get_neighbour(BOTTOM)
        if neighbour and neighbour.tile in BIG_TILES:
            #~ tile_obj = self.tiles.place_tile(neighbour.tile, neighbour.x, neighbour.y)
            self.draw_point(da, neighbour.x, neighbour.y, neighbour.tile, force=True)
            #~ self.__draw_pixbuf(da, neighbour.pixbuf, neighbour.x, neighbour.y, offset=tile_obj.offset)
            
        ## Update surrounding tiles
        if tile_obj.tile in UPDATE_TILES:
            if update_neighbours:
                for pos in (TOP, LEFT, RIGHT, BOTTOM):
                    neighbour =  tile_obj.get_neighbour(pos)
                    if neighbour:
                        self.draw_point(da, neighbour.x, neighbour.y, neighbour.tile, update_neighbours=False)
        
                   
    def __draw_pixbuf(self, da, pb, x, y, offset):
        x = x * (self.settings.GRID_WIDTH + self.settings.MULTI)
        y = y * (self.settings.GRID_WIDTH + self.settings.MULTI)
        da.window.draw_pixbuf(None, pb, 0, 0, x, y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        #~ self.queue.put((da, pb, x, y, offset))
        #~ da.window.draw_drawable(self.current_gc, pb, 0, 0, x, y+offset, -1, -1)
        
    #~ def __process_queue(self):
        #~ try:
            #~ while True:
                #~ da, pb, x, y, offset = self.queue.get(block=False)
                #~ x = x * (self.settings.GRID_WIDTH + self.settings.MULTI)
                #~ y = y * (self.settings.GRID_WIDTH + self.settings.MULTI)
                #~ da.window.draw_pixbuf(None, pb, 0, 0, x, y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        #~ except Queue.Empty:
            #~ pass
        #~ return True
    ## Draw a single point
    def draw_point_old(self, da, x, y, delete = False, tile=None):
        real_x, real_y = int(math.floor(x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
        
        # Do not allow drawing outside the grid
        if real_x >= self.settings.SIZE_X or real_y >= self.settings.SIZE_Y: return
        # Only allow modifying the border, when the correspinding option was set
        if not self.settings.allow_modifying_borders and (real_x == 0 or real_y == 0 or real_x == (self.settings.SIZE_X-1) or real_y == (self.settings.SIZE_Y-1)) : return
        
        x, y = real_x*self.settings.MULTI+(real_x+1)*self.settings.GRID_WIDTH, real_y*self.settings.MULTI+(real_y+1)*self.settings.GRID_WIDTH
        if not tile:
            obj = self.current_object
        else:
            obj = tile
        
        
        self.tiles.points[(real_x, real_y)] = TILES[obj]
        
        if obj == "Rail":

            
            
            offset, sub = self.tiles.get_tile("Floor", self.settings.MULTI, self.settings.MULTI)
            da.window.draw_pixbuf(None, sub, 0, 0, x, y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)       
            
            offset, sub = self.tiles.get_tile(obj, self.settings.MULTI, self.settings.MULTI, c)
            
            if not tile:
                for v, i in enumerate([(0, -1), (-1, 0), (1, 0), (0, 1)]):
                    x1, y1 = x+i[0]*self.settings.MULTI, y+i[1]*self.settings.MULTI
                    rx1, ry1 = real_x+i[0], real_y+i[1]
                    print real_x, real_y, rx1, ry1
                    t = self.points.get((rx1, ry1), None)
                    if t and COLORS[t] == "Rail":
                        self.draw_point(da, x1, y1, delete, "Rail")
        else:
            offset, sub = self.tiles.get_tile(obj, self.settings.MULTI, self.settings.MULTI)
        
        #~ pixbuf = gtk.gdk.pixbuf_new_from_file("map/floortiles.png") #one way to load a pixbuf
        #~ sub = pixbuf.subpixbuf(0, 0, 32, 32)
        #~ sub = sub.scale_simple(self.settings.MULTI, self.settings.MULTI, gtk.gdk.INTERP_BILINEAR)
        da.window.draw_pixbuf(None, sub, 0, 0, x, y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)        
        
        if self.current_object == "Wall" and self.points.get((real_x, real_y+1), None) == TILES[self.current_object]:
            self.draw_point(da, x, y+self.settings.MULTI, delete=False)
        
        """
        if delete:
            tmp = self.current_object
            self.current_object = "Floor"
            self.set_color("#ffffff")
        #da.window.draw_rectangle(self.current_gc, True, x, y, self.settings.MULTI, self.settings.MULTI)

        #~ da.queue_draw_area(x, y, self.settings.MULTI, self.settings.MULTI)
        """
        
        
        #~ if delete:
            #~ self.set_object(tmp)
    
    #
    # Callbacks
    #
    
    def realize_event(self, da):
        self.current_gc = da.window.new_gc()
        self.set_color("#000000")
        self.tiles = csnatch_editor_modules.tiles.Tiles(self.settings)
        #~ self.draw_points(da)
        #~ da.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        #~ raw_input()

    def configure_event(self, da, event):
        #~ x, y, width, height = da.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(da.window, self.settings.WIDTH, self.settings.HEIGHT)
        self.pixmap.draw_rectangle(da.get_style().white_gc, True, 0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        
        
        return True
    
    def expose_event(self, da, event):
        #~ print "expose"
        x , y, width, height = event.area
        #~ print x, width
        
        b = self.settings.GRID_WIDTH + self.settings.MULTI
        
        real_x, real_y = int(math.floor(x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
        real_w, real_h = int(math.ceil(width/(self.settings.MULTI+self.settings.GRID_WIDTH)))+1, int(math.ceil(height/(self.settings.MULTI+self.settings.GRID_WIDTH)))+1
        
        real_x -= 1 
        real_y -= 1
        real_h += 5
        real_w += 5 
        
        real_x = max(0, real_x)
        real_y = max(0, real_y)
        if real_x > self.settings.SIZE_X: real_x = self.settings.SIZE_X-1
        if real_w + real_x > self.settings.SIZE_X: real_w = (self.settings.SIZE_X)-real_x
        if real_y > self.settings.SIZE_Y: real_y = self.settings.SIZE_Y-1
        if real_h + real_y > self.settings.SIZE_Y: real_h = (self.settings.SIZE_Y)-real_y
        
        i = 0
        points = self.tiles.points
        for x in xrange(real_x, real_x+real_w, 1):
            for y in xrange(real_y, real_y+real_h, 1):
                i+=1
                #~ _x = x * b
                #~ _y = y * b
                tile = points[(x, y)]
                #~ _x, _y= x*(self.settings.MULTI+self.settings.GRID_WIDTH), y*(self.settings.MULTI+self.settings.GRID_WIDTH)
                #~ offset, sub = self.tiles.get_tile(obj, self.settings.MULTI, self.settings.MULTI)
                #~ da.window.draw_pixbuf(None, sub, 0, 0, _x, _y+offset, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)  
                #~ assert x >= 0 and y>=0
                self.draw_point(da, x, y, tile.tile, force=True, expose = True)

        print i

        ## what was that for??
        #~ da.window.draw_drawable(self.current_gc, self.pixmap, x, y, x, y, width, height)
        
        #~ self.draw_grid(da)
        #~ self.draw_points(da)
        #~ 
        return False
        
    def motion_notify_event(self, da, event):
        
        x, y = int(math.floor(event.x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(event.y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
        self.emit("position", x, y)
        
        if event.state & gtk.gdk.BUTTON1_MASK and self.pixmap:
            self.draw_point(da, x, y, self.current_object)
        elif event.state & gtk.gdk.BUTTON3_MASK and self.pixmap:
            self.draw_point(da, x, y, FLOOR)
        
        return True
        
    def button_press_event(self, da, event):
        
        x, y = int(math.floor(event.x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(event.y/(self.settings.MULTI+self.settings.GRID_WIDTH)))

        if event.button == 1 and self.pixmap:
            self.draw_point(da, x, y, self.current_object)
        elif event.button == 3 and self.pixmap:
            self.draw_point(da, x, y, FLOOR)
        else:
            print event.button
        
        return True
        
    def scroll_event(self, da, event):
        if event.state  & gtk.gdk.CONTROL_MASK:
            if event.direction & gtk.gdk.SCROLL_DOWN and self.settings.MULTI >= 2:
                self.settings.MULTI-=3
            elif not event.direction | gtk.gdk.SCROLL_UP and self.settings.MULTI <50:
                self.settings.MULTI+=3
                
            self.set_size_request(self.settings.WIDTH, self.settings.HEIGHT)
            #~ da.queue_draw_area(0, 0, self.settings.WIDTH*10, self.settings.HEIGHT*10)
            
            real_x, real_y = int(math.floor(event.x/(self.settings.MULTI+self.settings.GRID_WIDTH))), int(math.floor(event.y/(self.settings.MULTI+self.settings.GRID_WIDTH)))
            self.emit("position", real_x, real_y)
        
## Register custom signals
gobject.type_register(DrawThingy)
gobject.signal_new("position", DrawThingy, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (int, int, ))
gobject.signal_new("changed", DrawThingy, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, ())
