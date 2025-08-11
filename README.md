# Fantasy Football Draft Simulator

A Python-based fantasy football draft simulator that handles keepers, position requirements, and increasing randomness throughout the draft.

## Features

- **Keeper Support**: Automatically identifies and assigns keepers from the draft file
- **Pre-assigned Player Support**: Respects players already assigned in the draft CSV file
- **Position Requirements**: Ensures teams fill their starting roster (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 DST)
- **Progressive Randomness**: Early picks are more predictable, later picks have more randomness
- **Flexible Drafting**: Teams can draft bench players early while ensuring complete starting lineups by draft end
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

### Multiple Simulations
```bash
# Run 20 simulations and analyze results
python run_multiple_simulations.py
```

This will:
- Run multiple draft simulations
- Save each simulation as a separate CSV file in the `outputs/` folder
- Generate a comprehensive markdown analysis report
- Show player selection frequency and position breakdowns

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

### Single Simulation
The simulator will:
1. Print the complete draft results to console
2. Show final team rosters
3. Export results to `simulated_draft_results.csv`

### Multiple Simulations
The multiple simulation script will:
1. Run the specified number of simulations
2. Save each simulation as a separate CSV file in the `outputs/` folder
3. Generate a comprehensive markdown analysis report with:
   - Player selection frequency tables
   - Position breakdowns
   - Players selected in every simulation
   - Players selected in 80%+ of simulations
   - **Average draft position analysis** (showing where players are typically drafted)
   - **Team roster summaries** (showing most common players for each team)
4. Print summary statistics to console

## Customization

You can modify the simulator by:
- Changing the randomness factors in `_calculate_randomness_factor()`
- Adjusting the position priority logic in `_get_priority_positions()`
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
