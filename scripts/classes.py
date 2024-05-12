from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import * 
from scripts.helper_func import *
from scripts.texture import *
# from game import *

class entity:
    def __init__(self, game, path, pos= [0, 0], size=[50, 50], speed=[6, 5]):

        self.pos= list(pos)
        self.s_pos= pos
        
        self.size= list(size)

        self.game= game
        self.environment= game.environment
        self.gravity= self.environment['gravity']
        
        # texture
        self.path= path
        self.tex= Texture(game.assets[path])
        
        
        ## Entity transformation ##
        # movement will be passed from update
        self.speed= tuple(speed)      # initial speed property
        self.velocity= [speed[0], 0] # interactive speed

        self.collisions= {'up': False,
                           'down': False,
                           'right': False,
                           'left': False}

        self.action= ''
        self.flip= False


    def rect(self):
        return Rect(self.pos[0],self.pos[1],self.size[0],self.size[1])


    def set_action(self, action):
        if action != self.action:
            self.action= action
            self.animation= self.game.assets[self.path + '/' + self.action].copy()


    def draw(self):
        rect= self.rect()
        self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, self.flip)


class player(entity):
    def __init__(self, game, path, pos= [0,0], size=[50,50], speed=[6,5]):
        super().__init__(game, path, pos, size, speed)
        
        self.flags= {'air_jump': False,
                      'last_wall_jump': {'right': False, 'left': False},
                      'friction': False,
                      'fast_fall' : False
                      }
        self.air_time= 0
        self.mov_amount= [0,0]
        
        self.set_action('idle')
        self.health= 100
        self.fire= False
    
        self.gun= gun(self.game,[self.rect().centerx,self.rect().centery])
        
        self.health_bar= Health_bar(x= pos[0] - 8, y= pos[1] + 60 ,
                                     w=50, h=5,
                                     texture_path= game.assets['health_bar'],
                                     max_health=self.health,)
    
    def reset(self):
        self.health=100
        self.pos= self.s_pos    
    
    def move(self, map, direction):
        
        self.update_mov_amount(direction)
        
        # resetting collisions every movement
        self.collisions= {'up': False, 'down': False, 'right': False, 'left': False}        

        
        ## Check Collisions ##
        
        # Change horizontal position
        self.pos[0] += self.mov_amount[0]
        
        # Check horizontal collision
        entity_rect= self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                
                # From Right
                if self.mov_amount[0] > 0:
                    # Edit Flags
                    self.collisions['right']= True
                    self.flags['friction']= True
                    
                    entity_rect.right= rect.left
                    
                # From Left
                if self.mov_amount[0] < 0:
                    # Edit Flags
                    self.collisions['left']= True
                    self.flags['friction']= True
                        
                    entity_rect.left= rect.right
                    
                self.pos[0]= entity_rect.x
        
        # Change vertical position
        self.pos[1] += self.mov_amount[1]
        
        # Check Vertical collision
        entity_rect= self.rect()
        for rect in map.p_tiles_around(self.pos):
            if entity_rect.colliderect(rect):
                
                if self.mov_amount[1] > 0:
                    # Stop the player
                    self.velocity[1]= 0
                    
                    # Edit Flags
                    self.collisions['up']= True
                    entity_rect.top= rect.bottom
                    
                    
                if self.mov_amount[1] < 0:
                    # Stop the player
                    self.velocity[1]= 0
                    
                    # Edit Flags
                    self.collisions['down']= True
                    
                    self.flags['air_jump']= True
                    
                    self.flags['last_wall_jump']['right']= False
                    self.flags['last_wall_jump']['left']= False
                    self.air_time= 0
                    entity_rect.bottom= rect.top
                    
                    
                self.pos[1]= entity_rect.y
        
        if self.velocity[1] < 0 and self.flags['friction']: # Falling and Stick to the wall
            gravity_effect=  self.gravity / 2
        else:
            gravity_effect= self.gravity
        
        if self.flags['fast_fall']:
            self.velocity[1]= self.velocity[1] - 0.5
            
        self.velocity[1]= max(-10, self.velocity[1] - gravity_effect )
        
        self.flags['friction']= False
        
        if self.mov_amount[0] > 0:
            self.flip= False
        if self.mov_amount[0] < 0:
            self.flip= True
        
        ### Animations ###
        self.animation.update()
        self.air_time += 1
        self.action_update(direction)
        
        ### Gun and Bullets ###
        if self.fire:
            self.gun.fire()
        
        
        self.gun.flip=self.flip
        
        if not self.flip:
            self.gun.pos=[self.pos[0]+21,self.pos[1]+15]
        else:
            self.gun.pos=[self.pos[0],self.pos[1]+15]
            
        self.gun.bullets.update()
        
        ### Health Bar ###
        if self.health<=0 or self.pos[1] < -300:
            self.game.stage=2
            self.game.is_alive=False
            
        self.health_bar.update_pos(self.pos[0] - 8, self.pos[1] + 60)
        self.health_bar.draw()
        
    def update_mov_amount(self, direction): # Direction is list[int, int]=> between -1,0,1
        
        # In the air or Just wall jumped
        if not any(self.collisions.values()) or any(self.flags['last_wall_jump'].values()):
            
            air_dive_effect= direction[0]  * self.velocity[0] / 10
            h_limit= self.speed[0]
            
            if self.mov_amount[0] > 0: # Was moving right
                self.mov_amount[0]= min(h_limit, self.mov_amount[0] + air_dive_effect )
                
            else:
                self.mov_amount[0]= max( -h_limit , self.mov_amount[0] + air_dive_effect ) # air_dive_effect is negative

            
            self.mov_amount[1]= self.velocity[1]

        else:
            self.mov_amount= [direction[0] * self.velocity[0], self.velocity[1]]

    
    
    def jump(self):
        
        ## Check Double Jump ##
        if not any( self.collisions.values() ) and self.flags['air_jump'] == True: # In the air
            self.do_jump_action()
            self.flags['air_jump']= False
        else:
            if self.collisions['down']: # On the ground
                self.do_jump_action()
                
        ## Check Wall Jump ##
            elif self.collisions['right']:
                self.do_wall_jump_action(-1)
                
                self.flags['last_wall_jump']['right']= True
                self.flags['last_wall_jump']['left']= False
                self.flags['air_jump']= True
                    
            elif self.collisions['left']:
                self.do_wall_jump_action(1)
                
                self.flags['last_wall_jump']['left']= True
                self.flags['last_wall_jump']['right']= False
                self.flags['air_jump']= True
                    
        
    
    def do_jump_action(self):
        self.velocity[1]= self.speed[1]
    
    def do_wall_jump_action(self, direction): # Direction: Integer of -1 (left) or 1 (right)
        self.velocity[1]= self.speed[1]
        self.mov_amount[0]= direction * self.speed[0]
        
    def action_update(self, movement):
        if self.air_time > 1:
            if self.collisions['right'] or self.collisions['left'] :
                self.set_action('wall_slide')
            else:
                self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
        
    def update_tex(self):
        self.tex= Texture(self.animation.img())
    
    def draw(self):
        rect= self.rect()
        
        self.update_tex()
        self.tex.draw(rect.left, rect.right, rect.top, rect.bottom, self.flip)
        self.gun.draw()
        self.gun.bullets.draw()
        
        
class gun(entity):
    def __init__(self, game, pos, size=[15, 13]):
        super().__init__(game,'gun', pos, size, [0,0])
        self.bullets=Bullets()
        self.b_time=glutGet(GLUT_ELAPSED_TIME)
    def fire(self):
        if  glutGet(GLUT_ELAPSED_TIME)-self.b_time>250:
            if not self.flip:
                self.bullets.new_bullet(self.game,[self.pos[0]+25,self.pos[1]+5],self.flip)
            else:
                self.bullets.new_bullet(self.game,[self.pos[0]-45,self.pos[1]+5],self.flip)
            self.b_time=glutGet(GLUT_ELAPSED_TIME)
        

class Bullets:
    def __init__(self):
        self.bullets= []

    def new_bullet(self,game,  pos, flip):
        self.bullets.append(Bullet(game,self.bullets, pos, flip))

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()

    def update(self):
        
        for bullet in self.bullets:
            
            dis=  abs(bullet.pos[0]-bullet.s_pos[0])
            if dis> 500:
                self.bullets.remove(bullet)
            else: 
                bullet.update()

    def get_bullets(self):
        return self.bullets

        
class Bullet(entity):
    def __init__(self,game,bullet_lst, pos, flip):
        super().__init__(game,'bullet', pos, [35,15], [0,0])    
        self.flip=not flip
        self.s_pos=pos
        self.bullets=bullet_lst
        

    def update(self):
        
        if self.rect().colliderect(self.game.player.rect()):
            self.game.player.health -= 20
            self.game.player.health_bar.set_health(self.game.player.health)
            self.bullets.remove(self)
            return
            
        elif self.rect().colliderect(self.game.enemy.rect()):
            self.game.enemy.health -= 20  
            self.game.enemy.health_bar.set_health(self.game.enemy.health)
            self.bullets.remove(self)
            return
        for tile_rect in self.game.tilemap.p_tiles_around(self.pos):
            if self.rect().colliderect(tile_rect):
                self.bullets.remove(self)
                return
        if  self.flip:
            self.pos[0] += 20
        else:
            self.pos[0] -= 20

class Health_bar():
    def __init__(self, x, y, w, h, texture_path, max_health=100):
        self.rect= Rect(x, y, w, h)
        
        self.tex= Texture(texture_path)
        self.max_health= max_health
        self.max_width= w
    
    def set_health(self, value):
        health_ratio= value / self.max_health
        self.rect.w= health_ratio * self.max_width
    
    def update_pos(self, x, y):
        self.rect.x= x
        self.rect.y= y
        
    def draw(self):
        left= self.rect.left
        right= self.rect.right
        top= self.rect.top
        bottom= self.rect.bottom
        
        self.tex.draw(left, right, top, bottom)
