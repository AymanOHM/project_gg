import pygame as pg

def player_bullet_collision(player, bullets):
    for bullet in bullets:
        if pg.Rect.colliderect(player.rect(), bullet):
            return True
    return False


def enemy_bullet_collision(enemy, bullets):
    for bullet in bullets:
        if pg.Rect.colliderect(enemy.rect(), bullet):
            return True
    return False
