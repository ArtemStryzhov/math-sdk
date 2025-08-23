import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Load all game specific parameters and elements"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "0_0_scatter"
        self.game_name = "sample_scatter"
        self.provider_numer = 0
        self.working_name = "Sample scatter pay (pay anywhere)"
        self.wincap = 5000.0
        self.win_type = "scatter"
        self.rtp = 0.9700
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 6
        # Optionally include variable number of rows per reel
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3 = (8, 9), (10, 11), (12, 30)
        s1, s2, s3 = (4, 4), (5, 5), (6, 6)
        pay_group = {
            (t1, "H1"): 3.0,
            (t2, "H1"): 4.0,
            (t3, "H1"): 24.0,
            (t1, "H2"): 4.0,
            (t2, "H2"): 10.0,
            (t3, "H2"): 30.0,
            (t1, "H3"): 5.0,
            (t2, "H3"): 20.0,
            (t3, "H3"): 50.0,
            (t1, "H4"): 20.0,
            (t2, "H4"): 50.0,
            (t3, "H4"): 100.0,
            (t1, "L1"): 0.5,
            (t2, "L1"): 1.5,
            (t3, "L1"): 4.0,
            (t1, "L2"): 0.8,
            (t2, "L2"): 1.8,
            (t3, "L2"): 8.0,
            (t1, "L3"): 1.0,
            (t2, "L3"): 2.0,
            (t3, "L3"): 10.0,
            (t1, "L4"): 1.6,
            (t2, "L4"): 2.4,
            (t3, "L4"): 16.0,
            (t1, "L5"): 2.0,
            (t2, "L5"): 3.0,
            (t3, "L5"): 20.0,
            (s1, "S"): 6.0,
            (s2, "S"): 10.0,
            (s3, "S"): 200.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"wild": ["W"],
                                "scatter": ["S"], "multiplier": ["M"]}

        self.freespin_triggers = {
            self.basegame_type: {
                4: 15,
                5: 15,
                6: 15,
                7: 15,
                8: 15,
                9: 15,
                10: 15,
            },
            self.freegame_type: {
                3: 5,
                4: 5,
                5: 5,
                6: 5,
                7: 5,
                8: 5,
                9: 5,
                10: 5,
            },
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(
                os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
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
                        # win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10},
                                self.freegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:100, 100:50, 250: 20, 500:20},
                            },
                            "scatter_triggers": {4: 1, 5: 1,},
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
                            "scatter_triggers": {4: 1, 5: 1},
                            "mult_values": {
                                self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10},
                                self.freegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:100, 100:50, 250: 20, 500:20},
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
                                self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10},
                                self.freegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:100, 100:50, 250: 20, 500:20},
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
                            "mult_values": {self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        # win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10},
                                self.freegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:100, 100:50, 250: 20, 500:20},
                            },
                            "scatter_triggers": {4: 5, 5: 5, 6: 5},
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
                            "scatter_triggers": {4: 5, 5: 5, 6: 5},
                            "mult_values": {
                                self.basegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:50, 100:25, 250: 10, 500:10},
                                self.freegame_type: {2: 200, 3: 190, 4:180, 5: 170, 6: 160, 8: 150, 10:100, 12:90, 15: 80, 20: 70, 25:60, 50:100, 100:50, 250: 20, 500:20},
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
