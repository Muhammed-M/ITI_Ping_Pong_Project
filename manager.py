import pandas as pd
import json
import random
import os
import math
from datetime import datetime, timedelta

# --- CONFIGURATION ---
CSV_FILE = 'teams.csv'
JSON_FILE = 'tournament_data.json'
START_DATE = "2026-04-01"  # YYYY-MM-DD
MATCH_DURATION = 15
MATCHES_PER_DAY = 2  # Number of matches that can be played per day

class TournamentManager:
    def __init__(self):
        self.teams = []
        self.matches = [] 
        self.load_data()

    def load_data(self):
        if os.path.exists(JSON_FILE):
            print(f"Loading existing data from {JSON_FILE}...")
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
                self.teams = data.get('teams', [])
                self.matches = data.get('matches', [])
                # Ensure all teams have complete stats structure and player names
                for team in self.teams:

                    if 'track' not in team:
                        team['track'] = ''
                    if 'stats' not in team:
                        team['stats'] = {"wins": 0, "goals_for": 0, "goals_against": 0, "matches_played": 0}
                    else:
                        # Add missing stats fields if they don't exist
                        stats = team['stats']
                        if 'goals_for' not in stats:
                            stats['goals_for'] = 0
                        if 'goals_against' not in stats:
                            stats['goals_against'] = 0
                        if 'matches_played' not in stats:
                            stats['matches_played'] = 0
                    
                    # Ensure real_name exists for backward compatibility
                    if 'real_name' not in team:
                        if 'player1' in team and 'player2' in team:
                            team['real_name'] = f"{team['player1']} & {team['player2']}"
                        else:
                            team['real_name'] = team.get('name', 'Unknown')
                
                # Recalculate stats from existing matches to ensure accuracy
                self.recalculate_stats()
                self.save_data()
        else:
            print("Starting NEW tournament...")
            self.import_teams()
            self.create_full_bracket_tree()
            self.schedule_matches()
            self.save_data()

    def import_teams(self):
        try:
            df = pd.read_csv(CSV_FILE)
            df = df.sample(frac=1).reset_index(drop=True)
            for i, row in df.iterrows():
                player1_name = str(row['Player1 Name'])
                player2_name = str(row['Player2 Name'])
                track        = str(row['Track']) if 'Track' in row.index else ''

                self.teams.append({
                    "id": i, 
                    "name": f"Team {i+1}",
                    "real_name": f"{player1_name} & {player2_name}",  # Both player names
                    "player1": player1_name,
                    "player2": player2_name,
                    "track": track,  
                    "stats": {
                        "wins": 0,
                        "goals_for": 0,
                        "goals_against": 0,
                        "matches_played": 0
                    }
                })
        except Exception as e:
            print(f"Error reading CSV: {e}")

    def create_full_bracket_tree(self):
        """
        Generates the COMPLETE tree structure (R1 -> Final) with empty slots.
        """
        n_teams = len(self.teams)
        # Calculate depth (e.g., 32 teams -> 5 rounds)
        depth = math.ceil(math.log2(n_teams))
        bracket_size = 2**depth
        
        # 1. Setup Round 1 (The "Leaves" of the tree)
        current_round_matches = []
        match_id = 1
        
        # Fill slots with teams or Byes
        slots = self.teams[:]
        while len(slots) < bracket_size:
            slots.append(None) # Bye placeholder

        # Create Round 1 Matches
        for i in range(0, len(slots), 2):
            t1 = slots[i]
            t2 = slots[i+1]
            
            m = {
                "id": match_id,
                "round": 1,
                "p1": t1['id'] if t1 else -1,
                "p2": t2['id'] if t2 else -1,
                "score": [0, 0],
                "winner": None,
                "completed": False,
                "time": "TBD",
                "next_match_id": None # Link to next round
            }
            # Auto-handle Byes
            if t1 is None or t2 is None:
                m['completed'] = True
                m['time'] = "Bye"
                
                # FIX: Handle case where both are None (Bye vs Bye)
                if t1 is not None:
                    m['winner'] = t1['id']
                    m['score'] = [1, 0]
                elif t2 is not None:
                    m['winner'] = t2['id']
                    m['score'] = [0, 1]
                else:
                    # Both are None (Bye vs Bye) -> Winner is Bye (-1)
                    m['winner'] = -1
                    m['score'] = [0, 0]

            current_round_matches.append(m)
            self.matches.append(m)
            match_id += 1
            
        # 2. Build Future Rounds (The Branches)
        round_num = 2
        while len(current_round_matches) > 1:
            next_round_matches = []
            
            for i in range(0, len(current_round_matches), 2):
                prev_m1 = current_round_matches[i]
                prev_m2 = current_round_matches[i+1]
                
                new_m = {
                    "id": match_id,
                    "round": round_num,
                    "p1": None, 
                    "p2": None, 
                    "score": [0, 0],
                    "winner": None,
                    "completed": False,
                    "time": "TBD",
                    "next_match_id": None
                }
                
                prev_m1['next_match_id'] = new_m['id']
                prev_m2['next_match_id'] = new_m['id']
                
                # Propagate immediately if previous match was a Bye
                if prev_m1['completed'] and prev_m1['winner'] is not None:
                    new_m['p1'] = prev_m1['winner']
                if prev_m2['completed'] and prev_m2['winner'] is not None:
                    new_m['p2'] = prev_m2['winner']
                
                self.matches.append(new_m)
                next_round_matches.append(new_m)
                match_id += 1
            
            current_round_matches = next_round_matches
            round_num += 1
        
        # After creating all rounds, propagate all bye winners through subsequent rounds
        self.propagate_bye_winners()

    def propagate_bye_winners(self):
        """Propagate winners from bye matches through all subsequent rounds recursively"""
        changed = True
        while changed:
            changed = False
            for match in self.matches:
                # 1. Propagate winner to next match
                if match['completed'] and match['winner'] is not None and match['next_match_id']:
                    next_m = next((m for m in self.matches if m['id'] == match['next_match_id']), None)
                    if next_m:
                        feeders = [m for m in self.matches if m['next_match_id'] == next_m['id']]
                        if len(feeders) == 2:
                            if feeders[0]['id'] == match['id']:
                                if next_m['p1'] != match['winner']:
                                    next_m['p1'] = match['winner']
                                    changed = True
                            else:
                                if next_m['p2'] != match['winner']:
                                    next_m['p2'] = match['winner']
                                    changed = True

                # 2. Auto-complete matches against Byes (-1)
                # If a match has one real player and one Bye (-1), the real player wins automatically
                if not match['completed'] and match['p1'] is not None and match['p2'] is not None:
                    p1_is_bye = (match['p1'] == -1)
                    p2_is_bye = (match['p2'] == -1)
                    
                    if p1_is_bye or p2_is_bye:
                        match['completed'] = True
                        match['time'] = "Bye"
                        changed = True # We changed state, so loop again to propagate this new winner
                        
                        if p1_is_bye and p2_is_bye:
                            match['winner'] = -1
                        elif p1_is_bye:
                            match['winner'] = match['p2']
                            match['score'] = [0, 1]
                        elif p2_is_bye:
                            match['winner'] = match['p1']
                            match['score'] = [1, 0]
                            

    def schedule_matches(self):
        # Only schedule Round 1 for now (and auto-advance Byes)
        current_time = datetime.strptime(START_DATE + " 12:00", "%Y-%m-%d %H:%M")
        matches_today = 0
        
        for m in self.matches:
            if m['round'] == 1 and not m['completed']:
                while current_time.weekday() in [4, 5]: # Skip Fri/Sat
                     current_time += timedelta(days=1)
                     current_time = current_time.replace(hour=12, minute=0)
                
                m['time'] = current_time.strftime("%Y-%m-%d %H:%M")
                matches_today += 1
                if matches_today >= MATCHES_PER_DAY:
                    current_time += timedelta(days=1)
                    current_time = current_time.replace(hour=12, minute=0)
                    matches_today = 0
                else:
                    current_time += timedelta(minutes=MATCH_DURATION)
    
    def schedule_next_round_match(self, match):
        """Schedule a match in a later round when both teams are known"""
        # Find the latest scheduled match time (including completed matches)
        scheduled_matches = [m for m in self.matches if m['time'] != "TBD" and m['time'] != "Bye"]
        
        if scheduled_matches:
            try:
                # Get the latest scheduled time
                latest_time = max([datetime.strptime(m['time'], "%Y-%m-%d %H:%M") for m in scheduled_matches])
                # Schedule the new match after the latest one
                current_time = latest_time + timedelta(days=1)
                current_time = current_time.replace(hour=12, minute=0)
            except:
                # Fallback if date parsing fails
                current_time = datetime.strptime(START_DATE + " 12:00", "%Y-%m-%d %H:%M")
        else:
            # If no scheduled matches, start from START_DATE
            current_time = datetime.strptime(START_DATE + " 12:00", "%Y-%m-%d %H:%M")
        
        # Skip Fri/Sat
        while current_time.weekday() in [4, 5]:
            current_time += timedelta(days=1)
            current_time = current_time.replace(hour=12, minute=0)
        
        match['time'] = current_time.strftime("%Y-%m-%d %H:%M")

    def update_match(self):
        while True:
            # Determine accessible matches (where both players are known)
            playable = []
            for m in self.matches:
                # Check if players are determined (not None) and match not finished
                if not m['completed'] and m['p1'] is not None and m['p2'] is not None and m['p1'] != -1 and m['p2'] != -1:
                    playable.append(m)
            
            if not playable:
                print("No matches ready to play yet.")
                return

            print("\n--- READY TO PLAY ---")
            for m in playable[:10]:
                t1 = next(t['name'] for t in self.teams if t['id'] == m['p1'])
                t2 = next(t['name'] for t in self.teams if t['id'] == m['p2'])
                print(f"ID {m['id']} (R{m['round']}): {t1} vs {t2} @ {m['time']}")

            mid = input("\nEnter Match ID to update (0 to exit): ")
            if mid == '0':
                print("Exiting update mode.")
                return

            match = next((m for m in self.matches if str(m['id']) == mid), None)
            if not match:
                print("Match ID not found. Please try again.")
                continue
            
            if match['completed']:
                print("This match is already completed. Please select another match.")
                continue
                
            if match['p1'] is None or match['p2'] is None or match['p1'] == -1 or match['p2'] == -1:
                print("This match doesn't have both teams assigned yet. Please select another match.")
                continue

            try:
                t1_name = next(t['name'] for t in self.teams if t['id'] == match['p1'])
                t2_name = next(t['name'] for t in self.teams if t['id'] == match['p2'])
                print(f"\nUpdating: {t1_name} vs {t2_name}")
                
                s1 = int(input(f"Score for {t1_name}: "))
                s2 = int(input(f"Score for {t2_name}: "))
                match['score'] = [s1, s2]
                match['completed'] = True
                winner_id = match['p1'] if s1 > s2 else match['p2']
                match['winner'] = winner_id
                
                # UPDATE TEAM STATISTICS
                t1 = next((t for t in self.teams if t['id'] == match['p1']), None)
                t2 = next((t for t in self.teams if t['id'] == match['p2']), None)
                
                if t1:
                    t1['stats']['goals_for'] += s1
                    t1['stats']['goals_against'] += s2
                    t1['stats']['matches_played'] += 1
                    if s1 > s2:
                        t1['stats']['wins'] += 1
                
                if t2:
                    t2['stats']['goals_for'] += s2
                    t2['stats']['goals_against'] += s1
                    t2['stats']['matches_played'] += 1
                    if s2 > s1:
                        t2['stats']['wins'] += 1
                
                # PROPAGATE WINNER TO NEXT ROUND
                if match['next_match_id']:
                    next_m = next(m for m in self.matches if m['id'] == match['next_match_id'])
                    # Place winner in the correct slot of the next match
                    # We need to know if this match was the 'top' or 'bottom' feeder
                    # Simple heuristic: If next_m has no p1, take p1. Else take p2.
                    if next_m['p1'] is None:
                        next_m['p1'] = winner_id
                    else:
                        next_m['p2'] = winner_id
                    
                    # Schedule the next match if both teams are now known
                    if next_m['p1'] is not None and next_m['p2'] is not None and next_m['p1'] != -1 and next_m['p2'] != -1 and next_m['time'] == "TBD":
                        self.schedule_next_round_match(next_m)
                
                self.save_data()
                winner_name = next(t['name'] for t in self.teams if t['id'] == winner_id)
                print(f"✓ Updated! Winner: {winner_name} ({s1}-{s2})")
                
            except ValueError:
                print("Invalid input. Please enter numbers only.")
            except Exception as e:
                print(f"Error: {e}")

    def recalculate_stats(self):
        """Recalculate team statistics from all completed matches"""
        # Reset all stats
        for team in self.teams:
            team['stats'] = {
                "wins": 0,
                "goals_for": 0,
                "goals_against": 0,
                "matches_played": 0
            }
        
        # Recalculate from completed matches
        for match in self.matches:
            if match['completed'] and match['p1'] != -1 and match['p2'] != -1:
                s1, s2 = match['score']
                t1 = next((t for t in self.teams if t['id'] == match['p1']), None)
                t2 = next((t for t in self.teams if t['id'] == match['p2']), None)
                
                if t1:
                    t1['stats']['goals_for'] += s1
                    t1['stats']['goals_against'] += s2
                    t1['stats']['matches_played'] += 1
                    if s1 > s2:
                        t1['stats']['wins'] += 1
                
                if t2:
                    t2['stats']['goals_for'] += s2
                    t2['stats']['goals_against'] += s1
                    t2['stats']['matches_played'] += 1
                    if s2 > s1:
                        t2['stats']['wins'] += 1

    def save_data(self):
        data = {"teams": self.teams, "matches": self.matches}
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved.")

if __name__ == "__main__":
    tm = TournamentManager()
    tm.update_match()