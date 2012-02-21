#!/usr/bin/env python
# coding: utf-8

import os
import gtk
import math
import gobject
import zipfile
import tempfile

from PIL import Image

MULTI = 15
SIZE_X = 48
SIZE_Y = 48

GRID_WIDTH = 3

WIDTH = MULTI*SIZE_X+(SIZE_X+1)*GRID_WIDTH
HEIGHT = MULTI*SIZE_Y+(SIZE_Y+1)*GRID_WIDTH

TILES = {
    "Wall": "#ff0000",
    "Floor": "#ffffff",
    "Door": "#ff7777",
    "Treasure": "#ffff00",
    "Hole": "#000000",
    "Rail": "#969696"
}

__VERSION__ = 0.1
__AUTHOR__  = "Daniel Nögel"
__NAME__ = "Catacomb Snatch Map Editor"

def rgb2hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def get_file_from_jar(jar):
    tmp = tempfile.mkdtemp(prefix="csnatch.mapedit.", dir="/tmp")
    with zipfile.ZipFile(jar) as zf:
        zf.extract("levels/level1.bmp", tmp)
        return os.path.join(tmp, "levels", "level1.bmp")
    
def save_to_jar(filename, jar):
    with zipfile.ZipFile(jar, "a") as zf:
        zf.write(filename, "levels/level1.bmp")
        #~ return os.path.join(tmp, "levels", "level1.bmp")

def open_file(filetype="bmp"):
    assert filetype in ["bmp", "jar"]
    
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    if filetype == "bmp":
        ffilter=gtk.FileFilter()
        ffilter.set_name("Bitmap files")
        ffilter.add_pattern("*.bmp")
    else:
        ffilter=gtk.FileFilter()
        ffilter.set_name("Java .jar files")
        ffilter.add_pattern("*.jar")
    chooser.add_filter(ffilter)
    chooser.run()
    
    filename =  chooser.get_filename()
    chooser.destroy()
    return filename
    
def save_file(filetype):
    assert filetype in ["bmp", "jar"]
    
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    if filetype == "bmp":
        ffilter=gtk.FileFilter()
        ffilter.set_name("Bitmap files")
        ffilter.add_pattern("*.bmp")
    else:
        ffilter=gtk.FileFilter()
        ffilter.set_name("Java .jar files")
        ffilter.add_pattern("*.jar")
    chooser.add_filter(ffilter)
    chooser.run()
    
    filename =  chooser.get_filename()
    chooser.destroy()
    return filename

class DrawThingy(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.set_events(gtk.gdk.EXPOSURE_MASK
                            | gtk.gdk.LEAVE_NOTIFY_MASK
                            | gtk.gdk.BUTTON_PRESS_MASK
                            | gtk.gdk.POINTER_MOTION_MASK
                            | gtk.gdk.POINTER_MOTION_HINT_MASK )
        self.connect("expose_event", self.expose_event)
        self.connect("configure_event", self.configure_event)
        self.connect("motion_notify_event", self.motion_notify_event)
        self.connect("button_press_event", self.button_press_event)
        self.connect('realize',       self.realize_event)
        
        self.pixmap = None
        self.current_object = "Wall"


        self.points = {}
        for i in xrange(0, SIZE_X):
            self.points[(i, 0)] = TILES["Wall"]
            self.points[(i, SIZE_Y-1)] = TILES["Wall"]
        for i in xrange(0, SIZE_Y):
            self.points[(0, i)] = TILES["Wall"]
            self.points[(SIZE_X-1, i)] = TILES["Wall"]
        for i in [0, 47]:
            self.points[(22, i)] = TILES["Floor"]
            self.points[(23, i)] = TILES["Rail"]
            self.points[(24, i)] = TILES["Floor"]

    def set_object(self, obj):
        self.current_object = obj
        self.set_color(TILES[obj])

    def set_color(self, color):
        #~ self.current_gc = self.pixmap.new_gc()
        self.current_gc.set_foreground(self.get_colormap().alloc_color(color))
        #~ self.current_gc = gc

    def draw_grid(self, da):
        self.current_gc.set_line_attributes(GRID_WIDTH, gtk.gdk.LINE_SOLID,
                                        gtk.gdk.CAP_BUTT, gtk.gdk.JOIN_MITER)
        offset = int(GRID_WIDTH / 2.0)
        self.set_color("#000000")
        for i, x in enumerate(w for w in range(0, WIDTH, (MULTI+GRID_WIDTH))):
            da.window.draw_line(self.current_gc, x+offset, 0, x+offset, WIDTH)
            da.window.draw_line(self.current_gc, 0, x++offset, HEIGHT, x+offset)

    def draw_points(self, da):
        for x, y in self.points:
            self.set_color(self.points[(x, y)])
            da.window.draw_rectangle(self.current_gc, True, x*MULTI+(x+1)*GRID_WIDTH, y*MULTI+(y+1)*GRID_WIDTH, MULTI, MULTI)

            
    def draw_point(self, da, x, y, delete = False):
        real_x, real_y = int(math.floor(x/(MULTI+GRID_WIDTH))), int(math.floor(y/(MULTI+GRID_WIDTH)))
        x, y = real_x*MULTI+(real_x+1)*GRID_WIDTH, real_y*MULTI+(real_y+1)*GRID_WIDTH
        
        if delete:
            tmp = self.current_object
            self.current_object = "Floor"
            self.set_color("#ffffff")
        da.window.draw_rectangle(self.current_gc, True, x, y, MULTI, MULTI)
        #~ da.queue_draw_area(x, y, MULTI, MULTI)
        
        self.points[(real_x, real_y)] = TILES[self.current_object]
        
        if delete:
            self.set_object(tmp)
        
    def realize_event(self, da):
        self.current_gc = da.window.new_gc()
        self.set_color("#000000")
        

    def configure_event(self, da, event):
        #~ x, y, width, height = da.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(da.window, WIDTH, HEIGHT)
        self.pixmap.draw_rectangle(da.get_style().white_gc, True, 0, 0, WIDTH, HEIGHT)
        
        
        return True
    
    def expose_event(self, da, event):
        
        
        x , y, width, height = event.area
        da.window.draw_drawable(self.current_gc, self.pixmap, x, y, x, y, width, height)
        
        
        self.draw_grid(da)
        self.draw_points(da)
        
        return False
        
    def motion_notify_event(self, da, event):
        real_x, real_y = int(math.floor(event.x/(MULTI+GRID_WIDTH))), int(math.floor(event.y/(MULTI+GRID_WIDTH)))
        self.emit("position", real_x, real_y)
        
        if event.state & gtk.gdk.BUTTON1_MASK and self.pixmap:
            self.draw_point(da, event.x, event.y)
        elif event.state & gtk.gdk.BUTTON3_MASK and self.pixmap:
            self.draw_point(da, event.x, event.y, delete=True)
        
        return True
        
    def button_press_event(self, da, event):
        if event.button == 1 and self.pixmap:
            self.draw_point(da, event.x, event.y)
        elif event.button == 3 and self.pixmap:
            self.draw_point(da, event.x, event.y, delete=True)
        
        return True

gobject.type_register(DrawThingy)
gobject.signal_new("position", DrawThingy, gobject.SIGNAL_RUN_FIRST,
                   gobject.TYPE_NONE, (int, int, ))

class App(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title("{0} v{1}".format(__NAME__, __VERSION__))
        self.window.set_size_request(300, 300)
        self.window.set_default_size(640, 480)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        
        table = gtk.Table()
        
        self.window.add(table)
        
        menu = gtk.Menu()
        self.menu_items = {}
        for i in ["Load", "Load from JAR", "---", "Save", "Save to file",  "Save to JAR", "---", "Quit"]:
            if i == "---":
                item = gtk.SeparatorMenuItem()
            else:
                item = gtk.MenuItem(i)
                self.menu_items[i] = item
            item.show()
            item.connect("activate", self.menu_activate_event, i)
            menu.append(item)
        root_menu = gtk.MenuItem("File")
        root_menu.set_submenu(menu)
        root_menu.show()
        
        menu_bar = gtk.MenuBar()
        menu_bar.append (root_menu)
        table.attach(menu_bar, 0, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        menu_bar.show()
        
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.drawing_area = DrawThingy()
        self.drawing_area.set_size_request(WIDTH, HEIGHT)
        self.drawing_area.connect("position", self.position_event)
        sw.add_with_viewport(self.drawing_area)
        
        table.attach(sw, 0, 1, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL)

        
        bb = gtk.VButtonBox()
        for name in TILES:
            b = gtk.Button(name)
            bb.pack_start(b, False, False)
            b.show()
            b.connect("clicked", lambda x,y:self.drawing_area.set_object(y), name)
        table.attach(bb, 1, 2, 1, 2, xoptions=gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL)
        bb.set_layout(gtk.BUTTONBOX_START)
        bb.show()
        
        
        
        #~ bb = gtk.HButtonBox()
        #~ b = gtk.Button(stock=gtk.STOCK_OPEN)
        #~ b.connect("clicked", self.button_press_event, "open")
        #~ bb.pack_start(b)
        #~ b = gtk.Button(stock=gtk.STOCK_SAVE)
        #~ b.connect("clicked", self.button_press_event, "save")
        #~ bb.pack_start(b)
        #~ bb.set_layout(gtk.BUTTONBOX_SPREAD)
        #~ table.attach(bb, 0, 2, 1, 2, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        #~ bb.show_all()
        
        self.statusbar = gtk.Statusbar()
        table.attach(self.statusbar, 0, 2, 2, 3, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.statusbar.show()
        
        self.window.show()
        table.show()
        sw.show()
        self.drawing_area.show()
        
        
        
        
        settings = gtk.settings_get_default()
        settings.props.gtk_button_images = True
        
        self.current_file = None
        
        #~ fl = get_file_from_jar("/home/daniel/behalten/games/mojam.jar")
        #~ self.load(fl, set_filename=False)
    
    @property
    def current_file(self):
        return self._current_file
    @current_file.setter
    def current_file(self, value):
        if not value:
            self.menu_items["Save"].set_sensitive(False)
        else:
            self.menu_items["Save"].set_sensitive(True)
            self._current_file = value
            self.window.set_title("{0} v{1} / {2}".format(__NAME__, __VERSION__,self.current_file))

    #
    # Callbacks
    #
    def menu_activate_event(self, menu, user):
        if user == "Load":
            filename = open_file("bmp")
            if filename:
                self.load(filename)
        elif user == "Save":
            if self.current_file:
                self.save(self.current_file)
        elif user == "Save to file":
            
            filename = save_file("bmp")
            if filename:
                self.save(filename)
        elif user == "Load from JAR":
            filename = open_file("jar")
            if filename:
                fl = get_file_from_jar(filename)
                self.load(fl, set_filename=False)
        elif user == "Save to JAR":
            
            filename = save_file("jar")
            if filename:
                tmp = tempfile.mkstemp(suffix=".bmp", prefix="csnatch.mapedit.", dir="/tmp")[1]
                #~ print tmp
                self.save(tmp)
                
                save_to_jar(tmp, filename)
        elif user == "Quit":
            self.window.destroy()
            
    def position_event(self, obj, x, y):
        context_id = self.statusbar.get_context_id("pos")
        message_id = self.statusbar.push(context_id, "x{0}y{1}".format(x, y))
    
    def button_press_event(self, btn, command):
        if command == "save":
            self.save()
    
    
    
    def save(self, filename=None):
        img = Image.new("RGB", [SIZE_X,SIZE_Y], "white")
        for coords, color in self.drawing_area.points.iteritems():
            img.putpixel(coords,  tuple(ord(c) for c in color[1:].decode('hex')))
        img.save(filename)
        
    def load(self, filename, set_filename=True):
        img = Image.open(filename)
        
        _, _, w, h = img.getbbox()
        
        self.drawing_area.points = {}
        
        img= img.convert("RGB").getdata() 
        x, y = 0, -1
        
        for i, pix in enumerate(img):
            if i % w == 0: #new line
                y+=1
                x=0
            if pix != (255, 255, 255):
                self.drawing_area.points[(x, y)] = rgb2hex(pix)
            x+=1
        
        self.drawing_area.draw_points(self.drawing_area)
        self.drawing_area.queue_draw_area(0, 0, WIDTH, HEIGHT)
        if set_filename:
            self.current_file = filename
        else:
            self.current_file = None




if __name__ == "__main__":
    app = App()
    gtk.main()
