import os

import pygame as pg

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    temp = pg.image.load(BASE_IMG_PATH + path)
    img =   pg.image.tobytes(temp,"RGBA",False)

    return [img,temp.get_width(),temp.get_height()]

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images