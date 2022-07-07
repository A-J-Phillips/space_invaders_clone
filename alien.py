import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A class to represent aliens."""

    def __init__(self, si_game):
        """Initialise the alien and set its starting position."""
        super().__init__()
        self.screen = si_game.screen
        self.settings = si_game.settings

        # Load the alien image and set its rect attributes.
        # The alien_colour attribute was made so that different alien images could appear.
        # This system is currently not working correctly, but this has been left in for future use.
        self.alien_colour = "yellow"
        self.image = pygame.image.load(f"images/alien_{self.alien_colour}.bmp")

        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the aliens horizontal position.
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Move the aliens to the right or left."""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

