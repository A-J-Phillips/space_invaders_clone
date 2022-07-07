import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button


class SpaceInvaders:
    """A class to manage game assets and behaviours."""

    def __init__(self):
        """Initialise the game, and create game resources."""
        pygame.init()

        # Connecting the game to the settings module.
        self.settings = Settings()

        # Initialising game statistics.
        self.stats = GameStats(self)

        # Creating the game screen.
        if self.settings.fullscreen:
            # Playing the game in full screen mode.
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        else:
            # Playing the game in windowed mode.
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height)
            )

        # Create an instance of a scoreboard.
        self.sb = Scoreboard(self)

        pygame.display.set_caption("Space Invaders")

        # Establishing the player ship.
        self.ship = Ship(self)
        # Creating a group for bullets.
        self.bullets = pygame.sprite.Group()
        # Creating a group for Aliens
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Create a play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            # Update the visible screen. Must be done last in the run_game function.
            self._update_screen()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
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

    def _check_keydown_events(self, event):
        """Respond to keydown events (keypresses)."""
        if event.key == pygame.K_RIGHT:
            # Move ship to the right.
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            if not self.stats.game_active:
                self._start_game()

    def _check_keyup_events(self, event):
        """Respond to keyup events (key releases)."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Respond to player clicking the 'play' button."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Start a new game when the player clicks the play button.
            if self.play_button.rect.collidepoint(mouse_pos):
                self._start_game()

    def _start_game(self):
        """Start the game when if either the play button is pressed, or the P key is pressed."""
        # Reset the game statistics and settings.
        self.stats.reset_stats()
        self.settings.initialise_dynamic_settings()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # Remove any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet and centre the ship.
        self._create_fleet()
        self.ship.centre_ship()

        # Hide the mouse.
        pygame.mouse.set_visible(False)

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            # Reduce ammo count by one.
            self.sb.ammo_count -= 1
            self.sb.prep_ammo()

    def _update_bullets(self):
        """Update position of bullets and remove old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Delete bullets that have gone off screen.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
                # Increase the ammo count when a bullet disappears.
                self.sb.ammo_count += 1
                self.sb.prep_ammo()

        # Repopulate the fleet once a wave is destroyed.
        self._check_bullet_collision()

    def _check_bullet_collision(self):
        """Respond to bullets hitting objects."""
        # Check for bullets that have hit aliens. If so, remove the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        # Increase score if an alien is shot.
        if collisions:
            # Ensure that score is added for every alien hit.
            for alien in collisions.values():
                self.stats.score += self.settings.alien_points * len(alien)
            self.sb.prep_score()
            self.sb.check_high_score()

            # Add bullets to the ammo counter.
            self.sb.ammo_count += 1
            self.sb.prep_ammo()

        # Check if there are any aliens left in the aliens sprite group.
        if not self.aliens:
            self._new_wave()

            # Increase level indicator.
            self.stats.level += 1
            self.sb.prep_level()

    def _new_wave(self):
        """Create a new wave of aliens with increased stats."""
        # Destroy existing bullets and create new fleet with increased speed.
        self.bullets.empty()
        self.settings.alien_speed += self.settings.alien_speed_increase
        # Increase the score value without adding a decimal to the scoreboard
        self.settings.alien_points = int(self.settings.alien_points * self.settings.score_increase)
        if self.settings.fleet_drop_speed > self.settings.fleet_drop_max:
            self.settings.fleet_drop_speed += self.settings.fleet_drop_increase
        self._create_fleet()

    def _update_aliens(self):
        """Update the positions of all aliens in the fleet."""
        self.fleet_direction = 1

        # Check if the fleet is at an edge, then update the positions of all aliens in the fleet.
        self._check_fleet_edges()
        self.aliens.update()
        self._check_aliens_win()


    def _check_aliens_win(self):
        """Check if aliens collide with either the ship or the bottom of the screen."""
        # Check for alien and ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Check if aliens hit the bottom of the screen.
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break


    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        # Decrement ships_left and update scoreboard display.
        self.stats.ships_left -= 1
        self.sb.prep_ships()

        # Check if the game is still active.
        if self.stats.ships_left > 0:
            # Remove any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and centre the new ship.
            self._create_fleet()
            self.ship.centre_ship()

            # Pause the game.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create a fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that can fit onto the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        # Create an alien and place it in the row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed

        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update the images on screen and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_colour)
        self.ship.blitme()

        # Draw bullets onto the screen.
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        # Draw a scoreboard onto the screen.
        self.sb.show_score()

        # Create a play button at the start of the game.
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible.
        pygame.display.flip()


if __name__ == "__main__":
    # Make a game instance, and run the game.
    si = SpaceInvaders()
    si.run_game()