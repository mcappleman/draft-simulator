#!/usr/bin/env python3
"""
Script to run multiple draft simulations and analyze results.
"""

import pandas as pd
from draft_simulator import FantasyDraftSimulator
from collections import Counter
import random

def run_multiple_simulations(num_simulations=10):
    """Run multiple draft simulations and analyze the results."""
    
    print(f"Running {num_simulations} draft simulations...")
    print("="*60)
    
    # Store all results
    all_results = []
    player_selections = Counter()
    
    for i in range(num_simulations):
        print(f"Simulation {i+1}/{num_simulations}")
        
        # Use different seeds for each simulation
        seed = random.randint(1, 10000)
        
        # Initialize simulator
        simulator = FantasyDraftSimulator(
            'inputs/Draft 2025 - Available Players.csv',
            'inputs/Draft 2025 - Draft.csv'
        )
        
        # Run simulation
        results = simulator.simulate_draft(seed=seed)
        
        # Count player selections (excluding keepers)
        for result in results:
            if result['Type'] == 'Draft':
                player_selections[result['Player']] += 1
        
        all_results.append(results)
    
    print("\n" + "="*60)
    print("PLAYER SELECTION FREQUENCY")
    print("="*60)
    
    # Show most frequently selected players
    print("\nMost Frequently Selected Players:")
    print("-" * 40)
    for player, count in player_selections.most_common(20):
        percentage = (count / num_simulations) * 100
        print(f"{player:25} - {count:2d} times ({percentage:5.1f}%)")
    
    # Show players selected in every simulation
    print("\nPlayers Selected in Every Simulation:")
    print("-" * 40)
    always_selected = [player for player, count in player_selections.items() if count == num_simulations]
    for player in always_selected:
        print(f"{player}")
    
    # Show players selected in most simulations (80%+)
    print("\nPlayers Selected in 80%+ of Simulations:")
    print("-" * 40)
    frequently_selected = [(player, count) for player, count in player_selections.items() 
                          if (count / num_simulations) >= 0.8 and count < num_simulations]
    for player, count in frequently_selected:
        percentage = (count / num_simulations) * 100
        print(f"{player:25} - {count:2d} times ({percentage:5.1f}%)")
    
    # Position breakdown
    print("\nPosition Breakdown of Most Selected Players:")
    print("-" * 40)
    
    # Get position data for top players
    simulator = FantasyDraftSimulator(
        'inputs/Draft 2025 - Available Players.csv',
        'inputs/Draft 2025 - Draft.csv'
    )
    
    position_counts = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'K': [], 'DST': []}
    
    for player, count in player_selections.most_common(30):
        # Find player position
        player_data = simulator.available_players[
            simulator.available_players['Name Formula'] == player
        ]
        if not player_data.empty:
            position = player_data.iloc[0]['Position']
            percentage = (count / num_simulations) * 100
            position_counts[position].append((player, count, percentage))
    
    for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
        if position_counts[position]:
            print(f"\n{position}:")
            for player, count, percentage in position_counts[position][:5]:
                print(f"  {player:20} - {count:2d} times ({percentage:5.1f}%)")

if __name__ == "__main__":
    run_multiple_simulations(20)  # Run 20 simulations
