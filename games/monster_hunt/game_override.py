try:
    from .game_executables import GameExecutables
except ImportError:
    from game_executables import GameExecutables

try:
    from src.calculations.statistics import get_random_outcome
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is used to override or extend universal state.py functions.
    Handles Ninja Rabbit specific mechanics like sticky scatter symbols and bonus game logic.
    """

    def reset_book(self):
        super().reset_book()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_wild_multiplier],      # Golden Carrot
            "S": [self.assign_scatter_multiplier],   # Rabbit
            "B": [self.assign_bonus_property],       # Bonus symbol
        }

    def assign_wild_multiplier(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol (Golden Carrot)."""
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            # Wild symbols with moderate multipliers for target RTP
            possible_multipliers = [1, 1, 1, 2, 2]  # Mostly 1x, some 2x
            multiplier_value = get_random_outcome(
                {mult: 80 if mult == 1 else 20 for mult in possible_multipliers}  # 80% chance of 1x, 20% chance of 2x
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def assign_scatter_multiplier(self, symbol) -> dict:
        """Assign multiplier value to Scatter symbol (Rabbit)."""
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            # Scatter symbols with moderate multipliers for target RTP
            possible_multipliers = [1, 1, 1, 1, 2, 2, 2]  # Mostly 1x, some 2x
            multiplier_value = get_random_outcome(
                {mult: 75 if mult == 1 else 25 for mult in possible_multipliers}  # 75% chance of 1x, 25% chance of 2x
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def assign_bonus_property(self, symbol) -> dict:
        """Assign properties to Bonus symbol."""
        # Bonus symbol can only appear in base game
        if self.gametype == self.config.basegame_type:
            symbol.assign_attribute({"bonus": True})
        else:
            # In free games, bonus symbols become regular symbols or are replaced
            pass

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

    def handle_sticky_scatter_symbols(self):
        """Handle sticky scatter symbols in bonus games."""
        if self.gametype == self.config.freegame_type:
            # In bonus games, S symbols become sticky
            # They can expand on every spin if they participate in winning combinations
            # If a new S symbol lands below an existing one, the upper one gets removed
            self.manage_sticky_scatter_positions()

    def manage_sticky_scatter_positions(self):
        """Manage positions of sticky scatter symbols in bonus games."""
        # Find all scatter symbols
        scatter_positions = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "S":
                    scatter_positions.append((reel, row))
        
        # Sort by reel and row to handle overlapping
        scatter_positions.sort(key=lambda x: (x[0], x[1]))
        
        # Remove upper scatter if new one lands below
        for i, (reel, row) in enumerate(scatter_positions):
            for j, (other_reel, other_row) in enumerate(scatter_positions):
                if i != j and reel == other_reel and row < other_row:
                    # Remove the upper scatter symbol
                    # In a real implementation, you'd mark it for removal or replace it
                    pass
