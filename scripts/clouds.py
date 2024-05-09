import random
from scripts.texture import * 
import scripts.classes as classes
from scripts.helper_func import *

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
        self.tex= Texture(img)
        
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, offset=(0, 0)):
        rect=Rect(self.pos[0]- offset[0] * self.depth, self.pos[1]- offset[1] * self.depth, self.img[1]*8, self.img[2]*8)
        self.tex.draw(rect.left, rect.right, rect.top, rect.bottom)
        
class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 1999, random.random() * 1999), random.choice(cloud_images), random.random() * 0.2 + 0.05, random.random() * 0.6 + 0.2))
        
        self.clouds.sort(key=lambda x: x.depth)
    
    def update(self):
        for cloud in self.clouds:
            cloud.update()
    
    def render(self, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(offset=offset)