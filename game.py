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

        # OpenGL init
        self.gl_init()

        # Preparations
        glClearColor(72/255,160/255,211/255,1.0) # Sky color
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        
        self.scroll=[0,0]

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.gun = Texture(self.assets['gun'])

        # Initializing the player character.
        self.player = player(game=self,
                             pos=(750, 600),
                             size=(35, 55),
                             speed=(5, 5))
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


        # self.bullet = Bullet()


        glutMainLoop()


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        scroll=self.scroll
        glTranslate(-scroll[0],-scroll[1],0)
        
        self.clouds.update()
        self.clouds.render()

        self.tilemap.render()

        self.scroll[0] += int((self.player.pos[0] - self.w / 2 - self.scroll[0]) /30)
        self.scroll[1] += int((self.player.pos[1] - self.h / 2 - self.scroll[1])/30)


        # Drawing the player.
        self.player.move(self.tilemap, [self.player_movement[1] - self.player_movement[0], 0])
        self.player.draw()
        # Drawing the enemy.
        self.enemy.move(self.tilemap, [self.enemy_movement[1] - self.enemy_movement[0], 0])
        self.enemy.draw()

        # Setting the guns of the both the player and the enemy.
        draw_player_gun(self, self.player, self.gun, self.player_gun_direction, self.bullet_group, self.player_shoot)
        draw_enemy_gun(self, self.enemy, self.gun, self.enemy_gun_direction, self.enemy_bullet_group, self.enemy_shoot)

        glutSwapBuffers()


    def gl_init(self):
        
        # OpenGL Initialization
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
        glutInitWindowPosition(200, 200)
        glutInitWindowSize(self.w, self.h)
        glutCreateWindow(b"gg")
        
        # Define functions
        glutDisplayFunc(self.draw)
        glutKeyboardFunc(self.keyboard_callback)
        glutKeyboardUpFunc(self.keyboardUp_callback)
        glutTimerFunc(1, self.game_timer, 1)
        
        # Enable Texture
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # FOR BLENDING

    def game_timer(self, v):
        self.draw()
        glutTimerFunc(v, self.game_timer, v)
    
    def keyboard_callback(self, key, x, y):
        if key == b"q":
            sys.exit(0)
        if key == b'a':
            self.movement[0] = True
        if key == b'd':
            self.movement[1] = True
        if key == b'w':
            self.player.jump()

    def keyboardUp_callback(self, key, x, y):
        if key == b'a':
            self.movement[0] = False
        if key == b'd':
            self.movement[1] = False



g = Game(1366, 768)
g.run()
