"""Game-specific configuration file for Monster Hunt A, inherits from src/config/config.py"""

import os

try:
    from src.config.config import Config
    from src.config.distributions import Distribution
    from src.config.betmode import BetMode
except ImportError:
    # fallback, якщо запускаєш з каталогу гри напряму
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.config.config import Config
    from src.config.distributions import Distribution
    from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

        # Базові ідентифікатори гри
        self.game_id = "monster_hunt_A"
        self.provider_number = 0
        self.working_name = "Monster Hunt A"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9700

        # Стандартні шляхи з базового класу
        self.construct_paths()

        # ВАЖЛИВО: у тебе рілзи лежать у games/monster_hunt_A/reels, а не в library/reels
        # Тому локально перевизначаємо шлях до рілзів:
        self.reels_path = os.path.join(os.path.dirname(__file__), "reels")

        # Розмірність
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels

        # Пейтейбл (включив W/S, і ДОДАВ B з нульовою виплатою — щоб символ реєструвався)
        self.paytable = {
            # Wild
            (3, "W"): 10,  (4, "W"): 20, (5, "W"): 50,
            # High
            (3, "H1"): 10, (4, "H1"): 20, (5, "H1"): 50,
            (3, "H2"): 3,  (4, "H2"): 5,  (5, "H2"): 15,
            (3, "H3"): 2,  (4, "H3"): 3,  (5, "H3"): 10,
            (3, "H4"): 1,  (4, "H4"): 2,  (5, "H4"): 8,
            # Low
            (3, "L1"): 0.5, (4, "L1"): 1,   (5, "L1"): 5,
            (3, "L2"): 0.3, (4, "L2"): 0.7, (5, "L2"): 3,
            (3, "L3"): 0.3, (4, "L3"): 0.7, (5, "L3"): 3,
            (3, "L4"): 0.2, (4, "L4"): 0.5, (5, "L4"): 2,
            (3, "L5"): 0.1, (4, "L5"): 0.3, (5, "L5"): 1,
            # Scatter (для реєстрації — лінійних виплат зазвичай немає, але нехай буде 5oak)
            (5, "S"): 0.0,
            # Bonus (B) — суто щоб символ існував у моделі
            (5, "B"): 0.0,
        }

        # Лінії (твій набір на 20 ліній)
        self.paylines = {
            1:  [0, 0, 0, 0, 0],
            2:  [1, 1, 1, 1, 1],
            3:  [2, 2, 2, 2, 2],
            4:  [0, 1, 2, 1, 0],
            5:  [2, 1, 0, 1, 2],
            6:  [0, 0, 1, 2, 2],
            7:  [2, 2, 1, 0, 0],
            8:  [1, 0, 1, 2, 1],
            9:  [1, 2, 1, 0, 1],
            10: [0, 1, 1, 1, 2],
            11: [2, 1, 1, 1, 0],
            12: [0, 1, 0, 1, 2],
            13: [2, 1, 2, 1, 0],
            14: [1, 1, 0, 1, 1],
            15: [1, 1, 2, 1, 1],
            16: [0, 2, 1, 0, 2],
            17: [2, 0, 1, 2, 0],
            18: [0, 0, 2, 0, 0],
            19: [2, 2, 0, 2, 2],
            20: [1, 0, 0, 0, 1],
        }

        self.include_padding = True

        # Спец-символи
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["W"],   # якщо треба множники з падінгу
            "bonus": ["B"],        # щоб 'B' був офіційно відомий
        }

        # Тригери фріспінів (в бейсі — є; у фріспінах — без ретрігерів)
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 15},
            self.freegame_type: {},  # ретрігерів немає
        }

        # БЕЗПЕЧНА антиципація (включає ключ 'freegame', навіть якщо порожньо)
        base_ant = (min(self.freespin_triggers[self.basegame_type].keys()) - 1) \
            if self.freespin_triggers[self.basegame_type] else 0
        free_ant = (min(self.freespin_triggers[self.freegame_type].keys()) - 1) \
            if self.freespin_triggers[self.freegame_type] else 0

        self.anticipation_triggers = {
            self.basegame_type: base_ant,
            self.freegame_type: free_ant,
        }

        # Рілз-файли
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            full = os.path.join(self.reels_path, f)
            if os.path.exists(full):
                self.reels[r] = self.read_reels_csv(full)
            else:
                # fallback: якщо FR0 відсутній — використати BR0
                if r == "FR0" and "BR0" in self.reels:
                    self.reels[r] = self.reels["BR0"]
                else:
                    raise FileNotFoundError(f"Reel file not found: {full}")

        # Падінг-рілзи для обох типів ігор
        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        # Значення мультиплікаторів з падінгу (за потреби)
        self.padding_symbol_values = {
            "W": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 20: 20, 50: 5}},
            # При бажанні — додай S
            # "S": {"multiplier": {...}}
        }

        # Розклад дистрибуцій (залишив близько до твого варіанту; головне — є ключі для freegame/basegame)
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 20, 10: 50, 20: 20, 50: 10},
                            },
                            "scatter_triggers": {3: 1, 4: 1},  # щоб інколи форсило бонус
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.10,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 50, 4: 20, 5: 5},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 60, 3: 80, 4: 50, 5: 20, 10: 15, 20: 10, 50: 5},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.40,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.50,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {self.basegame_type: {1: 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 60, 10: 100, 20: 90, 50: 50},
                            },
                            "scatter_triggers": {3: 1, 4: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.999,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 20, 4: 10, 5: 2},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 20: 5, 50: 1},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
