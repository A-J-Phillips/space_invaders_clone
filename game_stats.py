import json

class GameStats:
    """Track game statistics."""

    def __init__(self, si_game):
        """Initialise statistics."""
        self.settings = si_game.settings
        self.reset_stats()
        # Start the game in an inactive state.
        self.game_active = False
        # A high score that should not be reset.
        self.high_score = self.current_high_score()

    def reset_stats(self):
        """Initialise statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = int(0)
        self.level = 1

    def update_high_score(self):
        """Define and update the high score using json."""
        high_score = self.high_score
        filename = "high_score.json"
        with open(filename, "w") as f:
            json.dump(high_score, f)

    def current_high_score(self):
        """Retrieve the current high score."""
        filename = "high_score.json"
        with open(filename, "r") as f:
            high_score = json.load(f)

        return int(high_score)
