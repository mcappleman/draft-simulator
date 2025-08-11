# Fantasy Football Draft Simulator

A Python-based fantasy football draft simulator that handles keepers, position requirements, and increasing randomness throughout the draft.

## Features

- **Keeper Support**: Automatically identifies and assigns keepers from the draft file
- **Position Requirements**: Ensures teams fill their starting roster (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 DST)
- **Progressive Randomness**: Early picks are more predictable, later picks have more randomness
- **Smart Drafting**: Teams prioritize filling starting positions before bench spots
- **Export Results**: Saves draft results to CSV for analysis

## Requirements

- Python 3.7+
- pandas
- numpy

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your CSV files in the `inputs/` directory:
   - `Draft 2025 - Available Players.csv`: Contains all available players with rankings
   - `Draft 2025 - Draft.csv`: Contains draft order and keeper information

2. Run the simulator:
```bash
python draft_simulator.py
```

## Input File Formats

### Available Players CSV
Should contain columns:
- `Name Formula`: Player name
- `Taken`: 'x' if player is already taken, empty if available
- `Rank`: Overall ranking
- `Position`: Player position (QB, RB, WR, TE, K, DST)
- Other columns are optional

### Draft CSV
Should contain columns:
- `ID`: Unique pick identifier
- `Overall`: Overall pick number
- `Round`: Draft round
- `Pick`: Pick within round
- `Team`: Team name
- `Player`: Player name (if keeper)
- `Position`: Player position (if keeper)
- `Notes`: Keeper notes

## Output

The simulator will:
1. Print the complete draft results to console
2. Show final team rosters
3. Export results to `simulated_draft_results.csv`

## Customization

You can modify the simulator by:
- Changing the randomness factors in `_calculate_randomness_factor()`
- Adjusting position priorities in `_get_priority_positions()`
- Modifying roster requirements in the `starting_roster` dictionary

## Example Output

```
Pick  1 (1.01): Basil     - Ja'Marr Chase              (WR)
Pick  2 (1.02): Chaz      - Amon-Ra St. Brown          (WR)
Pick  3 (1.03): Hunter    - Drake London               (WR)
Pick  4 (1.04): Ross      - CeeDee Lamb                (WR) - KEEPER
...
```

## Randomness Algorithm

- **Picks 1-10**: Top 5 players available
- **Picks 11-50**: Top 15 players available  
- **Picks 51-100**: Top 30 players available
- **Picks 100+**: Top 50 players available

Selection is weighted towards higher-ranked players within each pool.
