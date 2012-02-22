#!/usr/bin/env python
# coding: utf-8

import os
import gtk
import math
import gobject
import zipfile
import tempfile

from PIL import Image

__VERSION__ = 0.1
__AUTHOR__  = "Daniel Nögel"
__NAME__ = "Catacomb Snatch Map Editor"

## Stores some basic settings
# MULTI: Zoom-level
# SIZE_X, SIZE_Y: Width and height of the actual 1px map
# GRID_WIDTH: width of the grid
# WIDTH and HEIGHT (properties): actual dimensions of the image
class Settings(object):
    def __init__(self):
        self.MULTI = 15
        self.SIZE_X = 48
        self.SIZE_Y = 48

        self.GRID_WIDTH = 1

        self.multi_level_support = False
        
        self.last_save_dir = os.path.expanduser("~/.mojam/levels")
        self.last_load_dir = os.path.expanduser("~/.mojam/levels")

        #~ self._WIDTH = self.MULTI*self.SIZE_X+(self.SIZE_X+1)*self.GRID_WIDTH
        #~ self._HEIGHT = self.MULTI*self.SIZE_Y+(self.SIZE_Y+1)*self.GRID_WIDTH
        
    @property
    def WIDTH(self):
        return self.MULTI*self.SIZE_X+(self.SIZE_X+1)*self.GRID_WIDTH
    
    @property
    def HEIGHT(self):
        return self.MULTI*self.SIZE_Y+(self.SIZE_Y+1)*self.GRID_WIDTH

## Pre-defined tiles and their colors
TILES = {
    "Wall": "#ff0000",
    "Floor": "#ffffff",
    "Barrier": "#ff7777",
    "Treasure": "#ffff00",
    "Hole": "#000000",
    "Rail": "#969696"
}


def rgb2hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

## Extract level1.bmp from .jar
def get_file_from_jar(jar):
    
    
    tmp = tempfile.mkdtemp(prefix="csnatch.mapedit.", dir="/tmp")
    with zipfile.ZipFile(jar) as zf:
        

        
        
        levels = [m for m in zf.namelist() if m.startswith("levels/") and m.endswith(".bmp")]
        for n in levels[:]:
            while levels.count(n) > 1:
                levels.remove(n)
                
        for level in levels:
            zf.extract(level, tmp)
        
        extracted_levels =  [os.path.join(tmp, "levels", l) for l in os.listdir(os.path.join(tmp, "levels"))]

        if len(extracted_levels) == 1:
            return extracted_levels[0]

        l = LevelChooser(extracted_levels)
        if l.run() == gtk.RESPONSE_OK:
            level = l.levels[l.current_image]
            l.destroy()
            return level
        else:
            l.destroy()
        
        
    
        

## Put level1.bmp into .jar
def save_to_jar(filename, jar, level="level1.bmp"):
    if not level.endswith(".bmp"): level = "{0}.bmp".format(level)
    print filename, jar, level
    with zipfile.ZipFile(jar, "a") as zf:
        zf.write(filename, "levels/{0}".format(level))
        #~ return os.path.join(tmp, "levels", "level1.bmp")

## Show file dialog
def open_file(filetype="bmp", directory=None):
    assert filetype in ["bmp", "jar"]
    
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
                                  
    if directory and os.path.exists(directory):
        chooser.set_current_folder(directory)
        
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

## Show file dialog
def save_file(filetype, directory=None):
    assert filetype in ["bmp", "jar"]
    
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    if directory and os.path.exists(directory):
        chooser.set_current_folder(directory)


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
    if filename and not filename.endswith(".bmp") and filetype == "bmp":
        return "{0}.bmp".format(filename)
    return filename

class LevelChooser(gtk.Dialog):
    def __init__(self, levels):
        gtk.Dialog.__init__(self)
        
        self.current_image = 0
        self.levels = levels

        self.set_modal(True)
        self.set_resizable(False)

        vbox = gtk.VBox()
        self.vbox.pack_start(vbox, False, True)
        vbox.show()
        
        lbl = gtk.Label("Please select the level you want to edit\n")
        vbox.pack_start(lbl, False, True)
        
        self.label = gtk.Label("")
        vbox.pack_start(self.label, False, True)
        self.image = gtk.Image()
        vbox.pack_start(self.image, False, True)
        
            
        
        bb = gtk.HButtonBox()
        btn1 = gtk.Button(stock=gtk.STOCK_GO_BACK)
        btn2 = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        btn1.connect("clicked", self.btn_clicked, "<")
        btn2.connect("clicked", self.btn_clicked, ">")
        bb.set_layout(gtk.BUTTONBOX_EDGE)
        bb.pack_start(btn1)
        bb.pack_start(btn2)
        vbox.pack_start(bb, False, True)


        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        
        self.set_image(self.levels[0])
        self.show_all()
    
    def set_image(self, img):
        pb = gtk.gdk.pixbuf_new_from_file_at_size(img, 240, 240)
        self.image.set_from_pixbuf(pb)
        self.label.set_text(os.path.basename(img))
        self.set_title("Level {0}/{1}".format(self.current_image+1, len(self.levels)))

    def btn_clicked(self, btn, user):
        if user == "<":
            if self.current_image == 0: 
                self.current_image = len(self.levels)-1
            else:
                self.current_image -= 1
        elif user == ">":
            if self.current_image >= len(self.levels)-1:
                self.current_image = 0
            else:
                self.current_image += 1
        self.set_image(self.levels[self.current_image])


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
        
        if real_x >= self.settings.SIZE_X or real_y >= self.settings.SIZE_Y: return
        
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

## Out main class
class App(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title("{0} v{1}".format(__NAME__, __VERSION__))
        self.window.set_size_request(300, 300)
        self.window.set_default_size(640, 480)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        
        self.settings = Settings()
        #~ self.settings.MULTI=3
        table = gtk.Table()
        
        self.window.add(table)
        
        
        #
        # Menu
        #
        menu = gtk.Menu()
        self.menu_items = {}
        for i in ["Clear map", "---", "Load", "Load from JAR", "---", "Save", "Save to file",  "Save to JAR", "---", "Quit"]:
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
        
        #
        # Check
        #
        #~ hbox = gtk.HBox()
        #~ check = gtk.CheckButton("Enable multi-level support")
        #~ check.set_tooltip_text("Not available for the original Catacomb Snatch version made by Mojang")
        #~ hbox.pack_start(check, False, True)
        #~ check.show()
        #~ 
        #~ self.level_name = gtk.Entry()
        #~ self.level_name.set_text("asd")
        #~ hbox.pack_end(self.level_name, False, True)
        #~ lbl_level_name = gtk.Label("Level name: ")
        #~ hbox.pack_end(lbl_level_name, False, True)
#~ 
        #~ def toggle_event(widget):
            #~ active = widget.get_active()
            #~ self.settings.multi_level_support = active
            #~ if active:
                #~ lbl_level_name.show()
                #~ self.level_name.show()
            #~ else:
                #~ lbl_level_name.hide()
                #~ self.level_name.hide()
        #~ check.connect("toggled", toggle_event)
        #~ 
        #~ hbox.show()
        #~ table.attach(hbox, 0, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.SHRINK)
        
        
        
        #
        # SW
        #
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.drawing_area = DrawThingy(self.settings, self)
        self.drawing_area.set_size_request(self.settings.WIDTH, self.settings.HEIGHT)
        self.drawing_area.connect("position", self.position_event)
        self.sw.add_with_viewport(self.drawing_area)
        
        table.attach(self.sw, 0, 1, 2, 3, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL)
        
        #
        # Tiles
        #
        bb = gtk.VButtonBox()
        for name in sorted(TILES.keys()):
            b = gtk.Button(name)
            b.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(TILES[name]))
            if TILES[name]  == "#000000":
                lbl =  b.get_children()[0]
                lbl.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
            bb.pack_start(b, False, False)
            b.show()
            b.connect("clicked", lambda x,y:self.drawing_area.set_object(y), name)
        bb.set_spacing(10)
        table.attach(bb, 1, 2, 2, 3, xoptions=gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL)
        bb.set_layout(gtk.BUTTONBOX_START)
        bb.show()

        
        self.statusbar = gtk.Statusbar()
        table.attach(self.statusbar, 0, 2, 3, 4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.statusbar.show()
        
        self.window.show()
        table.show()
        self.sw.show()
        self.drawing_area.show()
        

        settings = gtk.settings_get_default()
        settings.props.gtk_button_images = True
        
        self.current_file = None
        
    
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

    ## Save a bitmap to a given file
    def save(self, filename=None, set_filename=True):
        img = Image.new("RGB", [self.settings.SIZE_X,self.settings.SIZE_Y], "white")
        for coords, color in self.drawing_area.points.iteritems():
            img.putpixel(coords,  tuple(ord(c) for c in color[1:].decode('hex')))
        img.save(filename)
        if set_filename:
            self.current_file = filename
    
    
    ## Load a bitmap from a given file
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
        self.drawing_area.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        if set_filename:
            self.current_file = filename
        else:
            self.current_file = None


    #
    # Callbacks
    #
    
    ## Some menu events
    def menu_activate_event(self, menu, user):
        if user == "Load":
            filename = open_file("bmp", self.settings.last_load_dir)
            if filename:
                self.settings.last_load_dir = os.path.dirname(filename)
                self.load(filename)
        elif user == "Save":
            if self.current_file:
                self.save(self.current_file)
        elif user == "Save to file":
            
            filename = save_file("bmp", self.settings.last_save_dir)
            if filename:
                self.settings.last_save_dir = os.path.dirname(filename)
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
                self.save(tmp, set_filename=False)
                
                if self.settings.multi_level_support:
                    save_to_jar(tmp, filename, self.level_name.get_text())
                else:
                    save_to_jar(tmp, filename)
        elif user == "Quit":
            self.window.destroy()
        elif user == "Clear map":
            self.drawing_area.set_default_map()
            self.drawing_area.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)

    ## Show the current coords
    def position_event(self, obj, x, y):
        context_id = self.statusbar.get_context_id("pos")
        message_id = self.statusbar.push(context_id, "x{0}y{1}".format(x, y))
    
    




if __name__ == "__main__":
    app = App()
    gtk.main()
