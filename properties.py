#!/usr/bin/env python
import os
import sys
import msgpack

from tml.tml import Teemap
from tml.items import TileLayer
from tml.constants import TML_DIR, TILEINDEX

Entities = {
  'NULL': 0,
  'SPAWN': 1,
  'SPAWN_RED': 2,
  'SPAWN_BLUE': 3,
  'FLAGSTAND_RED': 4,
  'FLAGSTAND_BLUE': 5,
  'ARMOR_1': 6,
  'HEALTH_1': 7,
  'WEAPON_SHOTGUN': 8,
  'WEAPON_GRENADE': 9,
  'POWERUP_NINJA': 10,
  'WEAPON_RIFLE': 11,
  # DDRace - Main Lasers
  'LASER_FAST_CW': 12,
  'LASER_NORMAL_CW': 13,
  'LASER_SLOW_CW': 14,
  'LASER_STOP': 15,
  'LASER_SLOW_CCW': 16,
  'LASER_NORMAL_CCW': 17,
  'LASER_FAST_CCW': 18,
  # DDRace - Laser Modifiers
  'LASER_SHORT': 19,
  'LASER_MEDIUM': 20,
  'LASER_LONG': 21,
  'LASER_C_SLOW': 22,
  'LASER_C_NORMAL': 23,
  'LASER_C_FAST': 24,
  'LASER_O_SLOW': 25,
  'LASER_O_NORMAL': 26,
  'LASER_O_FAST': 27,
  # DDRace - Plasma
  'PLASMAE': 29,
  'PLASMAF': 30,
  'PLASMA': 31,
  'PLASMAU': 32,
  # DDRace - Shotgun
  'CRAZY_SHOTGUN_EX': 33,
  'CRAZY_SHOTGUN': 34,
  # DDRace - Draggers
  'DRAGGER_WEAK': 42,
  'DRAGGER_NORMAL': 43,
  'DRAGGER_STRONG': 44,
  # Draggers Behind Walls
  'DRAGGER_WEAK_NW': 45,
  'DRAGGER_NORMAL_NW': 46,
  'DRAGGER_STRONG_NW': 47,
  # Doors
  'DOOR': 49,
}

Tiles = {
  # Start From Top Left
  # Tile Controllers
  'AIR': 0,
  'SOLID': 1,
  'DEATH': 2,
  'NOHOOK': 3,
  'NOLASER': 4,
  'THROUGH': 6,
  'JUMP': 7,
  'FREEZE': 9,
  'TELEINEVIL': 10,
  'UNFREEZE': 11,
  'DFREEZE': 12,
  'DUNFREEZE': 13,
  'TELEINWEAPON': 14,
  'TELEINHOOK': 15,
  'WALLJUMP': 16,
  'EHOOK_START': 17,
  'EHOOK_END': 18,
  'HIT_START': 19,
  'HIT_END': 20,
  'SOLO_START': 21,
  'SOLO_END': 22,
  # Switches
  'SWITCHTIMEDOPEN': 22,
  'SWITCHTIMEDCLOSE': 23,
  'SWITCHOPEN': 24,
  'SWITCHCLOSE': 25,
  'TELEIN': 26,
  'TELEOUT': 27,
  'BOOST': 28,
  'TELECHECK': 29,
  'TELECHECKOUT': 30,
  'TELECHECKIN': 31,
  'BEGIN': 33,
  'END': 34,
  'STOP': 60,
  'STOPS': 61,
  'STOPA': 62,
  'CP': 64,
  'CP_F': 65,
  'OLDLASER': 71,
  'NPC': 72,
  'EHOOK': 73,
  'NOHIT': 74,
  'NPH': 75,
  'NPC_END': 88,
  'SUPER_END': 89,
  'JETPACK_END': 90,
  'NPH_END': 91,
  'NPC_START': 104,
  'SUPER_START': 105,
  'JETPACK_START': 106,
  'NPH_START': 107
}

gameTiles = ['DFREEZE', 'EHOOK_START', 'HIT_START', 'SOLO_START', 'NPC_START', 'SUPER_START', 'JETPACK_START', 'NPH_START', 'WEAPON_SHOTGUN', 'WEAPON_GRENADE', 'POWERUP_NINJA', 'WEAPON_RIFLE', 'WALLJUMP']
frontTiles = ['DFREEZE', 'EHOOK_START', 'HIT_START', 'SOLO_START', 'NPC_START', 'SUPER_START', 'JETPACK_START', 'NPH_START', 'WEAPON_SHOTGUN', 'WEAPON_GRENADE', 'POWERUP_NINJA', 'WEAPON_RIFLE', 'WALLJUMP']
switchTiles = ['JUMP', 'SWITCHTIMEDOPEN', 'SWITCHOPEN', 'HIT_START']
speedupTiles = ['BOOST']
teleTiles = ['TELEINEVIL', 'TELEIN', 'TELECHECKIN', 'TELEINWEAPON', 'TELEINHOOK']

def add(result, tiles, layer):
  if layer:
    for tile in layer.tiles:
      for key in tiles:
        if tile.index == Tiles.get(key):
          result[key] = True
        if tile.index - 191 == Entities.get(key):
          result[key] = True

def main(argv):
  map_path = argv[1]
  result_path = argv[2]
  t = Teemap(map_path)
  result = {}

  frontlayer = None # Works thanks to hack in tml
  for group in t.groups:
    if group.name == 'Game':
      for layer in group.layers:
        if type(layer) == TileLayer and layer.name == 'Front':
          frontlayer = layer
          break

  add(result, gameTiles, t.gamelayer)
  add(result, frontTiles, frontlayer)

  # These don't seem to be working
  #add(result, switchTiles, switchlayer)
  #add(result, speedupTiles, t.speeduplayer)
  #add(result, teleTiles, t.telelayer)

  with open(result_path, 'wb') as out:
    out.write(msgpack.packb(t.gamelayer.width))
    out.write(msgpack.packb(t.gamelayer.height))
    out.write(msgpack.packb(result))

if __name__ == "__main__":
  main(sys.argv)
