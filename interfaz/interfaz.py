import webbrowser

import pygame as pg


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_width()
        self.image = pg.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                webbrowser.open("https://github.com/")

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))


def assembly_side(surface):

    calc_width = (30 / 100) * surface.get_size()[0]
    calc_height = surface.get_size()[1]

    pg.draw.rect(surface, (13, 17, 23), (0, 150, calc_width, calc_height))

    for y in [60, 120, 120]:
        pg.draw.line(surface, (44, 46, 52), (0, y), (calc_width, y))

    pg.draw.line(
        surface, (48, 51, 59), (calc_width, 0), (calc_width, surface.get_size()[1])
    )
    image = pg.image.load("./meluksito.bmp").convert_alpha()
    image = pg.transform.scale_by(image, 1)
    screen.blit(image, (10, 0))


if __name__ == "__main__":
    pg.init()

    # info = pg.display.Info()  # You have to call this before pygame.display.set_mode()
    # screen_width, screen_height = info.current_w, info.current_h

    github_img = pg.image.load("./a.bmp")
    screen = pg.display.set_mode((1080, 720))
    clock = pg.time.Clock()
    running = True

    github_btn = Button(255, 0, github_img, 0.16)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((28, 30, 36))
        assembly_side(screen)
        github_btn.draw()
        pg.display.flip()
        clock.tick(60)

    pg.quit()
