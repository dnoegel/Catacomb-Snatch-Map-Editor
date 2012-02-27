# coding: utf-8

__VERSION__ = 0.1
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
 SPIKES
) = range(7)


BIG_TILES = [WALL, BARRIER, TREASURE]
NEED_GROUND = [RAIL, SPIKES]

TILE_NAMES = ["Wall", "Floor", "Barrier", "Treasure", "Hole", "Rail", "Spike Trap"]

TILES = {
    WALL: "#ff0000",
    FLOOR: "#ffffff",
    BARRIER: "#ff7777",
    TREASURE: "#ffff00",
    HOLE: "#000000",
    RAIL: "#969696",
    SPIKES: "#0000ff"
}



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
