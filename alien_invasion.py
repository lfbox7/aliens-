import sys
from time import sleep

import pygame
import pygame.font

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from drop_down import DropDown
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

import sound_effects as se


class AlienInvasion:

    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.font = pygame.font.Font('fonts/ARCADECLASSIC.TTF', 45)

        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('Alien Invasion')

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        pygame.key.set_repeat(0)
        self.play_button = Button(self, 'Play')

    def main_menu(self):

        menu = True
        selected = "start"

        while menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        selected = 'beginner'
                    elif event.key == pygame.K_UP:
                        selected = 'intermediate'
                    elif event.key == pygame.K_RIGHT:
                        selected = 'expert'
                    elif event.key == pygame.K_DOWN:
                        selected = 'quit'
                    if event.key == pygame.K_RETURN:
                        if selected == 'beginner':
                            self.run_game()
                        if selected == 'intermediate':
                            self.settings.speedup_scale *= 2
                            self.run_game()
                        if selected == 'expert':
                            self.settings.speedup_scale *= 5
                            self.run_game()

                        if selected == 'quit':
                            pygame.quit()
                            quit()

            # Main Menu UI
            self.title = self.text_format("Alien Invasion", 'fonts/ARCADECLASSIC.TTF', 120, (255, 0 ,239))
            if selected == 'beginner':
                self.text_beginner = self.text_format("Beginner", 'fonts/ARCADECLASSIC.TTF', 75, (255, 0, 239))
            else:
                self.text_beginner = self.text_format("Beginner", 'fonts/ARCADECLASSIC.TTF', 75, (255, 255, 255))

            if selected == 'intermediate':
                self.text_intermediate = self.text_format("Intermediate", 'fonts/ARCADECLASSIC.TTF', 75, (255, 0, 239))
            else:
                self.text_intermediate = self.text_format("Intermediate", 'fonts/ARCADECLASSIC.TTF', 75, (255, 255, 255))

            if selected == 'expert':
                self.text_expert = self.text_format("Expert", 'fonts/ARCADECLASSIC.TTF', 75, (255, 0, 239))
            else:
                self.text_expert = self.text_format("Expert", 'fonts/ARCADECLASSIC.TTF', 75, (255, 255, 255))

            if selected == 'quit':
                self.text_quit = self.text_format("QUIT", 'fonts/ARCADECLASSIC.TTF', 75, (255, 0, 239))
            else:
                self.text_quit = self.text_format("QUIT", 'fonts/ARCADECLASSIC.TTF', 75, (255, 255, 255))

            self.title_rect = self.title.get_rect()
            self.beginner_rect = self.text_beginner.get_rect()
            self.intermediate_rect = self.text_intermediate.get_rect()
            self.expert_rect = self.text_expert.get_rect()
            self.quit_rect = self.text_quit.get_rect()

            # Main Menu Text
            self.screen.blit(self.title, (self.settings.screen_width / 2 - (self.title_rect[2] / 2), 80))
            self.screen.blit(self.text_beginner, (self.settings.screen_width / 2 - (self.beginner_rect[2] / 2), 300))
            self.screen.blit(self.text_intermediate, (self.settings.screen_width / 2 - (self.intermediate_rect[2] / 2), 400))
            self.screen.blit(self.text_expert, (self.settings.screen_width / 2 - (self.expert_rect[2] / 2), 500))
            self.screen.blit(self.text_quit, (self.settings.screen_width / 2 - (self.quit_rect[2] / 2), 600))
            pygame.display.update()
            #self.clock.tick(FPS)
            pygame.display.set_caption('Main Menu')

    def run_game(self):
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()

            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            se.bullet_sound.play()

    def _update_bullets(self):
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
            se.alien_sound.play()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.settings.bullets_allowed = self.stats.ships_left + 1
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        self.sb.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def text_format(self, message, textFont, textSize, textColor):
        self.newFont = pygame.font.Font(textFont, textSize)
        self.newText = self.newFont.render(message, 0, textColor)

        return self.newText


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.main_menu()
