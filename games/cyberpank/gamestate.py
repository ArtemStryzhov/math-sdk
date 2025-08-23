from .game_override import GameStateOverride
from src.calculations.scatter import Scatter


class GameState(GameStateOverride):
    """Gamestate for a single spin"""

    def run_spin(self, sim: int):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # 1) Перед тумблями — рахуємо БЕЗ скаттерів
            self.get_scatterpays_update_wins(include_scatter=False)
            self.emit_tumble_win_events()  # Transmit win information

            # 2) Тумбли — також БЕЗ скаттерів
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_scatterpays_update_wins(include_scatter=False)

            # 3) УСІ тумбли завершились — тепер рахуємо СКАТТЕРИ (вони не вибухають)
            self.get_scatterpays_update_wins(include_scatter=True)

            # Пост-обробка (множники у FS тощо)
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            # Перевірка входу у FS
            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            # Підготовка спіну FS (НЕ скидає global_multiplier)
            self.update_freespin()
            self.draw_board()

            # 1) Перед тумблями — БЕЗ скаттерів
            self.get_scatterpays_update_wins(include_scatter=False)
            self.emit_tumble_win_events()  # Transmit win information

            # 2) Тумбли — БЕЗ скаттерів
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                # self.update_global_mult()  # (стару механику "per tumble" прибрано)
                self.get_scatterpays_update_wins(include_scatter=False)

            # 3) Після тумблів — рахуємо СКАТТЕРИ один раз (не вибухають)
            self.get_scatterpays_update_wins(include_scatter=True)

            # Пост-обробка спіну (миттєвий + накопичувальний ефекти М у FS)
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            # Ретригери у FS (як було)
            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
