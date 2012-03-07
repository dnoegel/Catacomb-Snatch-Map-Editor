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
 SCARAB_SPAWNER,
 TEAM1_TURRET,
 TEAM2_TURRET,
 NEUTRAL_TURRET,
 LOOT,
 SAND,
 UNPASSABLE_SAND,
 DROP_TRAP,
 CHEST,
 PHARAO,
) = range(20)

## These tiles will need a special treatment when placed
BIG_TILES = [WALL, BARRIER, TREASURE, BAT_SPAWNER, SNAKE_SPAWNER, MUMMY_SPAWNER, SCARAB_SPAWNER, CHEST]
## Update surrounding tiles:
UPDATE_TILES = [SAND, UNPASSABLE_SAND, RAIL, HOLE, DROP_TRAP]
## Transparent tiles; blit some ground first
NEED_GROUND = [RAIL, SPIKES, BAT_SPAWNER, SNAKE_SPAWNER, MUMMY_SPAWNER, SCARAB_SPAWNER, TEAM1_TURRET, TEAM2_TURRET, NEUTRAL_TURRET, LOOT, CHEST]
## Names for the tiles
TILE_NAMES = ["Wall", "Floor", "Barrier", "Treasure", "Hole", "Rail", "Spike Trap", "Bat spawner", "Snake spawner", "Mummy spawner", "Scarab spawner", "Team1 Turret", "Team2 Turret", "Neutral Turret", "Loot (800)", "Sand", "Unpassable Sand", "Sturzfalle", "Schatztruhe", "Pharao"]

## Tiles2Color
TILES = {
    WALL: "#ff0000",
    FLOOR: "#ffffff",
    BARRIER: "#ff7777",
    TREASURE: "#ffff00",
    HOLE: "#000000",
    RAIL: "#969696",
    SPIKES: "#0000ff",
    BAT_SPAWNER: "#006600",
    SNAKE_SPAWNER: "#009900",
    MUMMY_SPAWNER: "#00cc00",
    SCARAB_SPAWNER: "#00ff00",
    TEAM1_TURRET: "#990099",
    TEAM2_TURRET: "#990033", 
    NEUTRAL_TURRET: "#990066",
    LOOT: "#100700",
    SAND: "#a8a800",
    UNPASSABLE_SAND: "#888800",
    DROP_TRAP: '#0000cc',
    CHEST: '#c4e570',
    PHARAO: '#ffdd00'
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
