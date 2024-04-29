import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from classes import *
from helper_func import *
from tilemap import *
from clouds import *

class Game():
    def __init__(self, w=800, h=600):
        self.movement = [False, False]

        self.w=w
        self.h=h
        self.environment = {'gravity': 0.2}
        #pg init
        pg.init()
        pg.display.set_caption("gg")
        self.display = pg.display.set_mode((w, h), flags=pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_images('entities/player/idle'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
        }

        self.scroll=[0,0]
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = player(self, (750, 600), (35, 55))

        self.tilemap = Tilemap(game=self, tile_size=45)
        self.tilemap.load('map.json')

        # OpenGL init

        glClearColor(72/255,160/255,211/255,1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        # gluPerspective(120,w/h,0.1,100)   #default is ortho unit cube
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        
        scroll=self.scroll
        glTranslate(-scroll[0],-scroll[1],0)
        # glRotate(30,0,0,1)
        # glColor3b(52, 73, 102)
        self.clouds.update()
        self.clouds.render()
        
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
                        self.player.jump()
                        
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False
                        
            self.scroll[0] += int((self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) /30)
            self.scroll[1] += int((self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/30)

            self.draw()
            self.clock.tick(60)  # limits FPS to 60


g = Game(1366, 768)
g.run()
