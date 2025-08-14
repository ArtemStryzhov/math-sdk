try:
    from .game_override import GameStateOverride
except ImportError:
    from game_override import GameStateOverride

try:
    from src.calculations.lines import Lines
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.calculations.lines import Lines


class GameState(GameStateOverride):
    """Handles game logic and events for Monster Hunt game."""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Sticky scatters (якщо реалізовані у твоєму override)
            self.handle_sticky_scatter_symbols()

            # Лінії/виплати
            self.evaluate_lines_board()

            # Збір статистики по режимах
            self.win_manager.update_gametype_wins(self.gametype)

            # Запуск фріспінів із бази (3+ бонусів)
            if self.check_fs_condition():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        # --- ВАЖЛИВО: явно переключаємо режим у freegame ---
        prev_mode = self.gametype
        self.gametype = self.config.freegame_type

        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            self.handle_sticky_scatter_symbols()
            self.evaluate_lines_board()

            # Ретрігер фріспінів (2+ бонусів у фріспіні)
            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

        # Повертаємо попередній режим після фріспінів
        self.gametype = prev_mode
        self.end_freespin()

    def check_fs_condition(self):
        """Check if free spins should be triggered based on bonus symbols."""
        bonus_count = self.count_bonus_symbols()

        if self.gametype == self.config.basegame_type:
            # Base game: 3 або 4 бонус-символи → фріспіни
            if bonus_count >= 3:
                return True
        elif self.gametype == self.config.freegame_type:
            # Free game: ретрігер (2+)
            if bonus_count >= 2:
                return True

        return False

    def count_bonus_symbols(self):
        """Count bonus symbols on the current board."""
        bonus_count = 0
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "B":
                    bonus_count += 1
        return bonus_count

    def determine_bonus_type(self):
        """Determine which bonus game to trigger based on bonus symbol count."""
        bonus_count = self.count_bonus_symbols()

        if bonus_count == 3:
            return "carrot_ambush"      # 10 free spins
        elif bonus_count == 4:
            return "ninjutsu_reign"     # 10 free spins
        else:
            return None

    def run_freespin_from_base(self):
        """Trigger free spins from base game with appropriate bonus type."""
        bonus_type = self.determine_bonus_type()
        if bonus_type:
            self.bonus_type = bonus_type
            self.tot_fs = 10
            self.run_freespin()
