# coding: utf-8

import os
import gobject
import gtk
import zipfile
import tempfile

import csnatch_editor_modules
import csnatch_editor_modules.settings
import csnatch_editor_modules.drawingarea
import csnatch_editor_modules.gui_helpers
import csnatch_editor_modules.tiles

from csnatch_editor_modules import TILES, TILE_NAMES, COLORS

from PIL import Image


## Out main class
class GUI(object):
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title("{0} v{1}".format(csnatch_editor_modules.__NAME__, csnatch_editor_modules.__VERSION__))
        self.window.set_size_request(300, 300)
        self.window.set_default_size(640, 480)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        
        self.settings = csnatch_editor_modules.settings.Settings()
        #~ self.settings.MULTI=3
        self.table = gtk.Table()
        
        self.window.add(self.table)
        
        self.accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self.accel_group)
        
        self.create_menues()
        
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
        #~ self.table.attach(hbox, 0, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.SHRINK)
        
        
        
        #
        # SW
        #
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.drawing_area = csnatch_editor_modules.drawingarea.DrawThingy(self.settings, self)
        self.drawing_area.set_size_request(self.settings.WIDTH, self.settings.HEIGHT)
        self.drawing_area.connect("position", self.position_event)
        self.drawing_area.connect("changed", self.changed_event)
        self.sw.add_with_viewport(self.drawing_area)
        
        self.table.attach(self.sw, 0, 1, 2, 4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL)
        
        #
        # Tiles
        #
        sw2 =  gtk.ScrolledWindow()
        sw2.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        t = csnatch_editor_modules.tiles.Tiles(self.settings)
        bb = gtk.VButtonBox()
        for tile in TILES:
            name = TILE_NAMES[tile]
            tile_obj = t.fake_tile(tile, 20, 20)
            b = csnatch_editor_modules.gui_helpers.ImageButton(tile_obj.pixbuf, name)
            #~ b.set_image_position(gtk.POS_TOP)
            #~ b.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(TILES[tile]))
            #~ if TILES[tile]  == "#000000":
                #~ lbl =  b.get_children()[0]
                #~ lbl.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
            bb.pack_start(b, False, False)
            b.show()
            b.connect("clicked", lambda x,y:self.drawing_area.set_object(y), tile)
        #~ bb.set_spacing(10)
        sw2.add_with_viewport(bb)
        self.table.attach(sw2, 1, 2, 2, 3, xoptions=gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL)
        bb.set_layout(gtk.BUTTONBOX_START)
        sw2.show()
        bb.show()

        self.image = gtk.Image()
        self.table.attach(self.image, 1, 2, 3, 4, xoptions=gtk.SHRINK, yoptions=gtk.SHRINK)
        if self.settings.show_thumbnail:
            self.image.show()
        self.lock_thumbnail = False
        #~ self.image.set_size_request(300,200)
        
        self.statusbar = gtk.Statusbar()
        self.table.attach(self.statusbar, 0, 2, 4, 5, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        self.statusbar.show()
        
        self.window.show()
        self.table.show()
        self.sw.show()
        self.drawing_area.show()
        

        settings = gtk.settings_get_default()
        settings.props.gtk_button_images = True
        
        self.current_file = None
        self.create_thumbnail()
    
    def create_menues(self):
        #
        # Menu
        #
        menu = gtk.Menu()
        self.menu_items = {}
        accelerators = [None, None, "<Control>O", None, None, "<Control>S", "<Control><Shift>S", None, None, "<Control>Q"]
        for idx, i in enumerate(["Clear map", "---", "Load", "Load from JAR", "---", "Save", "Save to file",  "Save to JAR", "---", "Quit"]):
            if i == "---":
                item = gtk.SeparatorMenuItem()
            else:
                item = gtk.MenuItem(i)
                self.menu_items[i] = item
            acc = accelerators[idx]
            if acc:
                key, mod = gtk.accelerator_parse(acc)
                item.add_accelerator("activate", self.accel_group, key, mod, gtk.ACCEL_VISIBLE)
            item.show()
            item.connect("activate", self.menu_activate_event, i)
            menu.append(item)
        file_menu = gtk.MenuItem("File")
        file_menu.set_submenu(menu)
        file_menu.show()
        
        
        def toggled_menu(item, mnu):
            if mnu == "border":
                self.settings.allow_modifying_borders = item.get_active()
            elif mnu == "thumb":
                if item.get_active():
                    self.image.show()
                else:
                    self.image.hide()
                self.settings.show_thumbnail = item.get_active()
        
        menu = gtk.Menu()
        # border
        item = gtk.CheckMenuItem("Allow modifying the borders")
        item.set_active(self.settings.allow_modifying_borders)
        item.show()
        item.connect("toggled", toggled_menu, "border")
        menu.append(item)
        # thumbnail
        item = gtk.CheckMenuItem("Show thumbnail")
        item.set_active(self.settings.show_thumbnail)
        item.show()
        item.connect("toggled", toggled_menu, "thumb")
        menu.append(item)
        preferences_menu = gtk.MenuItem("Preferences")
        preferences_menu.set_submenu(menu)
        preferences_menu.show()
        
        menu_bar = gtk.MenuBar()
        menu_bar.append (file_menu)
        menu_bar.append (preferences_menu)
        self.table.attach(menu_bar, 0, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.SHRINK)
        menu_bar.show()
        
        
    
    @property
    def current_file(self):
        return self._current_file
    @current_file.setter
    def current_file(self, value):
        if not value:
            self.menu_items["Save"].set_sensitive(False)
            self.window.set_title("{0} v{1}".format(csnatch_editor_modules.__NAME__, csnatch_editor_modules.__VERSION__))
        else:
            self.menu_items["Save"].set_sensitive(True)
            self._current_file = value
            self.window.set_title("{0} v{1} - {2}".format(csnatch_editor_modules.__NAME__, csnatch_editor_modules.__VERSION__,self.current_file))

    ## Save a bitmap to a given file
    def save(self, filename=None, set_filename=True):
        img = Image.new("RGB", [self.settings.SIZE_X,self.settings.SIZE_Y], "white")
        for coords, tile in self.drawing_area.tiles.points.iteritems():
            try:
                img.putpixel(coords,  tuple(ord(c) for c in tile.color[1:].decode('hex')))
            except IndexError:
                print coords, tile.color
                raise
        img.save(filename)
        if set_filename:
            self.current_file = filename
    
    
    ## Load a bitmap from a given file
    def load(self, filename, set_filename=True):
        img = Image.open(filename)
        
        _, _, w, h = img.getbbox()
        
        self.drawing_area.points = {}
        
        self.settings.SIZE_X = w
        self.settings.SIZE_Y = h
        
        img= img.convert("RGB").getdata() 
        x, y = 0, -1
        
        for i, pix in enumerate(img):
            if i % w == 0: #new line
                y+=1
                x=0
            #~ if pix != (255, 255, 255):
            hex_color = csnatch_editor_modules.gui_helpers.rgb2hex(pix)
            try:
                tile = COLORS[hex_color]
                self.drawing_area.tiles.place_tile(tile, x, y)
            except KeyError:
                print "Ignoring unknown tile {0}".format(hex_color)
            
            x+=1
        
        self.drawing_area.draw_points(self.drawing_area)
        #~ self.drawing_area.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
        if set_filename:
            self.current_file = filename
        else:
            self.current_file = None
            
        self.create_thumbnail()


    #
    # Callbacks
    #
    
    ## Some menu events
    def menu_activate_event(self, menu, user):
        if user == "Load":
            filename = csnatch_editor_modules.gui_helpers.open_file("bmp", self.settings.last_load_dir)
            if filename:
                self.settings.last_load_dir = os.path.dirname(filename)
                self.load(filename)
        elif user == "Save":
            if self.current_file:
                self.save(self.current_file)
        elif user == "Save to file":
            
            filename = csnatch_editor_modules.gui_helpers.save_file("bmp", self.settings.last_save_dir)
            if filename:
                self.settings.last_save_dir = os.path.dirname(filename)
                self.save(filename)
        elif user == "Load from JAR":
            filename = csnatch_editor_modules.gui_helpers.open_file("jar")
            if filename:
                fl = csnatch_editor_modules.gui_helpers.get_file_from_jar(filename)
                if fl:
                    self.load(fl, set_filename=False)
        elif user == "Save to JAR":
            
            filename = csnatch_editor_modules.gui_helpers.save_file("jar")
            if filename:
                tmp = tempfile.mkstemp(suffix=".bmp", prefix="csnatch.mapedit.", dir="/tmp")[1]
                #~ print tmp
                self.save(tmp, set_filename=False)
                
                if self.settings.multi_level_support:
                    csnatch_editor_modules.gui_helpers.save_to_jar(tmp, filename, self.level_name.get_text())
                else:
                    csnatch_editor_modules.gui_helpers.save_to_jar(tmp, filename)
        elif user == "Quit":
            self.window.destroy()
        elif user == "Clear map":
            dia = csnatch_editor_modules.gui_helpers.NewLevelDialog()
            result = dia.run()
            if result == gtk.RESPONSE_OK:
                w = int(dia.spin_width.get_value())
                h = int(dia.spin_height.get_value())
                dia.destroy()
                self.settings.SIZE_X = w
                self.settings.SIZE_Y = h
                self.drawing_area.tiles.set_default_map()
                self.drawing_area.queue_draw_area(0, 0, self.settings.WIDTH, self.settings.HEIGHT)
                self.current_file = None
            else:
                dia.destroy()
                return

    def changed_event(self, obj):
        if self.lock_thumbnail or not self.settings.show_thumbnail: return
        gobject.idle_add(self.create_thumbnail)
        self.lock_thumbnail = True
        
    def unlock_thumbnail(self):
        self.lock_thumbnail = False
        return False

    ## Show the current coords
    def position_event(self, obj, x, y):
        try:
            tile_name = TILE_NAMES[self.drawing_area.tiles.points[(x,y)].tile]
        except KeyError:
            tile_name = ""
        context_id = self.statusbar.get_context_id("pos")
        message_id = self.statusbar.push(context_id, "x{0}y{1}    | Size: {2}x{3}    |    Zoom: {4}    |    Tile under mouse: {5}".format(x, y, self.settings.SIZE_X, self.settings.SIZE_Y, self.settings.MULTI, tile_name))
    
    def create_thumbnail(self):
        print "drawing thumbnail"
        w, h =  self.settings.SIZE_X, self.settings.SIZE_Y
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
        pixmap,mask = pixbuf.render_pixmap_and_mask()
        cm = pixmap.get_colormap()
        for x in xrange(0, w):
            for y in xrange(0, h):
                color = self.drawing_area.tiles.points[(x, y)].color
                gc = pixmap.new_gc(foreground=cm.alloc_color(color))
                pixmap.draw_point(gc, x, y)
        pixbuf.get_from_drawable(pixmap,cm,0,0,0,0,w,h)
        pixbuf = pixbuf.scale_simple(200 ,200, gtk.gdk.INTERP_NEAREST)
        self.image.set_from_pixbuf(pixbuf)
        
        gobject.timeout_add(500, self.unlock_thumbnail)
    
