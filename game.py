import pygame as pg
from OpenGL.GL import *
import sys

class Game():
    def __init__(self, w=600,h=600):
        
        #pygame init
        pg.init()
        pg.display.set_caption("gg")
        self.screen=pg.display.set_mode((w,h),flags= pg.OPENGL | pg.DOUBLEBUF)
        self.clock=pg.time.Clock()
        
        #OpenGL init
        glClearColor(0.2,0.3,0.3,1.0)
    
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #gluPerspective(120,w/h,0.1,100)   #default is ortho unit cube
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
        glLoadIdentity()
        # glRotate(theta,0,0,1)
        # glColor3b(52, 73, 102)

        pg.display.flip()
     

    def run(self):
        
        while True:
        # glutMainLoop() or pygame loop in this case
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()       
            self.draw()
            self.clock.tick(60)  # limits FPS to 60


g=Game()
g.run()