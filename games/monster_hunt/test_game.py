#!/usr/bin/env python3
"""Simple test script for Ninja Rabbit game."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game_config import GameConfig
from gamestate import GameState


def test_game_config():
    """Test the game configuration."""
    print("Testing Game Configuration...")
    
    config = GameConfig()
    
    # Test basic properties
    assert config.game_id == "monster_hunt"
    assert config.working_name == "Monster Hunt"
    assert config.num_reels == 5
    assert config.num_rows == [5, 5, 5, 5, 5]
    assert len(config.paylines) == 15
    assert config.rtp == 0.97
    
    # Test paytable
    assert (5, "W") in config.paytable  # Wild 5-of-a-kind
    assert (5, "S") in config.paytable  # Scatter 5-of-a-kind
    assert (3, "L1") in config.paytable  # Low symbol 3-of-a-kind
    assert (5, "H4") in config.paytable  # High symbol 5-of-a-kind
    
    # Test special symbols
    assert "W" in config.special_symbols["wild"]
    assert "S" in config.special_symbols["scatter"]
    assert "B" in config.special_symbols["bonus"]
    
    print("✓ Game configuration test passed!")


def test_gamestate():
    """Test the game state."""
    print("Testing Game State...")
    
    config = GameConfig()
    gamestate = GameState(config)
    
    # Test basic gamestate properties
    assert hasattr(gamestate, 'config')
    assert hasattr(gamestate, 'win_manager')
    
    print("✓ Game state test passed!")


def test_bonus_mechanics():
    """Test bonus game mechanics."""
    print("Testing Bonus Game Mechanics...")
    
    config = GameConfig()
    
    # Test bonus triggers
    assert 3 in config.freespin_triggers[config.basegame_type]
    assert 4 in config.freespin_triggers[config.basegame_type]
    
    # Test bet modes
    bet_mode_names = [mode.get_name() for mode in config.bet_modes]
    assert "base" in bet_mode_names
    assert "bonus_3" in bet_mode_names
    assert "bonus_4" in bet_mode_names
    
    # Test bonus costs
    for mode in config.bet_modes:
        if mode.get_name() == "bonus_3":
            assert mode.get_cost() == 100.0
        elif mode.get_name() == "bonus_4":
            assert mode.get_cost() == 300.0
    
    print("✓ Bonus mechanics test passed!")


def test_paylines():
    """Test payline configurations."""
    print("Testing Paylines...")
    
    config = GameConfig()
    
    # Test payline structure
    for line_id, line in config.paylines.items():
        assert len(line) == 5  # 5 reels
        assert all(0 <= row < 5 for row in line)  # Valid row indices
    
    # Test specific paylines
    assert config.paylines[1] == [2, 2, 2, 2, 2]  # Middle horizontal
    assert config.paylines[2] == [1, 1, 1, 1, 1]  # Upper horizontal
    assert config.paylines[3] == [3, 3, 3, 3, 3]  # Lower horizontal
    
    print("✓ Paylines test passed!")


def main():
    """Run all tests."""
    print("Running Monster Hunt Game Tests...\n")
    
    try:
        test_game_config()
        test_gamestate()
        test_bonus_mechanics()
        test_paylines()
        
        print("\n🎉 All tests passed! Monster Hunt game is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
