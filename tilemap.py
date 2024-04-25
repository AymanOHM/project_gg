import pygame as pg
from texture import *

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, player_direction, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.tex = Texture(0)
        self.player_direction = player_direction
        for i in range(10):

            self.tilemap[str(6 + i) + ';4'] = {'type': 'grass', 'variant': 1, 'pos': (6 + i, 4)}
            
            self.tilemap['10;' + str(7 + i)] = {'type': 'stone', 'variant': 1, 'pos': (10, 7 + i)}
            self.tilemap['6;' + str(4 + i)] = {'type': 'stone', 'variant': 1, 'pos': (6, 4 + i)}
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def p_tiles_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self):
        for tile in self.offgrid_tiles:
            rect = pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)
            self.tex.img = self.game.assets[tile['type']][tile['variant']]
            self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, self.player_direction)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            rect = pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)
            self.tex.img = self.game.assets[tile['type']][tile['variant']]
            self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, self.player_direction)
