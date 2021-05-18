import pygame.font
import pygame.image


class Button:

    def __init__(self, ai_game, msg):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        self.play = pygame.image.load('images/play_button.png')
        self.image = pygame.transform.scale(self.play, (150, 150))
        self.rect = self.image.get_rect()

        self.rect.center = self.screen_rect.center

        self._prep_msg(msg)

    def _prep_msg(self, msg):
        self.image = self.image
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.blit(self.image, self.image_rect)
