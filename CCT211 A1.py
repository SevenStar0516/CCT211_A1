"""
TO DO:
Grid system
Shoot the enemy with click
two types of enemy: fire-enemy, rock-enemy
fire-enemy can also shoot you
implement platforms
pillar- mario style
"""

import pygame, numpy
import sys
import random

WIDTH = 960
HEIGHT = 540
BACKGROUND = pygame.image.load("background.png")
pygame.display.set_caption("Can You Catch The Timing?")


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(Sprite):
    def __init__(self, startx, starty):
        super().__init__("p1_front.png", startx, starty)
        self.stand_image = self.image
        self.jump_image = pygame.image.load("p1_jump.png")

        self.walk_cycle = [pygame.image.load(f"p1_walk{i:0>2}.png") for i in range(1, 12)]
        self.animation_index = 0
        self.facing_left = False

        self.speed = 4
        self.jumpspeed = 20
        self.vsp = 0  # vertical speed
        self.gravity = 1
        self.min_jumpspeed = 3
        self.prev_key = pygame.key.get_pressed()

    def update(self, all_plat):
        hsp = 0  # horizontal speed

        onground = self.check_collision(0, 1, all_plat)

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.facing_left = True
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:
            self.facing_left = False
            self.walk_animation()
            hsp = self.speed
        else:
            self.image = self.stand_image

        if key[pygame.K_UP] and (onground):
            self.vsp = -self.jumpspeed

        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.vsp < -self.min_jumpspeed:
                self.vsp = -self.min_jumpspeed

        self.prev_key = key

        if self.vsp < 10 and not (onground):
            self.jump_animation()
            self.vsp += self.gravity

        if self.vsp > 0 and (onground):
            self.vsp = 0

        self.move(hsp, self.vsp, all_plat)

    def move(self, x, y, all_plat):
        dx = x
        dy = y

        while self.check_collision(0, dy, all_plat):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy, all_plat):
            dx -= numpy.sign(dx)

        # Check for screen boundaries
        if self.rect.left < 0:
            dx = max(dx, -self.rect.left)
        elif self.rect.right > WIDTH:
            dx = min(dx, WIDTH - self.rect.right)

        self.rect.move_ip([dx, dy])

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def check_collision(self, x, y, all_plat):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, all_plat)
        self.rect.move_ip([-x, -y])
        return collide


class Enemy(Sprite):
    def __init__(self, startx, starty):
        super().__init__("stone.png", startx, starty)
        self.speed = 2

    def update(self, contactable):
        # Move the box horizontally
        self.rect.x += self.speed

        # If the box goes off the screen, reset its position
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0

        # Check for collisions with static boxes and change direction if needed
        collisions = pygame.sprite.spritecollide(self, contactable, False)
        if collisions:
            self.speed *= -1

    def player_collisions(self):
        self.speed *= -1


class Fire(Sprite):
    def __init__(self, startx, starty, speedx, speedy, player):
        super().__init__("enemy.png", startx, starty)
        self.speedx = speedx
        self.speedy = speedy

        self.player = player
        self.bullet_timer = 0

    def update(self, contactable, bullets):
        self.bullet_timer += 0.5
        if self.bullet_timer >= 60:  # Change 60 to control the firing interval (60 frames per second)
            bullet = Bullet(self.player)
            bullet.rect.center = self.rect.center
            bullet.direction_x = -self.speedx if self.player.rect.centerx < self.rect.centerx else self.speedx
            bullet.direction_y = self.speedy
            bullets.add(bullet)
            self.bullet_timer = 0


class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """

    def __init__(self, player):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.player = player
        self.image = pygame.Surface([10, 10])

        self.image.fill(pygame.color.THECOLORS['red'])

        self.rect = self.image.get_rect()
        self.direction_x = 0
        self.direction_y = 0

    def update(self):
        """ Move the bullet. """
        self.rect.x += (3 * self.direction_x)
        self.rect.y += (3 * self.direction_y)


class Platform(Sprite):
    def __init__(self, startx, starty):
        super().__init__("platform1.png", startx, starty)


class Teleport(Sprite):
    def __init__(self, startx, starty):
        super().__init__("teleport.png", startx, starty)


class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("boxAlt.png", startx, starty)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 25)

    current_level = 1

    player = Player(50, 390)

    # Sprite groups
    all_plat = pygame.sprite.Group()
    contactable = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    teleport_group = pygame.sprite.Group()
    stone = pygame.sprite.Group()
    fire = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    box_group_lv_2 = pygame.sprite.Group()
    box_group_lv_3 = pygame.sprite.Group()

    # Platform for all level
    platform_group.add(Platform(480, 490))

    # level 1 objects
    teleport_group.add(Teleport(920, 390))
    all_plat.add(platform_group)
    contactable.add(teleport_group)

    # text for level 1
    text = font.render("Two types of enemy: fire-enemy, rock-enemy.", True, (255, 255, 255))
    text2 = font.render("Fire-enemy can shoot you, and rock-enemy can move and crush you.", True, (255, 255, 255))
    text3 = font.render("Colliding with Fire enemies does not kill, but hitting Rock enemies and bullets does.", True, (255, 255, 255))
    text4 = font.render("If you die, you will be reborn at your spawn point.", True, (255, 255, 255))
    text5 = font.render("Enter teleport to enter the next level.", True, (255, 255, 255))

    ending_text1 = font.render("Congratulations! You've completed all levels.", True, (255, 255, 255))
    ending_text2 = font.render("If you want to play again, just enter the portal", True, (255, 255, 255))
    ending_text3 = font.render("and it will take you back to Level 2", True, (255, 255, 255))

    # level 2 objects
    box_group_lv_2.add(Box(250, 405))
    box_group_lv_2.add(Box(250, 335))
    box_group_lv_2.add(Box(250, 265))

    box_group_lv_2.add(Box(550, 405))
    box_group_lv_2.add(Box(550, 335))

    box_group_lv_2.add(Box(850, 405))
    box_group_lv_2.add(Box(850, 335))
    box_group_lv_2.add(Box(850, 265))

    # level 3 objects
    for by in range(35, 305, 70):
        box_group_lv_3.add(Box(225, by))
    for bx in range(295, 960, 70):
        box_group_lv_3.add(Box(bx, 35))

    box_group_lv_3.add(Box(435, 265))
    box_group_lv_3.add(Box(575, 265))

    box_group_lv_3.add(Box(435, 405))
    for by in range(105, 245, 70):
        box_group_lv_3.add(Box(645, by))

    for by in range(405, 195, -70):
        box_group_lv_3.add(Box(785, by))

    box_group_lv_3.add(Box(925, 245))

    done = True

    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False

        screen.blit(BACKGROUND, (0, 0))

        player.update(all_plat)
        stone.update(contactable)
        fire.update(contactable, bullets)
        bullets.update()

        for bullet in bullets:

            # Remove the bullet if it flies up off the screen
            if bullet.rect.x > WIDTH:
                bullets.remove(bullet)

        for block in contactable:
            # See if it hit a block
            bullet_hits_list = pygame.sprite.spritecollide(
                block, bullets, True)

            # For each block hit, remove the bullet and add to the score
            for bullet in bullet_hits_list:
                bullets.remove(bullet)

        if current_level == 1:
            all_plat.draw(screen)
            teleport_group.draw(screen)
            player.draw(screen)
            if pygame.sprite.spritecollideany(player, teleport_group):
                current_level = 2
                player.rect.center = (50, 390)
                contactable.add(box_group_lv_2)
                contactable.add(platform_group)
                all_plat.add(box_group_lv_2)
                stone.empty()
                stone.add(Enemy(550, 245))
                fire.add(Fire(250, 215, 1,0, player))
                fire.add(Fire(550, 285, 1,0, player))
                fire.add(Fire(780, 15, 0,2, player))

            # Display instruction text on the first level
            screen.blit(text, (WIDTH // 14, HEIGHT // 4))
            screen.blit(text2, (WIDTH // 14, HEIGHT // 4 + 40))
            screen.blit(text3, (WIDTH // 14, HEIGHT // 4 + 80))
            screen.blit(text4, (WIDTH // 14, HEIGHT // 4 + 120))
            screen.blit(text5, (WIDTH // 14, HEIGHT // 4 + 160))

        elif current_level == 2:
            stone.draw(screen)
            player.draw(screen)
            teleport_group.draw(screen)
            all_plat.draw(screen)
            stone.draw(screen)
            fire.draw(screen)
            bullets.draw(screen)

            if pygame.sprite.spritecollideany(player, bullets):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, stone):
                player.rect.center = (50, 390)

            if pygame.sprite.spritecollideany(player, teleport_group):
                all_plat.remove(box_group_lv_2)
                all_plat.add(box_group_lv_3)
                contactable.remove(box_group_lv_2)
                contactable.add(box_group_lv_3)
                current_level = 3
                player.rect.center = (50, 390)
                stone.empty()
                fire.empty()
                bullets.empty()
                fire.add(Fire(575, 215, 1, 0, player))
                fire.add(Fire(835, 85, 0, 2, player))
                stone.add(Enemy(500, 425))

        elif current_level == 3:
            stone.draw(screen)
            player.draw(screen)
            teleport_group.draw(screen)
            all_plat.draw(screen)
            stone.draw(screen)
            fire.draw(screen)
            bullets.draw(screen)

            if pygame.sprite.spritecollideany(player, bullets):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, stone):
                player.rect.center = (50, 390)

            if pygame.sprite.spritecollideany(player, teleport_group):
                all_plat.remove(box_group_lv_3)
                contactable.remove(box_group_lv_3)
                current_level = 4
                player.rect.center = (50, 390)
                stone.empty()
                fire.empty()
                bullets.empty()

        elif current_level == 4:
            player.draw(screen)
            all_plat.draw(screen)
            teleport_group.draw(screen)
            screen.blit(ending_text1, (WIDTH // 4, HEIGHT // 4))
            screen.blit(ending_text2, (WIDTH // 4, HEIGHT // 4 + 40))
            screen.blit(ending_text3, (WIDTH // 4, HEIGHT // 4 + 80))

            if pygame.sprite.spritecollideany(player, teleport_group):
                current_level = 2
                player.rect.center = (50, 390)
                contactable.add(box_group_lv_2)
                contactable.add(platform_group)
                all_plat.add(box_group_lv_2)
                stone.empty()
                stone.add(Enemy(550, 245))
                fire.add(Fire(250, 215, 1, 0, player))
                fire.add(Fire(550, 285, 1, 0, player))
                fire.add(Fire(780, 15, 0, 2, player))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
