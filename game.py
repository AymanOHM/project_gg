import sys
import os

parent_dir = os.path.abspath(os.path.dirname(__file__))
libs_dir = os.path.join(parent_dir, 'libs')

sys.path.append(libs_dir)

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from scripts.classes import *
from scripts.helper_func import *
from scripts.tilemap import *
from scripts.clouds import *
from scripts.screens import *

class Game():
    def __init__(self, w=800, h=600, fullscreen=True):
        self.fullscreen = fullscreen
        
        self.is_alive = False
        self.stage= 0
        self.movement = [False, False, False, False]

        self.w=w
        self.h=h
        self.environment = {'gravity': 0.2}
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_images('entities/player/idle'),
            'enemy': load_images('entities/player2/idle'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')), 
            'enemy/idle': Animation(load_images('entities/player2/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/player2/run'), img_dur=4),
            'enemy/jump': Animation(load_images('entities/player2/jump')),
            'enemy/slide': Animation(load_images('entities/player2/slide')),
            'enemy/wall_slide': Animation(load_images('entities/player2/wall_slide')),
            'gun': load_image('_gun.png'),
            'bullet': load_image('bullet3.png'),
            'health_bar': load_image('health_simple.png'),
            'welcome': load_image('welcome.png'),
            'P1': load_image('P1.png'),
            'P2': load_image('P2.png')
        }

        # OpenGL init
        self.gl_init()

        self.scroll=[0,0]

        self.wel_screen = Screen(self, 'welcome', [-400, 1000])
        self.P1_screen = Screen(self, 'P1', [2000, 300])
        self.P2_screen = Screen(self, 'P2', [-2000, 300])

        self.clouds = Clouds(self.assets['clouds'], count=16)




        self.tilemap = Tilemap(game=self, tile_size=45)

        self.tilemap.load('map.json')

        if self.fullscreen:
            glutFullScreen()

        glutMainLoop()


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        scroll=self.scroll
        
        glLoadIdentity()
        glTranslate(-scroll[0],-scroll[1],0)
        
        self.clouds.update()
        self.clouds.render()

        self.tilemap.render()
        
        if self.is_alive:
            
            self.scroll[0] += (((self.player.pos[0]+self.enemy.pos[0])/2) - self.w / 2 - self.scroll[0]) /30
            self.scroll[1] += (((self.player.pos[1]+self.enemy.pos[1])/2) - self.h / 2 - self.scroll[1])/30

            self.player.move(self.tilemap, [self.movement[3] - self.movement[2], 0])
            self.enemy.move(self.tilemap, [self.movement[1] - self.movement[0], 0])
            
            # Drawing the player.
            self.player.draw()
            # Drawing the enemy.
            self.enemy.draw()
        
        else:
            self.show_screens()
            
        glutSwapBuffers()


    def show_screens(self):
        if self.stage ==0:
            self.wel_screen.draw()
            self.scroll[0] += (self.wel_screen.center[0] -  self.w / 2 -self.scroll[0])/30
            self.scroll[1] += (self.wel_screen.center[1] -  self.h / 2 -self.scroll[1])/30
        elif self.stage ==1:
            
            self.player = player(self,'player',(900, 600),(35, 55))
    
            self.enemy = player(self, 'enemy',(80, 600), (35, 55)) 
            self.is_alive=True
            # self.player.reset()
            # self.enemy.reset()
        elif self.stage==2:
            if self.enemy.health==0 or self.enemy.pos[1] < -300:
                self.P1_screen.draw()
                self.scroll[0] += (self.P1_screen.center[0] - self.w / 2 - self.scroll[0]) /30
                self.scroll[1] += (self.P1_screen.center[1] - self.h / 2 - self.scroll[1])/30
        
            else:
                self.P2_screen.draw()
                self.scroll[0] += (self.P2_screen.center[0] - self.w / 2 - self.scroll[0]) /30
                self.scroll[1] += (self.P2_screen.center[1] - self.h / 2 - self.scroll[1])/30
    
    def gl_init(self):
        
        # OpenGL Initialization
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
        glutInitWindowPosition(0,0)
        glutInitWindowSize(self.w, self.h)
        glutCreateWindow(b"gg")
        
        
        # Define functions
        glutDisplayFunc(self.draw)
        glutKeyboardFunc(self.keyboard_callback)
        glutKeyboardUpFunc(self.keyboardUp_callback)
        
        glutTimerFunc(2, self.game_timer, 2)
        
        # Enable Texture
        glEnable(GL_TEXTURE_2D)
        
        # Activate Transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # FOR BLENDING
        
        # Preparations
        glClearColor(72/255,160/255,211/255,1.0) # Sky color
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.w, 0, self.h, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def game_timer(self, v):
        self.draw()
        glutTimerFunc(v, self.game_timer, v)
    
    def keyboard_callback(self, key, x, y):
        if key == b'\r' and not self.is_alive:
            self.stage=1
        if key == b"q":
            sys.exit(0)
        
        if self.is_alive:
            if key == b'a':
                self.movement[0] = True 
            if key == b'd':
                self.movement[1] = True
            if key == b'w' and self.is_alive:
                self.enemy.jump()
            if key == b's'and self.is_alive:
                self.enemy.flags['fast_fall'] = True
                
            if key == b'4':
                self.movement[2] = True
            if key == b'6':
                self.movement[3] = True
            if key == b'8':
                self.player.jump()
            if key == b'5':
                self.player.flags['fast_fall'] = True
            if key == b' ':
                self.enemy.fire=True
            if key == b'0':
                self.player.fire=True

    def keyboardUp_callback(self, key, x, y):
        if key == b'a':
            self.movement[0] = False
        if key == b'd':
            self.movement[1] = False
        if key == b's':
            self.enemy.flags['fast_fall'] = False
            
        if key == b'4':
            self.movement[2] = False
        if key == b'6':
            self.movement[3] = False
        if key == b'5':
            self.player.flags['fast_fall'] = False
        if key == b' ':
            self.enemy.fire=False
        if key == b'0':
            self.player.fire=False


g = Game(1280, 720, fullscreen=True)

