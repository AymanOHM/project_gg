from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from texture import *
import pygame as pg

class Bullet:
    def __init__(self, x, y, direction, img):
        self.x = x
        self.y = y
        self.direction = direction
        self.img = img
        self.tex = Texture(self.img)
        self.rect = ''

    def render(self):

        self.rect = pg.Rect(self.x, self.y, 5, 5)
        self.tex.draw(self.rect.left, self.rect.right, self.rect.top, self.rect.bottom, self.direction)

    def update(self):
        if self.direction == False:
            self.x += 25
        else:
            self.x -= 25


class Bullets:
    def __init__(self, img):
        self.bullets = []
        self.img = img

    def new_bullet(self,  x, y, direction):
        self.bullets.append(Bullet(x, y, direction, self.img))

    def render(self):
        for bullet in self.bullets:
            bullet.render()

    def update(self):
        for bullet in self.bullets:
            bullet.update()

    def get_bullets(self):
        return self.bullets

