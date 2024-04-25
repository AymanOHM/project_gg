from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 
import pygame as pg

from texture import *

class entity:
    
    def __init__(self, game, path, pos, size=[50,50], speed=[3,0]):
        
        self.pos = list(pos)
        self.size   = list(size)   
        
        #texture
        self.path = path
        self.tex = Texture(game.assets['player'])
        
        
        ## Entity transformation ##
        #movement will be passed from update
        self.speed = list(speed)  #array
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        
    def rect(self):
        return pg.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
    
    #the rect method does update param this for us, all we need is to chang pos now    

          
    def move(self,map, movement):
        #resetting collisions every movement
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}        
        
        mov_amount = (movement[0]*self.speed[0], movement[1] + self.speed[1])
        
        self.pos[0] += mov_amount[0]
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if mov_amount[0] > 0:
                    self.collisions['right'] = True
                    entity_rect.right = rect.left
                if mov_amount[0] < 0:
                    self.collisions['left'] = True
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x
        
        self.pos[1] += mov_amount[1]
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if mov_amount[1] > 0:
                    self.collisions['up'] = True
                    entity_rect.bottom = rect.top
                if mov_amount[1] < 0:
                    self.collisions['down'] = True
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y
        
        self.speed[1] = min(5, self.speed[1] - 0.2)
        
        if self.collisions['down'] or self.collisions['up']:
            self.speed[1] = 0
        

    def draw(self):
        rect = self.rect()
        self.tex.draw(rect.left,rect.right,rect.top,rect.bottom)
      

