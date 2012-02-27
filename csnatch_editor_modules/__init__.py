# coding: utf-8

__VERSION__ = 0.2
__AUTHOR__  = "Daniel Nögel"
__NAME__ = "Catacomb Snatch Map Editor"

## Pre-defined tiles and their colors


## TILES
(
 WALL,
 FLOOR,
 BARRIER,
 TREASURE,
 HOLE,
 RAIL,
 SPIKES,
 BAT_SPAWNER,
 SNAKE_SPAWNER,
 MUMMY_SPAWNER,
 SCARAB_SPAWNER
) = range(11)

## These tiles will need a special treatment when placed
BIG_TILES = [WALL, BARRIER, TREASURE, BAT_SPAWNER, SNAKE_SPAWNER, MUMMY_SPAWNER, SCARAB_SPAWNER]
## Transparent tiles; blit some ground first
NEED_GROUND = [RAIL, SPIKES, BAT_SPAWNER, SNAKE_SPAWNER, MUMMY_SPAWNER, SCARAB_SPAWNER]
## Names for the tiles
TILE_NAMES = ["Wall", "Floor", "Barrier", "Treasure", "Hole", "Rail", "Spike Trap", "Bat spawner", "Snake spawner", "Mummy spawner", "Scarab spawner"]

## Tiles2Color
TILES = {
    WALL: "#ff0000",
    FLOOR: "#ffffff",
    BARRIER: "#ff7777",
    TREASURE: "#ffff00",
    HOLE: "#000000",
    RAIL: "#969696",
    SPIKES: "#0000ff",
    BAT_SPAWNER: "#aa0000",
    SNAKE_SPAWNER: "#00aa00",
    MUMMY_SPAWNER: "#0000aa",
    SCARAB_SPAWNER: "#aaaa00"
}

## Color2Tile
COLORS = dict((v,k) for k, v in TILES.iteritems())


## POSITIONS
(
 TOP,
 LEFT,
 RIGHT,
 BOTTOM
) = range(4)

#                   TOP     LEFT     RIGHT   BOTTOM
NEIGHBOUR_TILES = [(0, -1), (-1, 0), (1, 0), (0, 1)]
