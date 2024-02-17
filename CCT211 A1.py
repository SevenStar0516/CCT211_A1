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


class Platform(Sprite):
    def __init__(self, startx, starty):
        super().__init__("platform1.png", startx, starty)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    platforms = pygame.sprite.Group()
    platforms.add(Platform( 480, 490))

    done = True
    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False

        screen.blit(BACKGROUND, (0, 0))

        platforms.draw(screen)

        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    main()
