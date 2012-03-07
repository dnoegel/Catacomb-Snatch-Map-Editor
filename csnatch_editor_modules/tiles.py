# coding: utf-8

import gtk
import os
import sys

import random
from csnatch_editor_modules import *




class Tile(object):
    def __init__(self, tile_manager, tile, x, y):
        self.x = x
        self.y = y
        
        self.tile = tile
        self.color = TILES[tile]
        
        self.tiles = tile_manager
        
        self.offset = None
        self.pixbuf = None

    def get_neighbour(self, position):
        offset_x, offset_y = NEIGHBOUR_TILES[position]
        return self.tiles.points.get((self.x+offset_x, self.y+offset_y), None)
    
    def check_neighbour(self, position, tile):
        offset_x, offset_y = NEIGHBOUR_TILES[position]
        n = self.tiles.points.get((self.x+offset_x, self.y+offset_y), None)
        if n:
            return n.tile  == tile
        return False
        

"""
Rails:
  1
2   4
  8   #
"""
class Tiles(object):
    def __init__(self, settings):
        self.path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "map")

        treasure = os.path.join(self.path, "treasure.png")
        floortiles = os.path.join(self.path, "floortiles.png")
        rails = os.path.join(self.path, "rails.png")
        spikes = os.path.join(self.path, "spike_trap_eglerion_32.png")
        spawner = os.path.join(self.path, "spawner.png")
        loot = os.path.join(self.path, "pickup_gem_diamond_24.png")
        turret1 = os.path.join(self.path, "turret.png")
        dark = os.path.join(self.path, "dark.png")
        droptrap  = os.path.join(self.path, "droptrap.png")
        chest  = os.path.join(self.path, "chest_small.png")
        pharao  = os.path.join(self.path, "enemy_pharao_anim_48.png")
        
        
        pb_floortiles = gtk.gdk.pixbuf_new_from_file(floortiles)
        pb_rails = gtk.gdk.pixbuf_new_from_file(rails)
        pb_treasure_barrier = gtk.gdk.pixbuf_new_from_file(treasure)
        pb_spikes = gtk.gdk.pixbuf_new_from_file(spikes)
        pb_spawner = gtk.gdk.pixbuf_new_from_file(spawner)
        pb_loot = gtk.gdk.pixbuf_new_from_file(loot)
        pb_turret1 = gtk.gdk.pixbuf_new_from_file(turret1)
        pb_dark = gtk.gdk.pixbuf_new_from_file(dark)

        pb_droptrap = gtk.gdk.pixbuf_new_from_file(droptrap)
        pb_chest = gtk.gdk.pixbuf_new_from_file(chest)
        
        pb_pharao = gtk.gdk.pixbuf_new_from_file(pharao)

        self.positions = {
            ##    tilesize   grid             positions
            WALL: ( (32, 64), (32, 32), [(0, 3), (1, 3), (2, 3), (3, 3)], pb_floortiles),
            FLOOR: ( (32, 32), (32, 32), [(0, 0), (1, 0), (2, 0), (3, 0)], pb_floortiles),
            BARRIER: ( (32, 56), (32, 56), [(4, 0)], pb_treasure_barrier),
            TREASURE: ( (32, 56), (32, 56), [(0, 0)], pb_treasure_barrier),
            HOLE: ( (32, 32), (32, 32), [(4, 0)], pb_floortiles),
            RAIL: ((32, 32), (32, 38), [(i, 0) for i in xrange(0, 7)], pb_rails),
            SPIKES: ((32, 32), (32, 32),[(i, 0) for i in xrange(0, 4)], pb_spikes),
            
            BAT_SPAWNER: ((32, 40), (32, 40),[(0, 0)], pb_spawner),
            SNAKE_SPAWNER: ((32, 40), (32, 40), [(0, 0)], pb_spawner),
            MUMMY_SPAWNER:((32, 40), (32, 40), [(0, 0)], pb_spawner),
            SCARAB_SPAWNER: ((32, 40), (32, 40), [(0, 0)], pb_spawner),
            
            TEAM1_TURRET: ((32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            TEAM2_TURRET: ((32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            NEUTRAL_TURRET: ((32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            
            LOOT: ((24, 24), (24, 24), [(i, 0) for i in xrange(0, 14)], pb_loot),
            SAND: ((32, 32), (32, 32), [(5, 0)], pb_floortiles),
            UNPASSABLE_SAND: ((32, 32), (32, 32), [(6, 0)], pb_floortiles),
            
            DROP_TRAP: ((32, 32), (32, 32), [(3, 0)], pb_droptrap),
            CHEST: ((32, 53), (32, 53), [(1, 0)], pb_chest),
            
            PHARAO: ((48, 48), (48, 48), [(i, 3) for i in xrange(0,4)], pb_pharao), 
            
            "DARK": ((32, 32), (32, 32), [(1, 1)], pb_dark),
            "SAND_TOP": ((32, 32), (32, 32), [(4, 1)], pb_floortiles),
            "SAND_BOTTOM": ((32, 32), (32, 32), [(5, 1)], pb_floortiles),
        }
        self.settings = settings
        self.set_default_map()
        
    def set_default_map(self):
        self.points = {}
        ## Floors
        for x in range(0, self.settings.SIZE_X):
            for y in range(0, self.settings.SIZE_Y):
                self.place_tile(FLOOR, x, y, True)
        ## Top and bottom walls
        for i in xrange(0, self.settings.SIZE_X):
            self.place_tile(WALL, i, 0, True)
            self.place_tile(WALL, i, self.settings.SIZE_Y-1, True)
        ## left and right walls
        for i in xrange(0, self.settings.SIZE_Y):
            self.place_tile(WALL, self.settings.SIZE_X-1, i, True)
            self.place_tile(WALL, 0, i, True)
            
        ## starting points
        start = int(self.settings.SIZE_X / 2)-2
        for i in [0, (self.settings.SIZE_Y-1)]:
            self.place_tile(FLOOR, start, i, True)
            self.place_tile(RAIL, start+1, i, True)
            self.place_tile(FLOOR, start+2, i, True)
        print "done"
        
    def place_tile(self, tile, x, y, lazy=False):
        tile_obj = self.points.get((x,y), None)
        if not tile_obj:
            tile_obj = Tile(self, tile, x, y)
            self.points[(x, y)] = tile_obj
        else:
            tile_obj.tile = tile
            tile_obj.color = TILES[tile]

        if not lazy:
            offset, pb = self.__get_tile_graphics(tile_obj, self.settings.MULTI, self.settings.MULTI)
            tile_obj.offset = offset
            tile_obj.pixbuf = pb
        
        return tile_obj
                
    def fake_tile(self, tile, w, h):
        tile_obj = Tile(self, tile, 0, 0)

        
        offset, pb = self.__get_tile_graphics(tile_obj, w, h)
        tile_obj.offset = offset
        tile_obj.pixbuf = pb
        
        return tile_obj
    
    def __get_tile_graphics(self, tile, w, h):
        tilesize, grid, positions, pb =  self.positions[tile.tile]

        position = random.choice(positions)
        
        if tile.tile == RAIL:
            surrounding = 0
            values = [1, 2, 4, 8]
            for pos in (TOP, LEFT, RIGHT, BOTTOM):
                
                if tile.check_neighbour(pos, tile.tile):
                    surrounding += values[pos]
                

            if surrounding in [1, 9, 0, 8, None]: position = 1
            if surrounding in [2, 4, 6]: position = 0
            if surrounding == 12: position = 2
            if surrounding == 10: position = 3
            if surrounding == 5: position = 4
            if surrounding == 3: position = 5
            if surrounding in [15, 7, 11, 13, 14]: position = 6
            position = (position, 0)
        elif tile.tile == HOLE:
            if tile.check_neighbour(TOP, tile.tile):
                tilesize, grid, positions, pb =  self.positions["DARK"]
                position = positions[0]
        elif tile.tile == FLOOR:
            ## Fix: If bot is true, only bottom tile will be shown
            if tile.check_neighbour(TOP, SAND) or tile.check_neighbour(TOP, UNPASSABLE_SAND):
                tilesize, grid, positions, pb =  self.positions["SAND_TOP"]
                position = positions[0]
            if tile.check_neighbour(BOTTOM, SAND) or tile.check_neighbour(BOTTOM, UNPASSABLE_SAND):
                tilesize, grid, positions, pb =  self.positions["SAND_BOTTOM"]
                position = positions[0]

        if tilesize[1]>32 and tile.tile != PHARAO:
            offset = 32-tilesize[1]
        else:
            offset = 0

        x = tilesize[0]/float(w)
        h = int(tilesize[1]/x)

        if offset != 0: offset = int(offset/x)
        
        #~ offset = 1s
        
        pb = pb.subpixbuf(grid[0]*position[0], grid[1]*position[1], tilesize[0], tilesize[1])
        pb = pb.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        
        #~ pm = gtk.gdk.Pixmap(self.drawingarea.window, pb.get_width(), pb.get_height())
        #~ pm.draw_pixbuf(self.drawingarea.current_gc, pb, 0, 0, 0, 0)
        return offset, pb
