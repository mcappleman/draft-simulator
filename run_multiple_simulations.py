#!/usr/bin/env python3
"""
Script to run multiple draft simulations and analyze results.
"""

import pandas as pd
from draft_simulator import FantasyDraftSimulator
from collections import Counter
import random
import os
from datetime import datetime

def run_multiple_simulations(num_simulations=10):
    """Run multiple draft simulations and analyze the results."""
    
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
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
        
        # Save individual simulation to CSV
        simulation_filename = f"outputs/simulation_{i+1:03d}_{timestamp}.csv"
        simulator.export_results(results, simulation_filename)
        
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
    
    # Write analysis to markdown file
    analysis_filename = f"outputs/simulation_analysis_{timestamp}.md"
    write_analysis_to_markdown(analysis_filename, num_simulations, player_selections, position_counts, timestamp)
    
    print(f"\nAnalysis written to: {analysis_filename}")
    print(f"Individual simulation CSVs saved to: outputs/")

def write_analysis_to_markdown(filename, num_simulations, player_selections, position_counts, timestamp):
    """Write the simulation analysis to a markdown file."""
    
    with open(filename, 'w') as f:
        f.write(f"# Fantasy Football Draft Simulation Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Number of Simulations:** {num_simulations}\n\n")
        
        f.write("## Player Selection Frequency\n\n")
        
        f.write("### Most Frequently Selected Players\n\n")
        f.write("| Player | Times Selected | Percentage |\n")
        f.write("|--------|----------------|------------|\n")
        for player, count in player_selections.most_common(20):
            percentage = (count / num_simulations) * 100
            f.write(f"| {player} | {count} | {percentage:.1f}% |\n")
        
        f.write("\n### Players Selected in Every Simulation\n\n")
        always_selected = [player for player, count in player_selections.items() if count == num_simulations]
        for player in always_selected:
            f.write(f"- {player}\n")
        
        f.write("\n### Players Selected in 80%+ of Simulations\n\n")
        frequently_selected = [(player, count) for player, count in player_selections.items() 
                              if (count / num_simulations) >= 0.8 and count < num_simulations]
        f.write("| Player | Times Selected | Percentage |\n")
        f.write("|--------|----------------|------------|\n")
        for player, count in frequently_selected:
            percentage = (count / num_simulations) * 100
            f.write(f"| {player} | {count} | {percentage:.1f}% |\n")
        
        f.write("\n## Position Breakdown\n\n")
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
            if position_counts[position]:
                f.write(f"### {position}\n\n")
                f.write("| Player | Times Selected | Percentage |\n")
                f.write("|--------|----------------|------------|\n")
                for player, count, percentage in position_counts[position][:5]:
                    f.write(f"| {player} | {count} | {percentage:.1f}% |\n")
                f.write("\n")
        
        f.write("## Simulation Files\n\n")
        f.write("Individual simulation results are saved as CSV files:\n\n")
        for i in range(num_simulations):
            f.write(f"- `simulation_{i+1:03d}_{timestamp}.csv`\n")

if __name__ == "__main__":
    run_multiple_simulations(20)  # Run 20 simulations
