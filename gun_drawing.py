from bullet import *

def draw_player_gun(map, player, gun, gun_direction, bullet_group, shoot):
    global bul
    # Drawing the player gun.
    if not gun_direction:
        gun.draw(player.pos[0] + 20, player.pos[0] + 35,
                      player.pos[1] + 15, player.pos[1] + 28, direction=False)
        # Drawing the bullet at case of shooting and the player looks right.
        if shoot:

            bullet_group.new_bullet(player.rect().centerx + 17, player.rect().centery - 3,
                         gun_direction)
        bullet_group.render()
        bullet_group.update()



    else:
        gun.draw(player.pos[0], player.pos[0] + 15,
                      player.pos[1] + 15, player.pos[1] + 28, direction=True)
        # Drawing the bullet at case of shooting and the player looks left.
        if shoot:
            bullet_group.new_bullet(player.rect().centerx - 21, player.rect().centery - 3,
                         gun_direction)
        bullet_group.render()
        bullet_group.update()


def draw_enemy_gun(map, enemy, gun, gun_direction, bullet_group, shoot):
    global bul
    # Drawing the player gun.
    if not gun_direction:
        gun.draw(enemy.pos[0] + 20, enemy.pos[0] + 35,
                      enemy.pos[1] + 15, enemy.pos[1] + 28, direction=False)
        # Drawing the bullet at case of shooting and the player looks right.
        if shoot:
            bullet_group.new_bullet(enemy.rect().centerx + 17, enemy.rect().centery - 3,
                         gun_direction)
        bullet_group.render()
        bullet_group.update()



    else:
        gun.draw(enemy.pos[0], enemy.pos[0] + 15,
                      enemy.pos[1] + 15, enemy.pos[1] + 28, direction=True)
        # Drawing the bullet at case of shooting and the player looks left.
        if shoot:
            bullet_group.new_bullet(enemy.rect().centerx - 21, enemy.rect().centery - 3,
                         gun_direction)
        bullet_group.render()
        bullet_group.update()
