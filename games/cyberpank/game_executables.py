"""
Game-specific executables.
Правила:
1) Під час FREE SPINS, якщо на спіні випав MULTIPLIER і спін виграшний,
   значення MULTIPLIER одразу входить у розрахунок цього ж спіну, а також додається
   до тотального множника раунду (global_multiplier) для наступних спінів раунду.
2) У scatter-pay скаттери (S) не вибухають і рахуються тільки ПІСЛЯ завершення тумблів.
"""

from copy import copy

from .game_calculations import GameCalculations
from src.calculations.scatter import Scatter
from .game_events import send_mult_info_event
from src.events.events import (
    set_win_event,
    set_total_event,
    fs_trigger_event,
    update_tumble_win_event,
    update_global_mult_event,
    update_freespin_event,
)


class GameExecutables(GameCalculations):
    """Game specific executable functions. Used for grouping commonly used/repeated applications."""

    # -------------------- helpers --------------------

    def _sum_new_multiplier_values(self, mult_info, board_mult):
        """
        Обережно дістаємо суму значень MULTIPLIER на полі.
        Пріоритет: беремо з mult_info (якщо там є 'value'), інакше використовуємо board_mult:
        - якщо board_mult > 1, припускаємо що це сума мультиплікаторів цього спіну;
        - якщо board_mult <= 1, вважаємо що нових мультиплікаторів немає.
        """
        sum_new = 0.0
        if isinstance(mult_info, (list, tuple)):
            for item in mult_info:
                # Очікуваний формат: dict із ключем 'value' або числове значення
                try:
                    if isinstance(item, dict) and "value" in item:
                        sum_new += float(item["value"])
                    elif isinstance(item, (int, float)):
                        sum_new += float(item)
                except Exception:
                    continue

        if sum_new <= 0.0:
            try:
                bm = float(board_mult)
                if bm > 1.0:
                    sum_new = bm
            except Exception:
                pass

        return float(max(0.0, sum_new))

    # -------------------- main logic --------------------

    def set_end_tumble_event(self):
        """
        Наприкінці тумблів:
        - У FREE SPINS множимо виграш на board_mult, а також враховуємо "тотал" множник раунду.
          Нові MULTIPLIER-и цього спіну одразу впливають на підсумок спіну.
          Якщо після множення спін виграшний і на полі були MULTIPLIER-и — додаємо їх суму
          в self.global_multiplier (працюватиме з наступного спіну).
        - У BASE логіка без змін.
        """
        if self.gametype == self.config.freegame_type:
            # 1) Збираємо множники з борда (сума М та їх позиції)
            board_mult, mult_info = self.get_board_multipliers()
            sum_new = self._sum_new_multiplier_values(mult_info, board_mult)

            # 2) Поточний тотальний множник перед цим спіном
            current_total = float(self.global_multiplier) if getattr(self, "global_multiplier", 1) else 1.0

            # 3) Базовий тумбл-він (на момент виклику — вже містить поточний total,
            #    бо get_scatterpays_update_wins() рахує з global_multiplier)
            base_tumble_win = copy(self.win_manager.spin_win)

            # 4) Щоб "нові М" одразу вплинули на цей же спін, масштабуємо ще на
            #    factor_total_adjust = (current_total + sum_new) / current_total
            #    та на board_mult (мультиплікатори цього спіну по борду).
            factor_total_adjust = (current_total + sum_new) / current_total if current_total > 0 else (1.0 + sum_new)
            updated_win = base_tumble_win * float(board_mult) * float(factor_total_adjust)

            # 5) Записуємо фінальний spin_win
            self.win_manager.set_spin_win(updated_win)

            # 6) Якщо спін виграшний і є нові мультиплікатори — накопичуємо їх у тоталі
            if self.win_manager.spin_win > 0 and sum_new > 0:
                # Передаємо у подію "базу" вже з урахуванням тоталу цього спіну,
                # щоб інваріант події лишився: updatedWin == base_win * board_mult
                base_win_for_event = base_tumble_win * float(factor_total_adjust)

                try:
                    send_mult_info_event(
                        self,
                        board_mult,                 # множник борда (сума М цього спіну)
                        mult_info,                  # деталі по клітинках М
                        base_win_for_event,         # базовий win уже з тоталом
                        self.win_manager.spin_win,  # фінальний win після board_mult (і тоталу)
                    )
                    update_tumble_win_event(self)
                finally:
                    # Нарощуємо глобальний множник для наступних спінів раунду
                    self.global_multiplier = current_total + sum_new
                    update_global_mult_event(self)

        # Спільні події завершення
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def update_freespin_amount(self, scatter_key: str = "scatter"):
        """Update current and total freespin number and emit event."""
        self.tot_fs = self.count_special_symbols(scatter_key) * 2
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def get_scatterpays_update_wins(self, *, include_scatter: bool = True):
        """
        Порахуйте Scatter-пей; тут уже застосовується self.global_multiplier до виплати.

        include_scatter=False — використовуємо під час тумблів (ігноруємо S і НЕ вибухаємо їх).
        include_scatter=True  — підсумковий підрахунок (після тумблів) із врахуванням S.
        """
        self.win_data = Scatter.get_scatterpay_wins(
            self.config,
            self.board,
            global_multiplier=self.global_multiplier,
            include_scatter=include_scatter,
        )  # Evaluate wins; для НЕ-S позицій, що заплатили, виставляється explode=True
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])  # Update wallet
        self.emit_tumble_win_events()  # Transmit win information

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        # За цим правилом глобальний множник НЕ скидається кожен спін у FS.
        # self.global_multiplier = 1
        update_global_mult_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
