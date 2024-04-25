from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 
import pygame as pg

from texture import *
# from game import *

class entity:

    def __init__(self, game, path, pos, size=[50, 50], speed=[3, 0]):

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

          
    def move(self, map, movement: bool):
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

    def updating_tex(self, game):
        self.tex = Texture(game.assets['player'])

    def draw(self, player_direction):
        rect = self.rect()
        self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, player_direction)


class player(entity):
    
    def __init__(self, game, path, pos, size=[50,50], speed=[3,0]):
        
        self.environment = game.environment

        self.gravity = self.environment['gravity']
        
        self.pos = list(pos)
        self.size  = list(size)
        
        self.flags = {'air_jump': False,
                      'last_wall_jump': {'right': False, 'left': False},
                      'friction': False
                      }
        
        #texture
        self.path = path
        self.tex = Texture(game.assets['player'])
        
        
        ## Entity transformation ##
        # movement will be passed from update
        self.speed = list(speed)  #array
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
    
    def move(self, map, movement: bool):
        # resetting collisions every movement
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}        

        mov_amount = (movement[0] + movement[0] * self.speed[0], movement[1] + self.speed[1])
        
        ## Check Collisions ##
        
        # Change horizontal position
        self.pos[0] += mov_amount[0]
        
        # Check horizontal collision
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if mov_amount[0] > 0:
                    # Edit Flags
                    self.collisions['right'] = True
                    self.flags['friction'] = True
                    entity_rect.right = rect.left
                    
                if mov_amount[0] < 0:
                    # Edit Flags
                    self.collisions['left'] = True
                    self.flags['friction'] = True
                        
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x
        
        # Change vertical position
        self.pos[1] += mov_amount[1] -  self.flags['friction'] * ( mov_amount[1] // 2 )
        self.flags['friction'] = False
        
        # Check Vertical collision
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                if mov_amount[1] > 0:
                    # Stop the player
                    self.speed[1] = 0
                    
                    # Edit Flags
                    self.collisions['up'] = True
                    
                    entity_rect.bottom = rect.top
                    
                if mov_amount[1] < 0:
                    # Stop the player
                    self.speed[1] = 0
                    
                    # Edit Flags
                    self.collisions['down'] = True
                    
                    self.flags['air_jump'] = True
                    
                    self.flags['last_wall_jump']['right'] = False
                    self.flags['last_wall_jump']['left'] = False
                    
                    entity_rect.top = rect.bottom
                    
                self.pos[1] = entity_rect.y
        
        self.speed[1] = min(5, self.speed[1] - self.gravity)
        
        
    def jump(self):
        ## Check Double Jump ##
        if not any( self.collisions.values() ) and self.flags['air_jump'] == True: # In the air
            self.do_jump_action()
            self.flags['air_jump'] = False
        else:
            if self.collisions['down']: # On the ground
                self.do_jump_action()
                
        ## Check Wall Jump ##
            if self.collisions['right']:
                if self.flags['last_wall_jump']['right'] == False: # Last jump wasn't from right
                    self.do_jump_action()
                    
                    self.flags['last_wall_jump']['right'] = True
                    self.flags['last_wall_jump']['left'] = False
                    self.flags['air_jump'] = True
                    
            if self.collisions['left']:
                if self.flags['last_wall_jump']['left'] == False: # Last jump wasn't from left
                    self.do_jump_action()
                    
                    self.flags['last_wall_jump']['left'] = True
                    self.flags['last_wall_jump']['right'] = False
                    self.flags['air_jump'] = True
                    
        
    def do_jump_action(self):
        self.speed[1]= 5