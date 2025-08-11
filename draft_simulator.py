import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
import csv
from config import *

class FantasyDraftSimulator:
    def __init__(self, available_players_file: str, draft_file: str):
        """
        Initialize the draft simulator with player data and draft order.
        
        Args:
            available_players_file: Path to CSV with available players
            draft_file: Path to CSV with draft order and keepers
        """
        self.available_players = pd.read_csv(available_players_file)
        self.draft_order = pd.read_csv(draft_file, skiprows=1)  # Skip the extra header row
        
        # Filter out already taken players (marked with 'x')
        self.available_players = self.available_players[self.available_players['Taken'] != 'x'].copy()
        
        # Starting roster requirements
        self.starting_roster = STARTING_ROSTER
        
        # Track each team's roster
        self.team_rosters = {}
        self.keepers = {}
        
        # Initialize team rosters and identify keepers
        self._initialize_rosters()
        self._identify_keepers()
        
    def _initialize_rosters(self):
        """Initialize empty rosters for all teams."""
        teams = self.draft_order['Team'].unique()
        for team in teams:
            self.team_rosters[team] = {
                'QB': [],
                'RB': [],
                'WR': [],
                'TE': [],
                'K': [],
                'DST': [],
                'FLEX': []  # Will be filled from RB/WR/TE
            }
    
    def _identify_keepers(self):
        """Identify and assign keepers to teams."""
        for _, row in self.draft_order.iterrows():
            if pd.notna(row['Player']) and row['Player'] != '':
                team = row['Team']
                player = row['Player']
                position = row['Position']
                
                # Find the player in available players
                player_data = self.available_players[
                    self.available_players['Name Formula'] == player
                ]
                
                if not player_data.empty:
                    # Remove keeper from available players
                    self.available_players = self.available_players[
                        self.available_players['Name Formula'] != player
                    ]
                    
                    # Add to team roster
                    if position in ['RB', 'WR', 'TE']:
                        # Check if we need to fill FLEX position
                        if len(self.team_rosters[team]['FLEX']) < self.starting_roster['FLEX']:
                            self.team_rosters[team]['FLEX'].append(player)
                        else:
                            self.team_rosters[team][position].append(player)
                    else:
                        self.team_rosters[team][position].append(player)
                    
                    # Mark this pick as a keeper
                    self.keepers[row['ID']] = {
                        'team': team,
                        'player': player,
                        'position': position
                    }
    
    def _get_team_needs(self, team: str) -> Dict[str, int]:
        """Calculate what positions a team still needs to fill."""
        roster = self.team_rosters[team]
        needs = {}
        
        for pos, required in self.starting_roster.items():
            if pos == 'FLEX':
                # FLEX can be filled by RB, WR, or TE
                flex_filled = len(roster['FLEX'])
                rb_count = len(roster['RB'])
                wr_count = len(roster['WR'])
                te_count = len(roster['TE'])
                
                # Calculate how many more FLEX players needed
                total_flex_eligible = rb_count + wr_count + te_count
                needs['FLEX'] = max(0, required - flex_filled)
                
                # Also track individual position needs for FLEX
                needs['RB_FLEX'] = max(0, 2 - rb_count)  # Need 2 RBs total
                needs['WR_FLEX'] = max(0, 2 - wr_count)  # Need 2 WRs total
                needs['TE_FLEX'] = max(0, 1 - te_count)  # Need 1 TE total
            else:
                current = len(roster[pos])
                needs[pos] = max(0, required - current)
        
        return needs
    
    def _get_priority_positions(self, team: str) -> List[str]:
        """Get positions that need to be filled, prioritized by importance."""
        needs = self._get_team_needs(team)
        priority = []
        
        # First priority: Fill starting positions
        for pos in POSITION_PRIORITIES:
            if needs.get(pos, 0) > 0:
                priority.append(pos)
        
        # Second priority: Fill FLEX positions
        if needs.get('FLEX', 0) > 0:
            # Determine which position to prioritize for FLEX
            if needs.get('RB_FLEX', 0) > 0:
                priority.append('RB')
            elif needs.get('WR_FLEX', 0) > 0:
                priority.append('WR')
            elif needs.get('TE_FLEX', 0) > 0:
                priority.append('TE')
            else:
                # All starting positions filled, can pick best available for FLEX
                priority.extend(['RB', 'WR', 'TE'])
        
        return priority
    
    def _get_available_players_by_position(self, position: str, count: int = 10) -> List[str]:
        """Get top available players for a specific position."""
        if position == 'FLEX':
            # For FLEX, get best available RB, WR, or TE
            flex_players = self.available_players[
                self.available_players['Position'].isin(['RB', 'WR', 'TE'])
            ].copy()
            return flex_players.nsmallest(count, 'Rank')['Name Formula'].tolist()
        else:
            pos_players = self.available_players[
                self.available_players['Position'] == position
            ].copy()
            return pos_players.nsmallest(count, 'Rank')['Name Formula'].tolist()
    
    def _calculate_randomness_factor(self, pick_number: int) -> int:
        """Calculate how much randomness to add based on pick number."""
        if pick_number <= PICK_THRESHOLDS['early']:
            return RANDOMNESS_FACTORS['early_picks']
        elif pick_number <= PICK_THRESHOLDS['mid']:
            return RANDOMNESS_FACTORS['mid_picks']
        elif pick_number <= PICK_THRESHOLDS['late']:
            return RANDOMNESS_FACTORS['late_picks']
        else:
            return RANDOMNESS_FACTORS['very_late_picks']
    
    def _select_player_with_randomness(self, available_players: List[str], pick_number: int) -> str:
        """Select a player with increasing randomness as draft progresses."""
        if not available_players:
            return None
        
        randomness_factor = self._calculate_randomness_factor(pick_number)
        selection_pool = available_players[:min(randomness_factor, len(available_players))]
        
        # Weight selection towards higher ranked players
        weights = [1.0 / (i + 1) for i in range(len(selection_pool))]
        weights = [w / sum(weights) for w in weights]  # Normalize
        
        selected_player = random.choices(selection_pool, weights=weights, k=1)[0]
        return selected_player
    
    def _make_pick(self, team: str, pick_number: int) -> Optional[Tuple[str, str]]:
        """Make a pick for a team based on their needs."""
        priority_positions = self._get_priority_positions(team)
        
        if not priority_positions:
            # Team has all starting positions filled, pick best available
            best_available = self.available_players.nsmallest(10, 'Rank')['Name Formula'].tolist()
            selected_player = self._select_player_with_randomness(best_available, pick_number)
        else:
            # Try to fill highest priority position
            for position in priority_positions:
                available_players = self._get_available_players_by_position(position, 20)
                if available_players:
                    selected_player = self._select_player_with_randomness(available_players, pick_number)
                    break
            else:
                # Fallback to best available
                best_available = self.available_players.nsmallest(10, 'Rank')['Name Formula'].tolist()
                selected_player = self._select_player_with_randomness(best_available, pick_number)
        
        if selected_player:
            # Get player data before removing from available players
            player_data = self.available_players[
                self.available_players['Name Formula'] == selected_player
            ]
            
            if not player_data.empty:
                position = player_data.iloc[0]['Position']
                
                # Determine where to place the player
                if position in ['RB', 'WR', 'TE']:
                    # Check if we need to fill starting positions first
                    needs = self._get_team_needs(team)
                    
                    if position == 'RB' and needs.get('RB_FLEX', 0) > 0:
                        self.team_rosters[team]['RB'].append(selected_player)
                    elif position == 'WR' and needs.get('WR_FLEX', 0) > 0:
                        self.team_rosters[team]['WR'].append(selected_player)
                    elif position == 'TE' and needs.get('TE_FLEX', 0) > 0:
                        self.team_rosters[team]['TE'].append(selected_player)
                    elif needs.get('FLEX', 0) > 0:
                        self.team_rosters[team]['FLEX'].append(selected_player)
                    else:
                        self.team_rosters[team][position].append(selected_player)
                else:
                    self.team_rosters[team][position].append(selected_player)
                
                # Remove player from available pool
                self.available_players = self.available_players[
                    self.available_players['Name Formula'] != selected_player
                ]
                
                return (selected_player, position)
        
        return None
    
    def simulate_draft(self, seed: int = None) -> List[Dict]:
        """Simulate the entire draft and return results."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        draft_results = []
        
        for _, pick in self.draft_order.iterrows():
            pick_id = pick['ID']
            team = pick['Team']
            overall_pick = pick['Overall']
            round_num = pick['Round']
            pick_in_round = pick['Pick']
            
            # Check if this is a keeper pick
            if pick_id in self.keepers:
                keeper_info = self.keepers[pick_id]
                draft_results.append({
                    'ID': pick_id,
                    'Overall': overall_pick,
                    'Round': round_num,
                    'Pick': pick_in_round,
                    'Team': team,
                    'Player': keeper_info['player'],
                    'Position': keeper_info['position'],
                    'Notes': 'Keeper',
                    'Type': 'Keeper'
                })
            else:
                # Make a pick
                pick_result = self._make_pick(team, overall_pick)
                
                if pick_result:
                    selected_player, position = pick_result
                    
                    draft_results.append({
                        'ID': pick_id,
                        'Overall': overall_pick,
                        'Round': round_num,
                        'Pick': pick_in_round,
                        'Team': team,
                        'Player': selected_player,
                        'Position': position,
                        'Notes': 'Simulated Pick',
                        'Type': 'Draft'
                    })
                else:
                    draft_results.append({
                        'ID': pick_id,
                        'Overall': overall_pick,
                        'Round': round_num,
                        'Pick': pick_in_round,
                        'Team': team,
                        'Player': 'No Player Available',
                        'Position': 'N/A',
                        'Notes': 'No players available',
                        'Type': 'Error'
                    })
        
        return draft_results
    
    def print_team_rosters(self):
        """Print the final rosters for all teams."""
        print("\n" + "="*80)
        print("FINAL TEAM ROSTERS")
        print("="*80)
        
        for team, roster in self.team_rosters.items():
            print(f"\n{team.upper()}:")
            print("-" * 40)
            
            for position, players in roster.items():
                if players:
                    print(f"{position:4}: {', '.join(players)}")
                else:
                    print(f"{position:4}: None")
    
    def export_results(self, results: List[Dict], filename: str = OUTPUT_FILE):
        """Export draft results to CSV."""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['ID', 'Overall', 'Round', 'Pick', 'Team', 'Player', 'Position', 'Notes', 'Type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\nDraft results exported to {filename}")

def main():
    """Run the draft simulator."""
    # Initialize simulator
    simulator = FantasyDraftSimulator(
        AVAILABLE_PLAYERS_FILE,
        DRAFT_FILE
    )
    
    # Simulate draft
    print("Simulating Fantasy Football Draft...")
    results = simulator.simulate_draft(seed=SEED)  # Set seed for reproducible results
    
    # Print results
    print("\n" + "="*80)
    print("SIMULATED DRAFT RESULTS")
    print("="*80)
    
    for result in results:
        if result['Type'] == 'Keeper':
            print(f"Pick {result['Overall']:2d} ({result['Round']}.{result['Pick']:02d}): {result['Team']:8} - {result['Player']:25} ({result['Position']}) - KEEPER")
        else:
            print(f"Pick {result['Overall']:2d} ({result['Round']}.{result['Pick']:02d}): {result['Team']:8} - {result['Player']:25} ({result['Position']})")
    
    # Print team rosters
    simulator.print_team_rosters()
    
    # Export results
    simulator.export_results(results)

if __name__ == "__main__":
    main()
