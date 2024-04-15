import pygame as pg
from OpenGL.GL import *
import sys
from classes import *
from helper_func import *
from tilemap import *

class Game():
    def __init__(self, w=800,h=600):
        self.movement=[False,False]
        
        
        #pg init
        pg.init()
        pg.display.set_caption("gg")
        self.screen=pg.display.set_mode((w,h),flags= pg.OPENGL | pg.DOUBLEBUF)
        self.clock=pg.time.Clock()
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png')
        }
        
        self.player = entity(self, 'player', (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        #OpenGL init
        glClearColor(0.2,0.3,0.3,1.0)
    
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        #gluPerspective(120,w/h,0.1,100)   #default is ortho unit cube
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
        glLoadIdentity()
        # glRotate(theta,0,0,1)
        # glColor3b(52, 73, 102)
        self.tilemap.render()
            
        self.player.move(self.tilemap, [self.movement[1] - self.movement[0], 0])
        self.player.draw()
        pg.display.flip()
     

    def run(self):
        
        while True:
        # glutMainLoop() or pg loop in this case
            
            
           
           
            
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()  
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pg.K_UP:
                        self.player.speed[1]= 3
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False     
            self.draw()
            self.clock.tick(60)  # limits FPS to 60


g=Game()
g.run()