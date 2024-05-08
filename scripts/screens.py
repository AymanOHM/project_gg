from scripts.texture import *
from scripts.helper_func import *
class Screen:
    def __init__(self,game,path,pos):
        self.pos=pos
        self.image=game.assets[path]
        self.tex=Texture(self.image)
        self.shake_dir=1
        self.offset=0
        rect=Rect(self.pos[0],self.pos[1]+self.offset,self.image[1],self.image[2]) 
        self.center=[rect.centerx,rect.centery]

    def draw(self):
        rect=Rect(self.pos[0],self.pos[1]+self.offset,self.image[1] - 200,self.image[2] - 200) 
        self.tex.draw(rect.left,rect.right,rect.top,rect.bottom, False)
        self.offset+= self.shake_dir*1
        if abs(self.offset)>50:
            self.offset-= self.shake_dir*1
            self.shake_dir*= -1
        self.center=[rect.centerx,rect.centery]