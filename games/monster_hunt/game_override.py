"""Monster Hunt — game-specific overrides.

Головна зміна: повне відключення ре‑тригерів у bonus/freegame.
"""

from typing import List, Tuple

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
    Розширення універсальної логіки state.py під Monster Hunt.
    - Включає мапу спец-символів.
    - Відключає ре-тригери у фріспіні (як для зловленого бонусу, так і для бонус-баю).
    - Додає помірні мультиплікатори для W/S у freegame.
    """

    # --- Базові перезаписи ----------------------------------------------------

    def reset_book(self):
        super().reset_book()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_wild_multiplier],      # Wild
            "S": [self.assign_scatter_multiplier],   # Scatter
            "B": [self.assign_bonus_property],       # Bonus trigger (тільки в basegame)
        }

    # --- Спец-символи ---------------------------------------------------------

    def assign_wild_multiplier(self, symbol) -> None:
        """Призначення множника для Wild."""
        mult = 1
        if self.gametype == self.config.freegame_type:
            # Переважно 1x, інколи 2x
            # (ймовірності через ваги: 80% на 1x, 20% на 2x)
            mult = get_random_outcome({1: 80, 2: 20})
        symbol.assign_attribute({"multiplier": mult})

    def assign_scatter_multiplier(self, symbol) -> None:
        """Призначення множника для Scatter."""
        mult = 1
        if self.gametype == self.config.freegame_type:
            # Більшість 1x, інколи 2x (75/25)
            mult = get_random_outcome({1: 75, 2: 25})
        symbol.assign_attribute({"multiplier": mult})

    def assign_bonus_property(self, symbol) -> None:
        """Властивість бонус‑символу. Працює лише у базі."""
        if self.gametype == self.config.basegame_type:
            symbol.assign_attribute({"bonus": True})
        # У freegame BONUS не тригерить і не має спец-властивостей.

    # --- Керування повтором симуляцій (залишено, як у вас) --------------------

    def check_repeat(self):
        """Логіка перезапуску спіну згідно дистрибуцій (не змінюємо)."""
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return

    # --- ГОЛОВНЕ: відключення ре-тригерів у freegame --------------------------

    def run_freespin(self):
        """
        Виконуємо freegame без можливості ре‑тригера:
        тимчасово зануляємо конфігні тригери для freegame і повертаємо їх після спіну.
        Це працює як для звичайного бонусу (з бази), так і для bonus buy.
        """
        # Запам'ятати і занулити правила тригерів у фріспіні
        original = dict(self.config.freespin_triggers.get(self.config.freegame_type, {}))
        try:
            self.config.freespin_triggers[self.config.freegame_type] = {}
            # Якщо у вас є механіка sticky/інша — можна викликати її тут або всередині super()
            return super().run_freespin()
        finally:
            # Повернути як було (на випадок подальших спінів/симуляцій)
            self.config.freespin_triggers[self.config.freegame_type] = original

    # --- Додаткові хелпери (опційно; залишимо як у вас) -----------------------

    def handle_sticky_scatter_symbols(self):
        """Приклад: обробка 'липких' scatter у бонусі (не активує ре-тригери)."""
        if self.gametype == self.config.freegame_type:
            self.manage_sticky_scatter_positions()

    def manage_sticky_scatter_positions(self):
        """Демонстраційна логіка для sticky scatter (без видалення/мутації)."""
        scatter_positions: List[Tuple[int, int]] = []
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                try:
                    if self.board[reel][row].name == "S":
                        scatter_positions.append((reel, row))
                except Exception:
                    # На ранніх етапах формування борда елементів може не бути
                    pass

        scatter_positions.sort(key=lambda x: (x[0], x[1]))
        # Якщо потрібно — тут можна реалізувати прибирання верхнього S, якщо нижче приземлився новий.
        # Наразі — no-op, тільки інфраструктура.
        return
