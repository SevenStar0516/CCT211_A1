"""
CCT 211 Assignment 1
Introduction of the game:
Two types of enemy: fire-enemy, rock-enemy
Fire-enemy can shoot you, rock-enemy can crash the player
Teleport for next level

Assignment made by Sean Fei and Roy Su
"""

import pygame, numpy
import sys

WIDTH = 960
HEIGHT = 540
BACKGROUND = pygame.image.load("background.png")
pygame.display.set_caption("Can You Catch The Timing?")


# the code for class Sprite taken from lab 4 exercise
class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# the code for class Player taken from lab 4 exercise
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
        self.vsp = 0
        self.gravity = 1
        self.min_jumpspeed = 3
        self.prev_key = pygame.key.get_pressed()

    # Methods for updating player state and animations
    def update(self, all_plat):
        hsp = 0

        # check collision with all platform sprite group
        onground = self.check_collision(0, 1, all_plat)

        # Walk animation and player movement based on key pressed
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

    # code for player movement
    def move(self, x, y, all_plat):
        dx = x
        dy = y

        while self.check_collision(0, dy, all_plat):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy, all_plat):
            dx -= numpy.sign(dx)

        # Check for screen boundaries
        if self.rect.left < 0:
            dx = -self.rect.left
        elif self.rect.right > WIDTH:
            dx = WIDTH - self.rect.right

        self.rect.move_ip([dx, dy])

    # code for player's walking animation
    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    # code for player's jumping animation
    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    # code for collision detection
    def check_collision(self, x, y, all_plat):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, all_plat)
        self.rect.move_ip([-x, -y])
        return collide


# Class for Enemy, inheriting from Sprite
class Enemy(Sprite):
    def __init__(self, startx, starty):
        super().__init__("stone.png", startx, starty)
        self.speed = 2

    # Method for updating enemy state and movement
    def update(self, contactable):
        # Move the sprite horizontally
        self.rect.x += self.speed

        # Check for collisions with static boxes and change direction if needed
        collisions = pygame.sprite.spritecollide(self, contactable, False)
        if collisions:
            self.speed *= -1


# Class for Fire, inheriting from Sprite
class Fire(Sprite):
    def __init__(self, startx, starty, speedx, speedy, player):
        super().__init__("enemy.png", startx, starty)
        self.speedx = speedx
        self.speedy = speedy
        self.player = player
        # Set a timer to control the firing interval
        self.bullet_timer = 60

    def update(self, contactable, bullets):
        # Increment the bullet timer
        self.bullet_timer += 0.5

        if self.bullet_timer >= 60:  # Change 60 to control the firing interval (60 frames per second)
            bullet = Bullet(self.player)
            bullet.rect.center = self.rect.center

            # Determine the bullet's direction based on the relative positions of the player and fire enemy
            bullet.direction_x = -self.speedx if self.player.rect.centerx < self.rect.centerx else self.speedx
            bullet.direction_y = self.speedy
            bullets.add(bullet)

            # Reset the bullet timer after firing
            self.bullet_timer = 0


# Class for Bullet, inheriting from Sprite
class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.image = pygame.Surface([10, 10])

        self.image.fill(pygame.color.THECOLORS['red'])

        self.rect = self.image.get_rect()
        self.direction_x = 0
        self.direction_y = 0

    # Move the bullet.
    def update(self):
        self.rect.x += (3 * self.direction_x)
        self.rect.y += (3 * self.direction_y)


# Class for Platform, inheriting from Sprite
class Platform(Sprite):
    def __init__(self, startx, starty):
        super().__init__("platform1.png", startx, starty)


# Class for Teleport, inheriting from Sprite
class Teleport(Sprite):
    def __init__(self, startx, starty):
        super().__init__("teleport.png", startx, starty)


# Class for box, inheriting from Sprite
class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("boxAlt.png", startx, starty)


# Main game logic
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 25)

    # level variable
    current_level = 1

    # create a player with x and y point.
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

    # Level 1 objects
    teleport_group.add(Teleport(920, 390))
    all_plat.add(platform_group)
    contactable.add(teleport_group)

    # Text for level 1
    text = font.render("Two types of enemy: fire-enemy, rock-enemy.", True, (255, 255, 255))
    text2 = font.render("Fire-enemy can shoot you, and rock-enemy can move and crush you.", True, (255, 255, 255))
    text3 = font.render("Colliding with Fire enemies does not kill, but hitting Rock enemies and bullets does.", True,
                        (255, 255, 255))
    text4 = font.render("If you die, you will be reborn at your spawn point.", True, (255, 255, 255))
    text5 = font.render("Enter teleport to enter the next level.", True, (255, 255, 255))

    # Text for level 4 (ending)
    ending_text1 = font.render("Congratulations! You've completed all levels.", True, (255, 255, 255))
    ending_text2 = font.render("If you want to play again, just enter the portal", True, (255, 255, 255))
    ending_text3 = font.render("and it will take you back to Level 2", True, (255, 255, 255))

    # Level 2 objects
    box_group_lv_2.add(Box(250, 405))
    box_group_lv_2.add(Box(250, 335))
    box_group_lv_2.add(Box(250, 265))

    box_group_lv_2.add(Box(550, 405))
    box_group_lv_2.add(Box(550, 335))

    box_group_lv_2.add(Box(850, 405))
    box_group_lv_2.add(Box(850, 335))
    box_group_lv_2.add(Box(850, 265))

    # Level 3 objects
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

    # Event handling
    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False

        screen.blit(BACKGROUND, (0, 0))

        # Remove bullets that go off the screen
        for bullet in bullets:
            if bullet.rect.x > WIDTH:
                bullets.remove(bullet)

        # Check for collisions between bullets and blocks
        for block in contactable:
            bullet_hits_list = pygame.sprite.spritecollide(
                block, bullets, True)

            # For each block hit, remove the bullet
            for bullet in bullet_hits_list:
                bullets.remove(bullet)

        # Level logic
        if current_level == 1:
            # Draw level 1 elements
            all_plat.draw(screen)
            teleport_group.draw(screen)
            player.draw(screen)

            # Display instruction text on the first level
            screen.blit(text, (WIDTH // 14, HEIGHT // 4))
            screen.blit(text2, (WIDTH // 14, HEIGHT // 4 + 40))
            screen.blit(text3, (WIDTH // 14, HEIGHT // 4 + 80))
            screen.blit(text4, (WIDTH // 14, HEIGHT // 4 + 120))
            screen.blit(text5, (WIDTH // 14, HEIGHT // 4 + 160))

            # Check for player entering the teleport to proceed to the next level
            if pygame.sprite.spritecollideany(player, teleport_group):
                current_level = 2
                # Set up level 2 elements
                player.rect.center = (50, 390)
                contactable.add(box_group_lv_2)
                contactable.add(platform_group)
                all_plat.add(box_group_lv_2)
                stone.empty()
                stone.add(Enemy(550, 245))
                fire.add(Fire(250, 215, 1, 0, player))
                fire.add(Fire(550, 285, 1, 0, player))
                fire.add(Fire(780, 15, 0, 2, player))

        elif current_level == 2:
            # Draw level 2 elements
            stone.draw(screen)
            player.draw(screen)
            teleport_group.draw(screen)
            all_plat.draw(screen)
            stone.draw(screen)
            fire.draw(screen)
            bullets.draw(screen)

            # Check for player collisions with bullets and stone
            if pygame.sprite.spritecollideany(player, bullets):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, stone):
                player.rect.center = (50, 390)

            # Check for player entering the teleport to proceed to the next level
            if pygame.sprite.spritecollideany(player, teleport_group):
                # Set up level 3 elements
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
            # Draw level 3 elements
            stone.draw(screen)
            player.draw(screen)
            teleport_group.draw(screen)
            all_plat.draw(screen)
            stone.draw(screen)
            fire.draw(screen)
            bullets.draw(screen)

            # Check for player collisions with bullets and stone
            if pygame.sprite.spritecollideany(player, bullets):
                player.rect.center = (50, 390)
            if pygame.sprite.spritecollideany(player, stone):
                player.rect.center = (50, 390)

            # Check for player entering the teleport to proceed to the next level
            if pygame.sprite.spritecollideany(player, teleport_group):
                # Set up level 4 elements
                all_plat.remove(box_group_lv_3)
                contactable.remove(box_group_lv_3)
                current_level = 4
                player.rect.center = (50, 390)
                stone.empty()
                fire.empty()
                bullets.empty()

        elif current_level == 4:
            # Draw level 4 elements
            player.draw(screen)
            all_plat.draw(screen)
            teleport_group.draw(screen)
            screen.blit(ending_text1, (WIDTH // 4, HEIGHT // 4))
            screen.blit(ending_text2, (WIDTH // 4, HEIGHT // 4 + 40))
            screen.blit(ending_text3, (WIDTH // 4, HEIGHT // 4 + 80))

            # Check for player entering the teleport to return to level 2
            if pygame.sprite.spritecollideany(player, teleport_group):
                # Set up level 2 elements
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

        # Update game elements
        player.update(all_plat)
        stone.update(contactable)
        fire.update(contactable, bullets)
        bullets.update()
        # Update display
        pygame.display.flip()

        # Cap the frame rate to 60 fps
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
