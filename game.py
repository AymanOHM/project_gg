import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from classes import *
from helper_func import *
from tilemap import *
from clouds import *
from bullet import *

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
            'gun': load_image('_gun.png'),
            'bullet': load_image('bullet.png')
        }

        self.scroll=[0,0]

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = player(self, (750, 600), (35, 55))
        self.gun = Texture(self.assets['gun'])
        self.player_gun_direction = False
        self.bullet_group = []
        self.shoot = False
        self.tilemap = Tilemap(game=self, tile_size=45)
        self.tilemap.load('map.json')

        self.bullet = Bullets()


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



        # Drawing the player gun.
        if not self.player_gun_direction:
            self.gun.draw(self.player.pos[0] + 20, self.player.pos[0] + 35,
                          self.player.pos[1] + 15, self.player.pos[1] + 28, direction=False)
            # Drawing the bullet at case of shooting and the player looks right.
            if self.shoot:

                self.bullet.new_bullet(self.player.rect().centerx + 17, self.player.rect().centery - 3,
                self.player_gun_direction, self.assets['bullet'])
            self.bullet.render()
            self.bullet.update()



        else:
            self.gun.draw(self.player.pos[0], self.player.pos[0] + 15,
                          self.player.pos[1] + 15, self.player.pos[1] + 28, direction=True)
            # Drawing the bullet at case of shooting and the player looks left.
            if self.shoot:
                self.bullet.new_bullet(self.player.rect().centerx - 21, self.player.rect().centery - 3,
                self.player_gun_direction, self.assets['bullet'])
            self.bullet.render()
            self.bullet.update()





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
                        self.player_gun_direction = True
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = True
                        self.player_gun_direction = False
                    if event.key == pg.K_UP:
                        self.player.jump()
                    if event.key == pg.K_m:
                        self.shoot = True

                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        self.movement[0] = False
                    if event.key == pg.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pg.K_m:
                        self.shoot = False
                        # self.bullet.bullets = []
                        
            self.scroll[0] += int((self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) /30)
            self.scroll[1] += int((self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/30)

            self.draw()
            self.clock.tick(60)  # limits FPS to 60


g = Game(1366, 768)
g.run()
