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

    def render(self):

        bullet_rect = pg.Rect(self.x, self.y, 5, 5)
        self.tex.draw(bullet_rect.left, bullet_rect.right, bullet_rect.top, bullet_rect.bottom, self.direction)

    def update(self):
        if self.direction == False:
            self.x += 25
        else:
            self.x -= 25


class Bullets:
    def __init__(self):
        self.bullets = []

    def new_bullet(self, x, y, direction, img):
        self.bullets.append(Bullet(x, y, direction, img))

    def render(self):
        for bullet in self.bullets:
            bullet.render()

    def update(self):
        for bullet in self.bullets:
            bullet.update()

