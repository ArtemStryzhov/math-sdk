"""Game-specific configuration file for Monster Hunt game, inherits from src/config/config.py"""

import os
try:
    from src.config.config import Config
    from src.config.distributions import Distribution
    from src.config.betmode import BetMode
    from src.config.paths import PATH_TO_GAMES
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.config.config import Config
    from src.config.distributions import Distribution
    from src.config.betmode import BetMode
    from src.config.paths import PATH_TO_GAMES


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "monster_hunt"  # Directory name
        self.provider_number = 0
        self.working_name = "Monster Hunt"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9700  # Target RTP between 96-98%
        self.construct_paths()

        # Game Dimensions - 5 reels, 5 rows
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels

        # Paytable
        self.paytable = {
            # Low symbols - Increased from 50% reduction to 30% reduction
            (3, "L1"): 0.14, (4, "L1"): 0.35, (5, "L1"): 1.40,
            (3, "L2"): 0.14, (4, "L2"): 0.35, (5, "L2"): 1.40,
            (3, "L3"): 0.21, (4, "L3"): 0.49, (5, "L3"): 2.10,
            (3, "L4"): 0.21, (4, "L4"): 0.49, (5, "L4"): 2.10,
            (3, "L5"): 0.35, (4, "L5"): 0.70, (5, "L5"): 3.50,

            # High symbols - Increased from 50% reduction to 30% reduction
            (3, "H1"): 0.70, (4, "H1"): 1.40, (5, "H1"): 5.60,
            (3, "H2"): 1.05, (4, "H2"): 2.10, (5, "H2"): 7.00,
            (3, "H3"): 1.05, (4, "H3"): 3.50, (5, "H3"): 10.50,
            (3, "H4"): 1.40, (4, "H4"): 7.00, (5, "H4"): 14.00,

            # Special symbols - Increased from 50% reduction to 30% reduction
            (5, "W"): 17.50,   # Wild - was 12.50, now 17.50
            (5, "S"): 17.50,   # Scatter - was 12.50, now 17.50
        }

        # 15 paylines
        self.paylines = {
            1: [2, 2, 2, 2, 2],
            2: [1, 1, 1, 1, 1],
            3: [3, 3, 3, 3, 3],
            4: [0, 0, 0, 0, 0],
            5: [4, 4, 4, 4, 4],
            6: [0, 1, 2, 1, 0],
            7: [4, 3, 2, 3, 4],
            8: [1, 2, 2, 2, 1],
            9: [3, 2, 2, 2, 3],
            10: [0, 1, 1, 1, 0],
            11: [4, 3, 3, 3, 4],
            12: [1, 0, 1, 0, 1],
            13: [3, 4, 3, 4, 3],
            14: [2, 1, 0, 1, 2],
            15: [2, 3, 4, 3, 2],
        }

        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["W", "S"],
            "bonus": ["B"],
        }

        # Free spin triggers
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},               # base: 3 або 4 бонуси → 10 FS
            self.freegame_type: {2: 3, 3: 5, 4: 8},           # retrigger у фріспіні
        }

        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        # Multiplier values for Wild and Scatter symbols
        self.padding_symbol_values = {
            "W": {"multiplier": {2: 2, 3: 2, 4: 2, 5: 2, 10: 2}},  # Reduced from 100x to 2x
            "S": {"multiplier": {2: 2, 3: 2, 4: 2, 5: 2, 10: 2, 15: 2, 20: 2}},  # Reduced from 100x to 2x
        }

        # Bet modes / Distributions
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
                    # Distribution(
                    #     criteria="wincap",
                    #     quota=0.0005,  # 0.05% for high wins
                    #     win_criteria=self.wincap,
                    #     conditions={
                    #         "reel_weights": {
                    #             self.basegame_type: {"BR0": 1},
                    #             self.freegame_type: {"FR0": 1, "WCAP": 5},
                    #         },
                    #         "mult_values": {
                    #             self.basegame_type: {1: 1},
                    #             self.freegame_type: {2: 2, 3: 3, 4: 4, 5: 3, 10: 5, 15: 4, 20: 3},  # Moderate multipliers
                    #         },
                    #         "scatter_triggers": {3: 1, 4: 2},
                    #         "force_wincap": True,
                    #         "force_freegame": True,
                    #     },
                    # ),
                    Distribution(
                        criteria="freegame",
                        quota=0.08,  # Increased from 5% to 8% for better balance
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 50, 4: 20},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {
                                    2: 1, 3: 1, 4: 1, 5: 1, 10: 1, 15: 1, 20: 1,  # Minimal multipliers
                                },
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.92,  # Adjusted to 92% to balance total to 100%
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},  # Added to prevent KeyError
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_3",
                cost=100.0,  # 3 bonus symbols
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.999,  # 99.9% for bonus mode
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 1, 3: 1, 4: 1, 5: 1, 10: 1, 15: 1, 20: 1},  # Minimal multipliers
                            },
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_4",
                cost=300.0,  # 4 bonus symbols
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.999,  # 99.9% for bonus mode
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 100},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 1, 3: 1, 4: 1, 5: 1, 10: 1, 15: 1, 20: 1},  # Minimal multipliers
                            },
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
