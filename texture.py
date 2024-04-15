from OpenGL.GL import *
import pygame as pg

class texture:
    def __init__(self, path):
        temp = pg.image.load('data/images/'+path)
        self.img =   pg.image.tobytes(temp)
        self.id = glGenTextures()

    def bind(self):
        glBindTexture(GL_TEXTURE_2D,self.img)
        