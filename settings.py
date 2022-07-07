class Settings:
    """A Class to store all settings for the game."""
    def __init__(self):
        """Initialise the game's static settings."""
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_colour = "#00497f"
        # "#c4c1c1"
        self.fullscreen = True

        # Ship settings.
        self.ship_speed = 1.5
        self.ship_limit = 3

        # Bullet Settings.
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_colour = "#d32f2f"
        self.bullets_allowed = 4

        # Alien Settings.
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Score settings.

        self.score_increase = 1.5

        # Difficulty incrementers.
        self.alien_speed_increase = 0.2
        self.fleet_drop_increase = 2.0
        self.fleet_drop_max = 30.0

        self.initialise_dynamic_settings()

    def initialise_dynamic_settings(self):
        """Initialise the settigns that change throughout the game."""
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10.0
        self.alien_points = 50