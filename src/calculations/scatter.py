"""Handle win calculation for pay-anywhere games"""

from typing import List, Dict
from collections import defaultdict
from src.calculations.symbol import Symbol
from src.config.config import Config


class Scatter:
    """Collection of Scatter-pays functions."""

    @staticmethod
    def get_central_scatter_position(
        rows_for_overlay: List, winning_positions: List[Dict], max_reels: int, max_rows: int
    ) -> tuple:
        """Return position on screen to display win amount."""
        closest_to_middle = 100
        reel_to_overlay = 0
        row_to_overlay = 0
        for pos in winning_positions:
            reel, row = pos["reel"], pos["row"]
            dist_from_middle = (reel - max_reels / 2) ** 2 + (row - max_rows / 2) ** 2
            if (
                dist_from_middle < closest_to_middle
                and row not in rows_for_overlay
                and len(rows_for_overlay) < max_reels
            ):
                closest_to_middle = dist_from_middle
                reel_to_overlay = reel
                row_to_overlay = row

        return (reel_to_overlay, row_to_overlay)

    @staticmethod
    def get_scatterpay_wins(
        config: Config,
        board: list[list[Symbol]],
        wild_key: str = "wild",
        multiplier_key: str = "multiplier",
        global_multiplier: int = 1,
        *,
        include_scatter: bool = True,   # <— новий прапорець
    ) -> dict:
        """Return win data for all paying symbols (scatter pay-anywhere).

        Правила:
        - У scatter-pay вайлди НЕ підміняють символи (не додаємо W в лічильники).
        - Скаттери (S) НІКОЛИ не вибухають (explode=False),
          і можуть бути повністю виключені з підрахунку під час тумблів (include_scatter=False).
        """
        return_data = {"totalWin": 0.0, "wins": []}
        rows_for_overlay = []
        symbols_on_board = defaultdict(list)
        total_win = 0.0

        scatter_syms = set(config.special_symbols.get("scatter", []))
        wild_syms    = set(config.special_symbols.get(wild_key, []))

        # Розкласти позиції символів на полі
        for reel_idx, reel in enumerate(board):
            for row_idx, symbol in enumerate(reel):
                name = symbol.name
                # Вайлди збираємо, але НЕ додаємо до лічильників інших символів у scatter-pay
                if name in wild_syms:
                    continue
                symbols_on_board[name].append({"reel": reel_idx, "row": row_idx})

        # Порахувати кластери
        for sym in symbols_on_board:
            # Під час тумблів можемо вимикати виплати по S
            if sym in scatter_syms and not include_scatter:
                continue

            win_size = len(symbols_on_board[sym])
            key = (win_size, sym)
            if key in config.paytable:
                # Підсумок мультиплікаторів на клітинках цього кластера (якщо є)
                symbol_mult = 0.0
                for p in symbols_on_board[sym]:
                    cell = board[p["reel"]][p["row"]]
                    if cell.check_attribute(multiplier_key):
                        try:
                            symbol_mult += float(cell.get_attribute(multiplier_key))
                        except Exception:
                            pass

                    # Позначити до вибуху ТІЛЬКИ НЕ-скаттери
                    if sym not in scatter_syms:
                        cell.assign_attribute({"explode": True})

                symbol_mult = max(symbol_mult, 1.0)

                overlay_position = Scatter.get_central_scatter_position(
                    rows_for_overlay, symbols_on_board[sym], len(board), len(board[0])
                )
                rows_for_overlay.append(overlay_position[1])

                pay = float(config.paytable[key])
                win_amount = pay * float(global_multiplier) * symbol_mult

                symbol_win_data = {
                    "symbol": sym,
                    "win": win_amount,
                    "positions": symbols_on_board[sym],
                    "meta": {
                        "globalMult": global_multiplier,
                        "clusterMult": symbol_mult,
                        "winWithoutMult": pay,
                        "overlay": {"reel": overlay_position[0], "row": overlay_position[1]},
                    },
                }
                total_win += win_amount
                return_data["wins"].append(symbol_win_data)

        return_data["totalWin"] = total_win
        return return_data

    @staticmethod
    def record_scatter_wins(gamestate) -> None:
        """Force-file description key generator."""
        for win in gamestate.win_data["wins"]:
            gamestate.record(
                {
                    "kind": len(win["positions"]),
                    "symbol": win["symbol"],
                    "totalMult": int(win["meta"]["globalMult"] + win["meta"]["clusterMult"]),
                    "gametype": gamestate.gametype,
                }
            )
