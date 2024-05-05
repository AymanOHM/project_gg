from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 

from texture import *
# from game import *

class entity:

    def __init__(self, game, path, pos, size=[50, 50], speed=[6, 5]):

        self.pos = list(pos)
        self.game=game
        self.environment = game.environment
        self.gravity = self.environment['gravity']
        self.size   = list(size)   
        
        # texture
        self.path = path
        self.tex = Texture(game.assets['player'])
        
        
        ## Entity transformation ##
        # movement will be passed from update
        self.speed = list(speed)      # initial speed property
        self.velocity = [speed[0], 0] # interactive speed

        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.flip = False
        self.set_action('idle')

    def rect(self):
        return Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])
    
    #the rect method does update param this for us, all we need is to change pos now    

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.path + '/' + self.action].copy()
        
    def move(self, map, movement: bool):
        #resetting collisions every movement
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}        
        
        mov_amount = (movement[0]*self.velocity[0], movement[1] + self.velocity[1])
        
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
                if mov_amount[1] < 0:
                    self.collisions['up'] = True
                    entity_rect.bottom = rect.top
                if mov_amount[1] > 0:
                    self.collisions['down'] = True
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.velocity[1] = min(5, self.velocity[1] - 0.2)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()
        
        
    def updating_tex(self):
        self.tex = Texture(self.animation.img())

    def draw(self):
        rect = self.rect()
        self.updating_tex()
        self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, self.flip)


class player(entity):
    
    def __init__(self, game, pos, size=[50,50], speed=[6,5]):
        super().__init__(game,'player',pos,size,speed)
        
        self.flags = {'air_jump': False,
                      'last_wall_jump': {'right': False, 'left': False},
                      'friction': False
                      }
        self.air_time=0
        self.mov_amount = [0,0]
    
    def move(self, map, direction: bool):
        
        self.update_mov_amount(direction)
        
        # resetting collisions every movement
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}        

        
        ## Check Collisions ##
        
        # Change horizontal position
        self.pos[0] += self.mov_amount[0]
        
        # Check horizontal collision
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                
                
                # From Right
                if self.mov_amount[0] > 0:
                    # Edit Flags
                    self.collisions['right'] = True
                    self.flags['friction'] = True
                    
                    entity_rect.right = rect.left
                    
                # From Left
                if self.mov_amount[0] < 0:
                    # Edit Flags
                    self.collisions['left'] = True
                    self.flags['friction'] = True
                        
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x
        
        # Change vertical position
        self.pos[1] += self.mov_amount[1]
        
        # Check Vertical collision
        entity_rect = self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                
                if self.mov_amount[1] > 0:
                    # Stop the player
                    self.velocity[1] = 0
                    
                    # Edit Flags
                    self.collisions['up'] = True
                    
                    entity_rect.bottom = rect.top
                    
                if self.mov_amount[1] < 0:
                    # Stop the player
                    self.velocity[1] = 0
                    
                    # Edit Flags
                    self.collisions['down'] = True
                    
                    self.flags['air_jump'] = True
                    
                    self.flags['last_wall_jump']['right'] = False
                    self.flags['last_wall_jump']['left'] = False
                    self.air_time = 0
                    
                    entity_rect.top = rect.bottom
                    
                self.pos[1] = entity_rect.y
        
        if self.velocity[1] < 0 and self.flags['friction']:
            gravity_effect =  self.gravity / 2
        else:
            gravity_effect = self.gravity
        
        self.velocity[1] = max(-10, self.velocity[1] - gravity_effect )
        self.flags['friction'] = False
        
        if self.mov_amount[0] > 0:
            self.flip = False
        if self.mov_amount[0] < 0:
            self.flip = True
        
        self.animation.update()
        self.air_time += 1
        
        self.texture_update(direction)
        
        
    def update_mov_amount(self, direction):
        
        if not any(self.collisions.values()) or any(self.flags['last_wall_jump'].values()):
            
            air_dive_effect = direction[0]  * self.velocity[0] / 10
            limit = self.velocity[0]
            
            if self.mov_amount[0] > 0:
                self.mov_amount[0] = min(limit, self.mov_amount[0] + air_dive_effect )
                
            else:
                self.mov_amount[0] = max( -limit , self.mov_amount[0] + air_dive_effect )

            self.mov_amount[1] = direction[1] + self.velocity[1]

        else:
            self.mov_amount = [direction[0] * self.velocity[0], direction[1] + self.velocity[1]]

    
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
                self.do_wall_jump_action(-1)
                
                self.flags['last_wall_jump']['right'] = True
                self.flags['last_wall_jump']['left'] = False
                self.flags['air_jump'] = True
                    
            if self.collisions['left']:
                self.do_wall_jump_action(1)
                
                self.flags['last_wall_jump']['left'] = True
                self.flags['last_wall_jump']['right'] = False
                self.flags['air_jump'] = True
                    
        
    
    def do_jump_action(self):
        self.velocity[1]= self.speed[1]
    
    def do_wall_jump_action(self, direction):
        self.velocity[1] = self.speed[1]
        self.mov_amount[0] = direction * self.speed[0]
        
    
    
    def texture_update(self, movement):
        if self.air_time > 1:
            if self.collisions['right'] or self.collisions['left'] :
                self.set_action('wall_slide')
            else:
                self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
class Rect():
    def __init__(self, x, y, w, h):
        self._x = int(x)
        self._y = int(y)
        self._w = int(w)
        self._h = int(h)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = int(value)
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = int(value)
    
    @property
    def centerx(self):
        return self._x
    
    @centerx.setter
    def centerx(self, value):
        self._x = int(value)
    
    @property
    def centery(self):
        return self._y
    
    @centery.setter
    def centery(self, value):
        self._y = int(value)
    
    @property
    def top(self):
        return self._y
    
    @top.setter
    def top(self, value):
        self._y = int(value)
    
    @property
    def left(self):
        return self._x
    
    @left.setter
    def left(self, value):
        self._x = int(value)
    
    @property
    def bottom(self):
        return self._y + self._h
    
    @bottom.setter
    def bottom(self, value):
        self._y = int(value) - self._h
    
    @property
    def right(self):
        return self._x + self._w
    
    @right.setter
    def right(self, value):
        self._x = int(value) - self._w
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = int(value)
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = int(value)
    
    def colliderect(self, rect):
        
        # Calculate max horizontal distance
        max_h_distance = max(abs(self.right - rect.left), abs(self.left - rect.right))
        
        # Calculate max vertical distance
        max_v_distance = max(abs(self.bottom - rect.top), abs(self.top - rect.bottom))
        
        
        # Detect collision
        h_collid = max_h_distance < (self.w + rect.w)
        v_collid = max_v_distance < (self.h + rect.h)
        
        collid = (h_collid and v_collid)
        return collid

    def colliderect(self, rect):
        
        # Calculate max horizontal distance
        max_h_distance = max(abs(self.right - rect.left), abs(self.left - rect.right))
        
        # Calculate max vertical distance
        max_v_distance = max(abs(self.top - rect.bottom), abs(self.bottom - rect.top))
        
        
        # Detect collision
        h_collid = max_h_distance < (self.w + rect.w)
        v_collid = max_v_distance < (self.h + rect.h)
        
        collid = (h_collid and v_collid)
        return collid
    