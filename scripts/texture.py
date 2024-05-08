from OpenGL.GL import *
from scripts.helper_func import *
import random

class Texture:
    def __init__(self, img):

        self.img = img
        
        random_id = random.randint(1, 1000)
        self.id = random_id

        glGenTextures(1, [random_id])
        
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # GL_MIRRORED_REPEAT , GL_CLAMP_TO_EDGE, GL_CLAMP_TO_BORDER
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


    def bind(self):
        glBindTexture(GL_TEXTURE_2D,self.id)
        glTexImage2D(GL_TEXTURE_2D,
            0,  
            GL_RGBA,  
            self.img[1], self.img[2],
            0, 
            GL_RGBA, GL_UNSIGNED_BYTE, self.img[0])

    def draw(self, left, right, top, bot, direction=True):
        self.bind()
        glBegin(GL_QUADS)
        if not direction:
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

#EASE of usage
#   init with image-w-h
#   draw with left right top bo