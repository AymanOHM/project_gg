import pygame as pg
from OpenGL.GL import *
import sys
from classes import *
from helper_func import *
from tilemap import *

class Game():
    def __init__(self, w=800, h=600):
        self.movement = [False, False]

        self.direction = 1
        self.flip = False

        self.animation_idle_list = []
        self.animation_idle_index = 0
        for i in range(22):
            img = load_image(f'entities/player/idle/{i}.png')
            self.animation_idle_list.append(img)
        self.player_image = self.animation_idle_list[self.animation_idle_index]

        self.animation_run_list = []
        self.animation_run_index = 0
        for i in range(8):
            img = load_image(f'entities/player/run/{i}.png')
            self.animation_run_list.append(img)

        self.time = pg.time.get_ticks()

        self.w=w
        self.h=h
        #pg init
        pg.init()
        pg.display.set_caption("gg")
        self.screen = pg.display.set_mode((w, h), flags=pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': self.player_image
        }

        self.player = entity(self, 'player', (400, 400), (23, 45))

        self.tilemap = Tilemap(game=self, player_direction=self.flip, tile_size=45)

        # OpenGL init
        glClearColor(0.2,0.3,0.3,1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        # gluPerspective(120,w/h,0.1,100)   #default is ortho unit cube
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
        self.player.updating_tex(self)  # Updating tex for each frame.
        self.player.draw(self.flip)
        pg.display.flip()


    def update_player_animation(self):
        # Setting the time of the animation until the next one.
        animation_time = 100
        if self.movement == [False, False]:
            # Updating the animation.
            self.player_image = self.animation_idle_list[self.animation_idle_index]
            self.assets['player'] = self.player_image

            # Checking the time
            if pg.time.get_ticks() - self.time > animation_time:
                self.time = pg.time.get_ticks()
                self.animation_idle_index += 1

            # Repeating the animation.
            if self.animation_idle_index >= len(self.animation_idle_list):
                self.animation_idle_index = 0

        else:
            # Updating the animation.
            self.player_image = self.animation_run_list[self.animation_run_index]
            self.assets['player'] = self.player_image

            # Checking the time
            if pg.time.get_ticks() - self.time > animation_time:
                self.time = pg.time.get_ticks()
                self.animation_run_index += 1

            # Repeating the animation.
            if self.animation_run_index >= len(self.animation_run_list):
                self.animation_run_index = 0

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
                        self.direction = -1
                        self.flip = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                        self.direction = 1
                        self.flip = False
                    if event.key == pg.K_UP:
                        self.player.speed[1]= 5
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False

            self.update_player_animation()
            self.draw()
            self.clock.tick(60)  # limits FPS to 60


g=Game(1366,768)
g.run()
