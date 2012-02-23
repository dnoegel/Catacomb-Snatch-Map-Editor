# coding: utf-8

import os

from xdg import BaseDirectory
import pickle


## Stores some basic settings
# MULTI: Zoom-level
# SIZE_X, SIZE_Y: Width and height of the actual 1px map
# GRID_WIDTH: width of the grid
# WIDTH and HEIGHT (properties): actual dimensions of the image
class Settings(dict):
    config_path =  os.path.join(BaseDirectory.xdg_config_home, "csnatch-editor")
    
    def __init__(self):
        dict.__init__(self)
        
        if os.path.exists(Settings.config_path):
            with open(Settings.config_path) as fh:
                try:
                    d = pickle.loads(fh.read())
                    for key, value in d.iteritems():
                        dict.__setitem__(self, key, value)
                        print "Setting", key, "to", value
                except EOFError:
                    print "Config empty"
        else:
            print "No config file found"
        
        for setting in [
            ("MULTI", 15),
            ("SIZE_X", 48),
            ("SIZE_Y", 48),
            ("GRID_WIDTH", 1),
            ("multi_level_support", False),
            ("last_save_dir", os.path.expanduser("~/.mojam/levels")),
            ("last_load_dir", os.path.expanduser("~/.mojam/levels")),
            ("allow_modifying_borders", False)]:
            key, value = setting
            if dict.get(self, key, None) is None: 
                dict.__setitem__(self, key, value)
        
   
    ## Wrap attributes to dict-items
    def __getattribute__(self, atr):
        return self[atr]
    
    def __setattr__(self, atr, value):
        self[atr] = value
    
    ## Actual logic should be inserted here
    def __getitem__(self, key):
        if key == "WIDTH": return self.MULTI*self.SIZE_X+(self.SIZE_X+1)*self.GRID_WIDTH
        if key == "HEIGHT": return self.MULTI*self.SIZE_Y+(self.SIZE_Y+1)*self.GRID_WIDTH
        val = dict.__getitem__(self, key)
        return val
        
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        
        print "Writing config"
        print self
        with open(Settings.config_path, "w") as fh:
            tmpd = {}
            for key, value in dict.iteritems(self):
                tmpd[key] = value
            pickled_dict = pickle.dumps(tmpd)
            fh.write(pickled_dict)
