import json
from scripts.texture import *
import scripts.classes as classes
from scripts.helper_func import *

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.tex = Texture(0)
    
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
    
        self.tilemap = map_data['tilemap']
        self.offgrid_tiles = map_data['offgrid']
        
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
                rects.append(Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self):
        for tile in self.offgrid_tiles:
            rect = Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)
            self.tex.img = self.game.assets[tile['type']][tile['variant']]
            self.tex.draw(rect.left, rect.right, rect.top, rect.bottom)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            rect = Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size)
            self.tex.img = self.game.assets[tile['type']][tile['variant']]
            self.tex.draw(rect.left, rect.right, rect.top, rect.bottom)


#   self.tex={
#    {'grass':{'1':self.game.assets['grass'][0]},
#     etc.},
#    etc.  
# }
#
# dictionary O(1)                                                                  
#tiles_around ---> 9 tiles only
# draw --> change img --> bind --> render