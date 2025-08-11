"""
Configuration settings for the Fantasy Football Draft Simulator.
"""

# Randomness settings for different draft phases
RANDOMNESS_FACTORS = {
    'early_picks': 5,      # Picks 1-10: top 5 players
    'mid_picks': 15,       # Picks 11-50: top 15 players  
    'late_picks': 30,      # Picks 51-100: top 30 players
    'very_late_picks': 50  # Picks 100+: top 50 players
}

# Pick thresholds for randomness phases
PICK_THRESHOLDS = {
    'early': 10,
    'mid': 50, 
    'late': 100
}

# Starting roster requirements
STARTING_ROSTER = {
    'QB': 1,
    'RB': 2,
    'WR': 2, 
    'TE': 1,
    'FLEX': 1,  # Can be RB, WR, or TE
    'K': 1,
    'DST': 1
}

# Position priorities for filling roster
POSITION_PRIORITIES = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']

# File paths
AVAILABLE_PLAYERS_FILE = 'inputs/Draft 2025 - Available Players.csv'
DRAFT_FILE = 'inputs/Draft 2025 - Draft.csv'

# Output settings
OUTPUT_FILE = 'simulated_draft_results.csv'
SEED = 42  # Set to None for random seed each run
