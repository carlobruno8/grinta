"""Test spatial analysis features."""
import pandas as pd
import pytest
from features.spatial import (
    attack_distribution_by_zone,
    defensive_zone_activity,
    passing_concentration
)


def create_test_events():
    """Create sample events for testing spatial analysis."""
    events = []
    
    # Team 1 (ID: 100) - attacks down right flank
    # Add passes in attacking half, right side (y > 53.33)
    for i in range(10):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Pass',
            'x': 70.0,  # Attacking half
            'y': 60.0,  # Right flank
            'end_x': 75.0,
            'end_y': 62.0
        })
    
    # Add some left flank attacks (y < 26.67)
    for i in range(3):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Pass',
            'x': 70.0,
            'y': 20.0,  # Left flank
            'end_x': 75.0,
            'end_y': 22.0
        })
    
    # Add center attacks
    for i in range(5):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Pass',
            'x': 70.0,
            'y': 40.0,  # Center
            'end_x': 75.0,
            'end_y': 42.0
        })
    
    # Team 2 (ID: 200) - balanced attacks
    for i in range(5):
        events.append({
            'team_id': 200,
            'team_name': 'Team B',
            'type_name': 'Pass',
            'x': 65.0,
            'y': 20.0,  # Left
            'end_x': 70.0,
            'end_y': 22.0
        })
    
    for i in range(5):
        events.append({
            'team_id': 200,
            'team_name': 'Team B',
            'type_name': 'Pass',
            'x': 65.0,
            'y': 40.0,  # Center
            'end_x': 70.0,
            'end_y': 42.0
        })
    
    for i in range(5):
        events.append({
            'team_id': 200,
            'team_name': 'Team B',
            'type_name': 'Pass',
            'x': 65.0,
            'y': 60.0,  # Right
            'end_x': 70.0,
            'end_y': 62.0
        })
    
    # Add some defensive actions for both teams
    # Team 1 high press
    for i in range(8):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Pressure',
            'x': 70.0,  # Opponent's half
            'y': 40.0,
            'end_x': None,
            'end_y': None
        })
    
    # Team 1 low block
    for i in range(3):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Clearance',
            'x': 30.0,  # Own third
            'y': 40.0,
            'end_x': None,
            'end_y': None
        })
    
    # Add some backward passes for Team 1
    for i in range(4):
        events.append({
            'team_id': 100,
            'team_name': 'Team A',
            'type_name': 'Pass',
            'x': 70.0,
            'y': 40.0,
            'end_x': 65.0,  # Backward (end_x < start_x)
            'end_y': 40.0
        })
    
    return pd.DataFrame(events)


def test_attack_distribution():
    """Test attack distribution by zone."""
    df = create_test_events()
    
    # Team 1 (100) should have more right flank attacks
    result = attack_distribution_by_zone(df, 100)
    
    assert result is not None
    assert 'left_flank_attacks_pct' in result
    assert 'center_attacks_pct' in result
    assert 'right_flank_attacks_pct' in result
    
    # Check that percentages sum to ~1.0
    total = (
        result['left_flank_attacks_pct'] +
        result['center_attacks_pct'] +
        result['right_flank_attacks_pct']
    )
    assert abs(total - 1.0) < 0.01, f"Percentages should sum to 1.0, got {total}"
    
    # Team 1 should favor right flank (10 right vs 3 left vs 5 center)
    assert result['right_flank_attacks_pct'] > result['left_flank_attacks_pct']
    assert result['right_flank_attacks_pct'] > result['center_attacks_pct']
    
    print(f"✅ Team A attack distribution:")
    print(f"   Left: {result['left_flank_attacks_pct']*100:.1f}%")
    print(f"   Center: {result['center_attacks_pct']*100:.1f}%")
    print(f"   Right: {result['right_flank_attacks_pct']*100:.1f}%")
    
    # Team 2 (200) should be balanced
    result2 = attack_distribution_by_zone(df, 200)
    assert abs(result2['left_flank_attacks_pct'] - result2['right_flank_attacks_pct']) < 0.1
    
    print(f"\n✅ Team B attack distribution (balanced):")
    print(f"   Left: {result2['left_flank_attacks_pct']*100:.1f}%")
    print(f"   Center: {result2['center_attacks_pct']*100:.1f}%")
    print(f"   Right: {result2['right_flank_attacks_pct']*100:.1f}%")


def test_defensive_positioning():
    """Test defensive zone activity."""
    df = create_test_events()
    
    result = defensive_zone_activity(df, 100)
    
    assert result is not None
    assert 'high_press_actions' in result
    assert 'low_block_actions' in result
    
    # Team 1 has 8 high press actions and 3 low block actions
    assert result['high_press_actions'] == 8
    assert result['low_block_actions'] == 3
    
    print(f"\n✅ Team A defensive positioning:")
    print(f"   High press actions: {result['high_press_actions']}")
    print(f"   Low block actions: {result['low_block_actions']}")


def test_passing_concentration():
    """Test passing patterns analysis."""
    df = create_test_events()
    
    result = passing_concentration(df, 100)
    
    assert result is not None
    assert 'pass_width_spread' in result
    assert 'back_passes_pct' in result
    
    # Should have some backward passes
    assert result['back_passes_pct'] is not None
    assert result['back_passes_pct'] > 0
    
    # Width spread should be positive
    assert result['pass_width_spread'] > 0
    
    print(f"\n✅ Team A passing patterns:")
    print(f"   Width spread: {result['pass_width_spread']:.2f}")
    print(f"   Backward passes: {result['back_passes_pct']*100:.1f}%")


def test_empty_dataframe():
    """Test handling of empty data."""
    df = pd.DataFrame(columns=['team_id', 'type_name', 'x', 'y', 'end_x', 'end_y'])
    
    result = attack_distribution_by_zone(df, 999)
    assert result['left_flank_attacks_pct'] is None
    assert result['attacking_half_actions'] == 0
    
    print("\n✅ Empty dataframe handled correctly")


def test_integration_with_builder():
    """Test that spatial metrics integrate with reasoning builder."""
    try:
        from reasoning.input_schema import TeamMetrics
    except ModuleNotFoundError:
        print("\n⚠️  Skipping integration test (dependencies not installed)")
        return
    
    # Create sample metrics with spatial data
    metrics = TeamMetrics(
        team_id=100,
        team_name="Test Team",
        possession_share=0.55,
        pass_count=400,
        successful_passes=350,
        shot_count=12,
        goals=2,
        left_flank_attacks_pct=0.25,
        center_attacks_pct=0.50,
        right_flank_attacks_pct=0.25,
        attacking_half_actions=120,
        high_press_actions=15,
        low_block_actions=8,
        pass_width_spread=18.5,
        back_passes_pct=0.32
    )
    
    assert metrics.left_flank_attacks_pct == 0.25
    assert metrics.high_press_actions == 15
    assert metrics.pass_width_spread == 18.5
    
    print("\n✅ Spatial metrics integrate with TeamMetrics schema")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Spatial Analysis Features")
    print("=" * 60)
    
    test_attack_distribution()
    test_defensive_positioning()
    test_passing_concentration()
    test_empty_dataframe()
    test_integration_with_builder()
    
    print("\n" + "=" * 60)
    print("✅ All spatial analysis tests passed!")
    print("=" * 60)
