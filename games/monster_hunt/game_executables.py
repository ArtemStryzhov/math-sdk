try:
    from .game_calculations import GameCalculations
except ImportError:
    from game_calculations import GameCalculations

try:
    from src.calculations.lines import Lines
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.calculations.lines import Lines


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events with Ninja Rabbit mechanics."""
        # First, handle expanding scatter symbols (Rabbit expansion)
        self.expand_scatter_symbols()
        
        # Then evaluate wins with the expanded board
        self.win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)

    def expand_scatter_symbols(self):
        """Expand scatter symbols (Rabbit) upwards and collect wild multipliers."""
        # Find all scatter symbols on the board
        scatter_positions = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "S":
                    scatter_positions.append((reel, row))
        
        # Process each scatter symbol
        for reel, row in scatter_positions:
            if self.should_expand_scatter(reel, row):
                self.expand_single_scatter(reel, row)

    def should_expand_scatter(self, reel, row):
        """Check if scatter symbol should expand (participates in winning combination)."""
        # This is a simplified check - in a real implementation, you'd check if the symbol
        # is part of any winning line combination
        return True  # For now, expand all scatter symbols

    def expand_single_scatter(self, reel, row):
        """Expand a single scatter symbol upwards and collect wild multipliers."""
        original_multiplier = self.board[reel][row].get_attribute("multiplier") if hasattr(self.board[reel][row], "multiplier") else 1
        collected_multiplier = 0
        
        # Expand upwards from current position
        for expand_row in range(row - 1, -1, -1):
            if expand_row >= 0:
                # Check if there's a wild symbol to collect
                if self.board[reel][expand_row].name == "W":
                    wild_mult = self.board[reel][expand_row].get_attribute("multiplier") if hasattr(self.board[reel][expand_row], "multiplier") else 1
                    collected_multiplier += wild_mult
                    # Mark the wild as collected (could be removed or marked as used)
                
                # Mark this position as covered by expanded scatter
                # In a real implementation, you'd create a new symbol or mark the position
                # For now, we'll just update the multiplier
        
        # Update the scatter symbol's multiplier
        total_multiplier = original_multiplier + collected_multiplier
        self.board[reel][row].assign_attribute({"multiplier": total_multiplier})
