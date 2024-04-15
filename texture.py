from OpenGL.GL import *
import pygame as pg
from helper_func import *


class Texture:
    def __init__(self,img):
        
        self.img = img
        self.id = glGenTextures(1)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D,self.id)
        glTexImage2D(GL_TEXTURE_2D,
            0,  # mipmap
            3,  # Bytes per pixel
            self.img[1], self.img[2],
            0,  # Texture border
            GL_RGBA, GL_UNSIGNED_BYTE, self.img[0]) # texture init step [7]

    
    def draw(self, left,right,top,bot):
        self.bind()
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(left, top) 
        glTexCoord2f(0, 0); glVertex2f(left, bot)
        glTexCoord2f(1, 1); glVertex2f(right, top)
        glTexCoord2f(1, 0); glVertex2f(right, bot)
        glEnd() 