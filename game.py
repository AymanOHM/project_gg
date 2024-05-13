import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from classes import *
from helper_func import *
from tilemap import *
from clouds import *
from bullet import *
from gun_drawing import draw_player_gun, draw_enemy_gun
from bullet_collision import player_bullet_collision, enemy_bullet_collision

class Game():
    def __init__(self, w=800, h=600):
        self.is_alive = False

        self.player_movement = [False, False]
        self.enemy_movement = [False, False]

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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'gun': load_image('_gun.png'),
            'bullet': load_image('bullet.png')
        }

        self.scroll=[0,0]

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.gun = Texture(self.assets['gun'])

        # Initializing the player character.
        self.player = player(self, (750, 600), (35, 55))
        self.player_gun_direction = False

        # Initializing the enemy character.
        self.enemy = player(self, (80, 600), (35, 55))
        self.enemy_gun_direction = False

        self.bullet_group = Bullets(self.assets['bullet'])
        self.enemy_bullet_group = Bullets(self.assets['bullet'])
        self.player_shoot = False
        self.enemy_shoot = False
        self.tilemap = Tilemap(game=self, tile_size=45)
        self.tilemap.load('map.json')

        # self.bullet = Bullet()


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

        # Drawing the player.
        self.player.move(self.tilemap, [self.player_movement[1] - self.player_movement[0], 0])
        self.player.draw()

        # Drawing the enemy.
        self.enemy.move(self.tilemap, [self.enemy_movement[1] - self.enemy_movement[0], 0])
        self.enemy.draw()

        # Setting the guns of the both the player and the enemy.
        draw_player_gun(self, self.player, self.gun, self.player_gun_direction, self.bullet_group, self.player_shoot)
        draw_enemy_gun(self, self.enemy, self.gun, self.enemy_gun_direction, self.enemy_bullet_group, self.enemy_shoot)

        pg.display.flip()



    def run(self):
        time = pg.time.get_ticks()
        while True:

            # glutMainLoop() or pg loop in this case
            if self.is_alive:

                # I made this if statement to remove the bullets from the bullet_group
                # each 2 seconds so that the game stills fast.
                if pg.time.get_ticks() - time >= 2000:
                    self.bullet_group.bullets = []
                    self.enemy_bullet_group.bullets = []
                    time = pg.time.get_ticks()
                else:
                    pass

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()


                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_LEFT:
                            self.player_movement[0] = True
                            self.player_gun_direction = True
                        if event.key == pg.K_RIGHT:
                            self.player_movement[1] = True
                            self.player_gun_direction = False
                        if event.key == pg.K_UP:
                            self.player.jump()
                        if event.key == pg.K_m:
                            self.player_shoot = True

                        if event.key == pg.K_a:
                            self.enemy_movement[0] = True
                            self.enemy_gun_direction = True
                        if event.key == pg.K_d:
                            self.enemy_movement[1] = True
                            self.enemy_gun_direction = False
                        if event.key == pg.K_w:
                            self.enemy.jump()
                        if event.key == pg.K_x:
                            self.enemy_shoot = True


                    if event.type == pg.KEYUP:
                        if event.key == pg.K_LEFT:
                            self.player_movement[0] = False
                        if event.key == pg.K_RIGHT:
                            self.player_movement[1] = False
                        if event.key == pg.K_m:
                            self.player_shoot = False

                        if event.key == pg.K_a:
                            self.enemy_movement[0] = False
                        if event.key == pg.K_d:
                            self.enemy_movement[1] = False
                        if event.key == pg.K_x:
                            self.enemy_shoot = False

                self.scroll[0] += int(((self.player.rect().centerx + self.enemy.rect().centerx) // 2 - self.display.get_width() / 2 - self.scroll[0]) /30)
                self.scroll[1] += int((self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])/30)

                # Detecting if the enemy or the player is killed.
                if player_bullet_collision(self.player, self.enemy_bullet_group.get_bullets()):
                    self.is_alive = False
                    continue
                if enemy_bullet_collision(self.enemy, self.bullet_group.get_bullets()):
                    self.is_alive = False
                    continue


                self.draw()
                self.clock.tick(60)  # limits FPS to 60

            else:
                self.player = player(self, (750, 600), (35, 55))
                self.player_gun_direction = False
                self.enemy = player(self, (80, 600), (35, 55))
                self.enemy_gun_direction = False

                self.scroll[0] = int(((self.player.rect().centerx + self.enemy.rect().centerx) // 2 - self.display.get_width() / 2 - self.scroll[0]) /30)
                self.scroll[1] = 1000

                # I will ask the user to press enter to start playing.
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()

                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            self.is_alive = True


                    if event.type == pg.KEYUP:
                        if event.key == pg.K_RETURN:
                            self.is_alive = False

                self.draw()
                self.clock.tick(60)  # limits FPS to 60



g = Game(1366, 768)
g.run()
