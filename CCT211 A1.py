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
pygame.display.set_caption("Adventure")


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
        self.speed = 1
    def update(self, contactable):
        # Move the box horizontally
        self.rect.x += self.speed

        # If the box goes off the screen, reset its position
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left> WIDTH:
            self.rect.right = 0

        # Check for collisions with static boxes and change direction if needed
        collisions = pygame.sprite.spritecollide(self, contactable, False)
        if collisions:
            self.speed *= -1
    def player_collisions(self):
        self.speed *= -1

class Fire(Sprite):
    def __init__(self, startx, starty):
        super().__init__("enemy.png", startx, starty)
        self.speed = 1
    def update(self, contactable):
        # Move the box horizontally
        self.rect.x += self.speed

        # If the box goes off the screen, reset its position
        if self.rect.right< 0:
            self.rect.left = WIDTH
        elif self.rect.left> WIDTH:
            self.rect.right = 0

        # Check for collisions with static boxes and change direction if needed
        collisions = pygame.sprite.spritecollide(self, contactable, False)
        if collisions:
            self.speed *= -1
    def player_collisions(self):
        self.speed *= -1


class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """

    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = pygame.Surface([10, 10])

        self.image.fill(pygame.color.THECOLORS['red'])

        self.rect = self.image.get_rect()

        self.direction = 1 #Going right

    def update(self):
        """ Move the bullet. """
        self.rect.x += (3*self.direction)


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
    font = pygame.font.Font(None, 36)

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
    box_group = pygame.sprite.Group()

    # Platform for all level
    platform_group.add(Platform(480, 490))

    # level 1 objects
    teleport_group.add(Teleport(910, 390))
    all_plat.add(platform_group)
    contactable.add(teleport_group)
    stone.add(Enemy(410, 420))
    fire.add(Fire(650, 420))

    # text for level 1
    text = font.render("Shoot the enemy with a mouse click.", True, (255, 255, 255))
    text2 = font.render("Two types of enemy: fire-enemy, rock-enemy.", True, (255, 255, 255))
    text3 = font.render("Fire-enemy can also shoot you, and rock-enemy can move and crush you.", True, (255, 255, 255))
    text4 = font.render("If you die, you will be reborn at your spawn point.", True, (255, 255, 255))
    text5 = font.render("Enter teleport to enter the next level.", True, (255, 255, 255))

    # level 2 objects
    box_group.add(Box(300,405))
    box_group.add(Box(300, 335))


    done = True
    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False

        screen.blit(BACKGROUND, (0, 0))

        player.update(all_plat)
        stone.update(contactable)
        fire.update(contactable)
        bullets.update()

        for bullet in bullets:

            # Remove the bullet if it flies up off the screen
            if bullet.rect.x > WIDTH:
                bullets.remove(block)
        
        for block in contactable:
            # See if it hit a block
            bullet_hits_list = pygame.sprite.spritecollide(
                block, bullets, True)

            # For each block hit, remove the bullet and add to the score
            for bullet in bullet_hits_list:
                bullets.remove(bullet)

        for enemy in fire:
                if random.random() < 0.003:
                    # Fire a bullet from the enemy
                    bullet = Bullet()
                    # Set the bullet so it is where the player is
                    bullet.rect.x = enemy.rect.x
                    bullet.rect.y = enemy.rect.y + (enemy.rect.height/2)
                    bullet.direction = enemy.speed
                    # Add the bullet to the lists
                    bullets.add(bullet)

        if current_level == 1:
            all_plat.draw(screen)
            teleport_group.draw(screen)
            player.draw(screen)
            stone.draw(screen)
            fire.draw(screen)
            bullets.draw(screen)
            if pygame.sprite.spritecollideany(player, teleport_group):
                current_level = 2
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, bullets):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, stone):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, fire):
                player.rect.center = (50, 390)
        elif current_level == 2:
            player.draw(screen)
            all_plat.draw(screen)


            # Display instruction text on the first level
            screen.blit(text, (WIDTH // 14, HEIGHT // 4))
            screen.blit(text2, (WIDTH // 14, HEIGHT // 4 + 40))
            screen.blit(text3, (WIDTH // 14, HEIGHT // 4 + 80))
            screen.blit(text4, (WIDTH // 14, HEIGHT // 4 + 120))
            screen.blit(text5, (WIDTH // 14, HEIGHT // 4 + 160))

            if pygame.sprite.spritecollideany(player, teleport_group):
                current_level = 2
                player.rect.center = (50, 390)
                all_plat.add(box_group)

        elif current_level == 3:
            box_group.draw(screen)
            player.draw(screen)
            teleport_group.draw(screen)
            all_plat.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
