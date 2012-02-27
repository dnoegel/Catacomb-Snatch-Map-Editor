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
            return n.tile  == self.tile
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
        
        pb_floortiles = gtk.gdk.pixbuf_new_from_file(floortiles)
        pb_rails = gtk.gdk.pixbuf_new_from_file(rails)
        pb_treasure_barrier = gtk.gdk.pixbuf_new_from_file(treasure)
        pb_spikes = gtk.gdk.pixbuf_new_from_file(spikes)
        pb_spawner = gtk.gdk.pixbuf_new_from_file(spawner)
        pb_loot = gtk.gdk.pixbuf_new_from_file(loot)
        pb_turret1 = gtk.gdk.pixbuf_new_from_file(turret1)
        pb_dark = gtk.gdk.pixbuf_new_from_file(dark)

        self.positions = {
            ##    offset tilesize   grid             positions
            WALL: (-32, (32, 64), (32, 32), [(0, 3), (1, 3), (2, 3), (3, 3)], pb_floortiles),
            FLOOR: (0, (32, 32), (32, 32), [(0, 0), (1, 0), (2, 0), (3, 0)], pb_floortiles),
            BARRIER: (-24, (32, 56), (32, 56), [(4, 0)], pb_treasure_barrier),
            TREASURE: (-24, (32, 56), (32, 56), [(0, 0)], pb_treasure_barrier),
            HOLE: (0, (32, 32), (32, 32), [(4, 0)], pb_floortiles),
            RAIL: (0, (32, 32), (32, 38), [(i, 0) for i in xrange(0, 7)], pb_rails),
            SPIKES: (0, (32, 32), (32, 32),[(i, 0) for i in xrange(0, 4)], pb_spikes),
            
            BAT_SPAWNER: (-8, (32, 40), (32, 40),[(0, 0)], pb_spawner),
            SNAKE_SPAWNER: (-8, (32, 40), (32, 40), [(0, 0)], pb_spawner),
            MUMMY_SPAWNER:(-8, (32, 40), (32, 40), [(0, 0)], pb_spawner),
            SCARAB_SPAWNER: (-8, (32, 40), (32, 40), [(0, 0)], pb_spawner),
            
            TEAM1_TURRET: (0, (32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            TEAM2_TURRET: (0, (32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            NEUTRAL_TURRET: (0, (32, 32), (32, 32), [(i, 0) for i in xrange(0, 8)], pb_turret1),
            
            LOOT: (0, (24, 24), (24, 24), [(i, 0) for i in xrange(0, 14)], pb_loot),
            "DARK": (0, (32, 32), (32, 32), [(1, 1)], pb_dark),
        }
        self.settings = settings
        self.set_default_map()
        
    def set_default_map(self):
        self.points = {}
        ## Floors
        for x in range(0, self.settings.SIZE_X):
            for y in range(0, self.settings.SIZE_Y):
                self.place_tile(FLOOR, x, y)
        ## Top and bottom walls
        for i in xrange(0, self.settings.SIZE_X):
            self.place_tile(WALL, i, 0)
            self.place_tile(WALL, i, self.settings.SIZE_Y-1)
        ## left and right walls
        for i in xrange(0, self.settings.SIZE_Y):
            self.place_tile(WALL, self.settings.SIZE_X-1, i)
            self.place_tile(WALL, 0, i)
        ## starting points
        for i in [0, (self.settings.SIZE_Y-1)]:
            self.place_tile(FLOOR, 22, i)
            self.place_tile(RAIL, 23, i)
            self.place_tile(FLOOR, 24, i)
        
        
    def place_tile(self, tile, x, y):
        tile_obj = self.points.get((x,y), None)
        if not tile_obj:
            tile_obj = Tile(self, tile, x, y)
            self.points[(x, y)] = tile_obj
        else:
            tile_obj.tile = tile
            tile_obj.color = TILES[tile]
        
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
        offset, tilesize, grid, positions, pb =  self.positions[tile.tile]
        
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
                offset, tilesize, grid, positions, pb =  self.positions["DARK"]
                position = positions[0]
        x = tilesize[0]/float(w)
        h = int(tilesize[1]/x)

        if offset != 0: offset = int(offset/x)
        
        #~ offset = 1s
        
        pb = pb.subpixbuf(grid[0]*position[0], grid[1]*position[1], tilesize[0], tilesize[1])
        pb = pb.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR)
        
        #~ pm = gtk.gdk.Pixmap(self.drawingarea.window, pb.get_width(), pb.get_height())
        #~ pm.draw_pixbuf(self.drawingarea.current_gc, pb, 0, 0, 0, 0)
        return offset, pb