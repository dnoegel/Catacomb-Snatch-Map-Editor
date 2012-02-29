# coding: utf-8

import os
import gtk
import zipfile
import tempfile


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
    ret = chooser.run()
    
    if ret != gtk.RESPONSE_OK:
        chooser.destroy()
        return None
    
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
    ret = chooser.run()
    
    if ret == gtk.RESPONSE_CANCEL:
        chooser.destroy()
        return None
    
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

class ImageButton(gtk.Button):
    def __init__(self, pb, text,):
        gtk.Button.__init__(self)
        
        bb = gtk.HBox()
        bb.set_spacing(10)
        
        self.lbl = gtk.Label(text)
        self.img = gtk.Image()

        bb.pack_start(self.img, False, False)
        bb.pack_start(self.lbl, True, True)
        
        self.add(bb)
        
        self.setimage(pb)
        self.show_all()
        
    def setimage(self, pb):
        self.img.set_from_pixbuf(pb)
        #~ self.set_image(self.img)
