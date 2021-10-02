import pygame
from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 50)

        self.intro_background = pygame.image.load('menu.jpg')
        self.go_background = pygame.image.load('Gameover.jpg')

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                if column == 'A':
                    Ground(self, j, i)
                if column == 'B':
                    Block(self, j, i)
                if column == 'E':
                    Enemy(self, j, i)
                if column == "P":
                    Player(self, j, i)

    def new(self):
        # a new game starts
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def events(self):
        # game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        # game loop updates
        self.all_sprites.update()

    def draw(self):
        # game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        #game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        restart_button = Button(606.5, 480, 338, 95, WHITE, BLACK, 'TRY AGAIN', 70)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()

            self.screen.blit(self.go_background, (0, 0))
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('', True, BLACK)
        title_rect = title.get_rect(x=10, y=10)

        play_button = Button(455, 400, 338, 95, WHITE, BLACK, 'PLAY', 80)
        exit_button = Button(455, 550, 338, 95, WHITE, BLACK, 'EXIT', 80)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
                self.running = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.screen.blit(exit_button.image, exit_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()



g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()
