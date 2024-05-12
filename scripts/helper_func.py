import os
from scripts.classes import *
import pygame as pg

BASE_IMG_PATH = 'data/images/'


def load_image(path):
    temp = pg.image.load(BASE_IMG_PATH + path)
    img =  pg.image.tostring(temp, "RGBA", True)

    return [img, temp.get_width(), temp.get_height()]


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
class Rect:
    def __init__(self, x, y, w, h):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
    
    @property
    def centerx(self):
        return self._x + self._w / 2
    
    @centerx.setter
    def centerx(self, value):
        self._x = value + self._w /2
    
    @property
    def centery(self):
        return self._y + self._h / 2
    
    @centery.setter
    def centery(self, value):
        self._y = value - self._h/2
    
    @property
    def top(self):
        return self._y + self._h
    
    @top.setter
    def top(self, value):
        self._y = value - self._h
    
    @property
    def left(self):
        return self._x
    
    @left.setter
    def left(self, value):
        self._x = value
    
    @property
    def bottom(self):
        return self._y
    
    @bottom.setter
    def bottom(self, value):
        self._y = value
        
    @property
    def right(self):
        return self._x + self._w
    
    @right.setter
    def right(self, value):
        self._x = value - self._w
    
    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, value):
        self._w = value
    
    @property
    def h(self):
        return self._h
    
    @h.setter
    def h(self, value):
        self._h = value
    
    def colliderect(self, rect):
        
        # Calculate max horizontal distance
        max_h_distance = max(abs(self.right - rect.left),
                             abs(self.left - rect.right))
        
        # Calculate max vertical distance
        max_v_distance = max(abs(self.bottom - rect.top),
                             abs(self.top - rect.bottom))
        
        
        # Detect collision
        h_collid = max_h_distance < (self.w + rect.w)
        v_collid = max_v_distance < (self.h + rect.h)
        
        collid = (h_collid and v_collid)
        return collid
