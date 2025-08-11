"""Game-specific configuration file for Ninja Rabbit game, inherits from src/config/config.py"""

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
        
        # Board and Symbol Properties
        self.paytable = {
            # Low symbols
            (3, "L1"): 0.20, (4, "L1"): 0.50, (5, "L1"): 2.00,
            (3, "L2"): 0.20, (4, "L2"): 0.50, (5, "L2"): 2.00,
            (3, "L3"): 0.30, (4, "L3"): 0.70, (5, "L3"): 3.00,
            (3, "L4"): 0.30, (4, "L4"): 0.70, (5, "L4"): 3.00,
            (3, "L5"): 0.50, (4, "L5"): 1.00, (5, "L5"): 5.00,
            
            # High symbols
            (3, "H1"): 1.00, (4, "H1"): 2.00, (5, "H1"): 8.00,
            (3, "H2"): 1.50, (4, "H2"): 3.00, (5, "H2"): 10.00,
            (3, "H3"): 1.50, (4, "H3"): 5.00, (5, "H3"): 15.00,
            (3, "H4"): 2.00, (4, "H4"): 10.00, (5, "H4"): 20.00,
            
            # Special symbols
            (5, "W"): 25.00,   # Wild (Golden Carrot)
            (5, "S"): 25.00,   # Scatter (Rabbit)
        }

        # 15 predefined paylines starting from leftmost reel
        self.paylines = {
            1: [2, 2, 2, 2, 2],      # Middle horizontal
            2: [1, 1, 1, 1, 1],      # Upper horizontal
            3: [3, 3, 3, 3, 3],      # Lower horizontal
            4: [0, 0, 0, 0, 0],      # Top horizontal
            5: [4, 4, 4, 4, 4],      # Bottom horizontal
            6: [0, 1, 2, 1, 0],      # V shape
            7: [4, 3, 2, 3, 4],      # Inverted V shape
            8: [1, 2, 2, 2, 1],      # U shape
            9: [3, 2, 2, 2, 3],      # Inverted U shape
            10: [0, 1, 1, 1, 0],     # Small U shape
            11: [4, 3, 3, 3, 4],     # Small inverted U shape
            12: [1, 0, 1, 0, 1],     # Zigzag
            13: [3, 4, 3, 4, 3],     # Inverted zigzag
            14: [2, 1, 0, 1, 2],     # Diamond
            15: [2, 3, 4, 3, 2],     # Inverted diamond
        }

        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],           # Golden Carrot
            "scatter": ["S"],        # Rabbit
            "multiplier": ["W", "S"], # Both can have multipliers
            "bonus": ["B"]           # Bonus symbol
        }

        # Free spin triggers
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10},  # 3 or 4 bonus symbols trigger free spins
            self.freegame_type: {2: 3, 3: 5, 4: 8},  # Retrigger possibilities
        }
        
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(
                os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
        
        # Multiplier values for Wild and Scatter symbols
        self.padding_symbol_values = {
            "W": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30}},
            "S": {"multiplier": {2: 100, 3: 50, 4: 50, 5: 50, 10: 30, 15: 20, 20: 10}}
        }

        # Game logic simulation conditions
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
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 10, 3: 20, 4: 50, 5: 20, 10: 50, 15: 20, 20: 10},
                            },
                            "scatter_triggers": {3: 1, 4: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 50, 4: 20},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {
                                    2: 60, 3: 80, 4: 50, 5: 20, 10: 15, 15: 10, 20: 5,
                                },
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 15: 5, 20: 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
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
                name="bonus_3",
                cost=100.0,  # 3 bonus symbols bonus mode costs x100
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.999,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100},  # Force 3 bonus symbols
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 15: 5, 20: 1},
                            },
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus_4",
                cost=300.0,  # 4 bonus symbols bonus mode costs x300
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.999,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 100},  # Force 4 bonus symbols
                            "mult_values": {
                                self.basegame_type: {1: 1},
                                self.freegame_type: {2: 100, 3: 80, 4: 50, 5: 20, 10: 10, 15: 5, 20: 1},
                            },
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
