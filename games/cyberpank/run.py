"""Main file for generating results for sample ways-pay game."""

import os
import sys

# === Додаємо і корінь проєкту, і src/ у sys.path ===
# Структура: math-sdk/ (PROJECT_ROOT)
#            ├─ games/cyberpank/...
#            └─ src/...
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
for p in (PROJECT_ROOT, SRC_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

# --- Імпорти з локальної папки games/cyberpank ---
from .gamestate import GameState
from .game_config import GameConfig
from .game_optimization import OptimizationSetup

# --- Імпорти з каталогу src/ (без префікса 'src.')
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from state.run_sims import create_books
from write_data.write_configs import generate_configs


if __name__ == "__main__":

    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True
    profiling = False

    num_sim_args = {
        "base": int(1e4),
        "bonus": int(1e4),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base", "bonus"]

    config = GameConfig()
    gamestate = GameState(config)

    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)  # noqa: F841

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
