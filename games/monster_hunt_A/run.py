"""Main file for generating results for Monster Hunt A."""

# Use relative imports because this file is run as a module:
# python3 -m games.monster_hunt_A.run
from .gamestate import GameState
from .game_config import GameConfig
from .game_optimization import OptimizationSetup

from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


def main():
    # ---------- knobs for quick testing ----------
    num_threads = 4           # ↓ reduce if your CPU struggles
    rust_threads = 8
    batch_size = 2000         # how many sims per temp file chunk
    compression = False       # keep False while debugging (faster, human-readable .jsonl)
    profiling = False

    # keep counts small for quick runs while debugging
    num_sim_args = {
        "base": 500,          # increase later (e.g., 10_000+ per mode)
        "bonus": 500,
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": False,   # turn on after you're happy with sims
        "run_analysis": False,       # generates PAR sheet
        "run_format_checks": False,  # RGS-format verification
    }
    target_modes = list(num_sim_args.keys())

    # ---------- construct objects ----------
    config = GameConfig()
    gamestate = GameState(config)

    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        # sets config.opt_params
        OptimizationSetup(config)

    # ---------- run sims (create books/LUT/force json) ----------
    if run_conditions["run_sims"]:
        print("[RUN] Creating books…")
        create_books(
            gamestate=gamestate,
            config=config,
            num_sim_args=num_sim_args,
            batch_size=batch_size,   # <-- correct param name
            threads=num_threads,
            compress=compression,
            profiling=profiling,
        )

    # write the index.json etc. after sims and/or optimization
    generate_configs(gamestate)

    # ---------- optimizer ----------
    if run_conditions["run_optimization"]:
        print("[RUN] Optimizing…")
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    # ---------- analysis (PAR sheet) ----------
    if run_conditions["run_analysis"]:
        print("[RUN] Analysis…")
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    # ---------- format checks for RGS ----------
    if run_conditions["run_format_checks"]:
        print("[RUN] Format checks…")
        execute_all_tests(config)

    print("[DONE]")


if __name__ == "__main__":
    main()
