import pygame, numpy

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

class Platform(Sprite):
    def __init__(self, startx, starty):
        super().__init__("platform1.png", startx, starty)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    current_level = 1

    player = Player(280, 280)

    all_plat = pygame.sprite.Group()
    platform_1 = pygame.sprite.Group()
    platform_1.add(Platform(480, 490))
    all_plat.add(platform_1)


    done = True
    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False

        screen.blit(BACKGROUND, (0, 0))

        if current_level == 1:
            player.update(all_plat)
            all_plat.draw(screen)

        player.draw(screen)
        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    main()
