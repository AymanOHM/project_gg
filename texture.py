from OpenGL.GL import *
import pygame as pg
from helper_func import *


class Texture:
    def __init__(self, img):

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # FOR BLENDING

        self.img = img
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # GL_MIRRORED_REPEAT , GL_CLAMP_TO_EDGE, GL_CLAMP_TO_BORDER
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
   

    def bind(self):
        glBindTexture(GL_TEXTURE_2D,self.id)
        glTexImage2D(GL_TEXTURE_2D,
            0,  # mipmap
            GL_RGBA,  # for blinding
            self.img[1], self.img[2],
            0,  # Texture border
            GL_RGBA, GL_UNSIGNED_BYTE, self.img[0])  # texture init step [7]

    def draw(self, left, right, top, bot, player_direction):
        self.bind()
        glBegin(GL_QUADS)
        if not player_direction:
            glTexCoord2f(0, 0); glVertex2f(left, bot)
            glTexCoord2f(0, 1); glVertex2f(left, top)
            glTexCoord2f(1, 1); glVertex2f(right, top)
            glTexCoord2f(1, 0); glVertex2f(right, bot)
        else:
            glTexCoord2f(1, 0); glVertex2f(left, bot)
            glTexCoord2f(1, 1); glVertex2f(left, top)
            glTexCoord2f(0, 1); glVertex2f(right, top)
            glTexCoord2f(0, 0); glVertex2f(right, bot)
        glEnd()
