# games/monster_hunt_A/game_executables.py

try:
    from src.executables.executables import Executables
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.executables.executables import Executables


class GameExecutables(Executables):
    def evaluate_lines_board(self):
        """
        Обрахунок виграшів по лініях для поточного борда без зовнішнього Lines().
        Правила:
          - Рахуємо зліва направо.
          - Wild(и) замінюють будь‑який платний символ (крім scatter/bonus).
          - Платимо за найбільший збіг на лінії (не сумуємо кілька комбінацій на одній лінії).
          - Окремо враховуємо «чисті» комбінації з Wild, якщо вони є в paytable (напр. (3, "W")).
          - Scatter/Bonus по лініях не платимо (їх логіка — поза цим методом).
        """
        board = self.board                   # форма: [reel][row]
        paylines = self.config.paylines      # dict: id -> [row_idx...]
        paytable = self.config.paytable      # dict: (count, symbol) -> payout
        bet_per_line = getattr(self, "bet_per_line", 1)

        wild_syms = set(self.config.special_symbols.get("wild", []))
        ignore_syms = set(self.config.special_symbols.get("scatter", [])) | \
                      set(self.config.special_symbols.get("bonus", []))

        # Множина платних символів із paytable
        paying_symbols = {sym for (_, sym) in paytable.keys()}

        total_win = 0.0
        win_details = []

        def line_sequence(line_rows):
            # Повертає послідовність символів по лінії зліва направо
            return [board[reel_idx][row_idx] for reel_idx, row_idx in enumerate(line_rows)]

        def leading_count_for_target(seq, target):
            """Скільки поспіль зліва: target або wild (якщо target не спец-символ)."""
            cnt = 0
            for s in seq:
                if s == target:
                    cnt += 1
                elif target not in ignore_syms and s in wild_syms:
                    cnt += 1
                else:
                    break
            return cnt

        def leading_pure_wilds(seq):
            """Скільки поспіль зліва тільки wild-символів."""
            cnt = 0
            for s in seq:
                if s in wild_syms:
                    cnt += 1
                else:
                    break
            return cnt

        # Для кожної лінії шукаємо найкращу комбінацію
        for line_id, rows in paylines.items():
            seq = line_sequence(rows)

            best_line_win = 0.0
            best_detail = None

            # 1) Чисті wild-и (якщо в paytable є записи типу (3, "W"))
            if wild_syms:
                # беремо перший wild як репрезентативний символ виплати
                w = next(iter(wild_syms))
                wc = leading_pure_wilds(seq)
                if wc >= 2:  # поріг виплат у тебе в таблиці починається з 3; залишив >=2 на випадок змін
                    val = paytable.get((wc, w), 0)
                    if val > 0:
                        line_win = val * bet_per_line
                        if line_win > best_line_win:
                            best_line_win = line_win
                            best_detail = {
                                "line": line_id,
                                "symbol": w,
                                "count": wc,
                                "payout": val,
                                "win": line_win,
                            }

            # 2) Кожен платний символ (без scatter/bonus)
            for sym in paying_symbols:
                if sym in ignore_syms:
                    continue
                cnt = leading_count_for_target(seq, sym)
                if cnt >= 3:  # класичний поріг для лінійних слотів
                    val = paytable.get((cnt, sym), 0)
                    if val > 0:
                        line_win = val * bet_per_line
                        if line_win > best_line_win:
                            best_line_win = line_win
                            best_detail = {
                                "line": line_id,
                                "symbol": sym,
                                "count": cnt,
                                "payout": val,
                                "win": line_win,
                            }

            # Додаємо найкращу комбінацію по лінії
            if best_line_win > 0:
                total_win += best_line_win
                if best_detail:
                    self.win_details.append(best_detail)

        self.total_win += total_win
