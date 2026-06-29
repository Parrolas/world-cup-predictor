import pandas as pd
import numpy as np
import joblib
import os

# 1. Load your trained xG model!
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, "models", "xg_model.joblib")
xg_model = joblib.load(model_path)
print("✅ xG Model loaded successfully!")

# 2. Set up our Elo Dictionary
teams_elo = {}
def get_team_elo(team_name):
    if team_name not in teams_elo:
        fifa_rank = get_fifa_rank(team_name)
        
        # SEED THE ELO BASED ON FIFA RANK!
        # Formula: Top team (Rank 1) starts at 1900. Worst team starts around 1200.
        starting_elo = 1900 - (fifa_rank * 6)
        starting_elo = max(1200, starting_elo) # Floor at 1200
        
        # Good teams have high Attacking and Defensive Elo
        teams_elo[team_name] = {
            'attacking_elo': float(starting_elo), 
            'defensive_elo': float(starting_elo)
        }
    return teams_elo[team_name]

# Official FIFA Men's World Rankings (Late 2024)
FIFA_RANKINGS = {
    "Argentina": 1, "France": 2, "Spain": 3, "England": 4, "Brazil": 5,
    "Portugal": 8, "Netherlands": 7, "Belgium": 10, "Italy": 14, "Croatia": 13,
    "Germany": 12, "Morocco": 6, "Colombia": 11, "Uruguay": 19, "USA": 15,
    "Mexico": 9, "Japan": 17, "Switzerland": 16, "Iran": 21, "Denmark": 20,
    "Korea Republic": 32, "Senegal": 18, "Austria": 22, "Ukraine": 33, "Australia": 28,
    "Sweden": 36, "Turkey": 27, "Wales": 38, "Serbia": 40, "Poland": 35,
    "Peru": 50, "Tunisia": 57, "Algeria": 29, "Egypt": 26, "Norway": 23,
    "Romania": 52, "Czechia": 48, "Scotland": 42, "Chile": 49, "Ecuador": 24,
    "Nigeria": 25, "Costa Rica": 51, "Cameroon": 43, "Russia": 34, "Canada": 30,
    "Paraguay": 37, "Saudi Arabia": 58, "Republic of Ireland": 55, "Ghana": 65,
    "Qatar": 59, "Greece": 46, "Panama": 44, "Mali": 53, "Bosnia and Herzegovina": 61,
    "Honduras": 66, "Slovakia": 45, "Burkina Faso": 62, "Cape Verde Islands": 64,
    "Finland": 75, "Uzbekistan": 60, "Jordan": 73, "Iraq": 63, "United Arab Emirates": 68
}

def get_fifa_rank(team_name):
    # Return rank, default to 100 if team isn't in our list
    return FIFA_RANKINGS.get(team_name, 100)

# 3. The Elo Update Function (FIXED & STABLE)
def update_elo(home_team, away_team, home_xg, away_xg):
    home = get_team_elo(home_team)
    away = get_team_elo(away_team)
    
    # Base K-factor
    k_factor = 20.0
    
    # Get FIFA Ranks (Lower number is better)
    home_rank = get_fifa_rank(home_team)
    away_rank = get_fifa_rank(away_team)
    
    # STRENGTH OF SCHEDULE MULTIPLIER
    # If a highly ranked team plays a low ranked team, the multiplier is small.
    # If an upset happens, the multiplier is huge!
    rank_diff = abs(home_rank - away_rank)
    upset_multiplier = 1.0
    if home_xg > away_xg and home_rank > away_rank: # Higher rank number (worse team) won
        upset_multiplier = 1.0 + (rank_diff / 20.0)
    elif away_xg > home_xg and away_rank > home_rank: # Higher rank number (worse team) won
        upset_multiplier = 1.0 + (rank_diff / 20.0)
        
    effective_k = k_factor * upset_multiplier

    # Use RATIO for expected xG
    exp_home_xg = (home['attacking_elo'] / away['defensive_elo']) * 1.35
    exp_away_xg = (away['attacking_elo'] / home['defensive_elo']) * 1.35
    
    # The difference between ACTUAL xG and EXPECTED xG
    home_delta = (home_xg - exp_home_xg) * effective_k
    away_delta = (away_xg - exp_away_xg) * effective_k
    
    home['attacking_elo'] += home_delta
    away['defensive_elo'] -= home_delta
    
    away['attacking_elo'] += away_delta
    home['defensive_elo'] -= away_delta
    
    # CLAMP THE VALUES
    home['attacking_elo'] = max(800, min(2200, home['attacking_elo']))
    away['attacking_elo'] = max(800, min(2200, away['attacking_elo']))
    home['defensive_elo'] = max(800, min(2200, home['defensive_elo']))
    away['defensive_elo'] = max(800, min(2200, away['defensive_elo']))

# 4. Load your massive shot dataset
data_path = os.path.join(base_dir, "data", "all_qualifier_shots.csv")
df = pd.read_csv(data_path)

# 5. Feature Engineering (Smart Coordinate Flip!)
df['x_standard'] = df.apply(lambda row: 100 - row['x'] if row['x'] < 50 else row['x'], axis=1)
df['y_standard'] = df.apply(lambda row: 100 - row['y'] if row['x'] < 50 else row['y'], axis=1)
goal_x, goal_y = 100, 50
df['distance'] = np.sqrt((goal_x - df['x_standard'])**2 + (goal_y - df['y_standard'])**2)
left_post_y, right_post_y = 53.66, 46.34
angle_left = np.arctan2(left_post_y - df['y_standard'], goal_x - df['x_standard'])
angle_right = np.arctan2(right_post_y - df['y_standard'], goal_x - df['x_standard'])
df['angle'] = np.abs(np.degrees(angle_left - angle_right))

# 6. Calculate xG for every single shot!
df['xg'] = xg_model.predict_proba(df[['distance', 'angle']])[:, 1]

# 7. Group by match and team to get total xG
# We use reset_index() instead of unstack() to keep it as a clean list
match_xg = df.groupby(['match_id', 'team'])['xg'].sum().reset_index()

print(f"\nCalculating Elo for {match_xg['match_id'].nunique()} matches...")

# 8. Loop through matches and update the Elo!
for match_id in match_xg['match_id'].unique():
    # Get ONLY the teams that played in this specific match
    match_data = match_xg[match_xg['match_id'] == match_id]
    
    # We need exactly 2 teams to play a match
    if len(match_data) < 2:
        continue
        
    team1_name = match_data.iloc[0]['team']
    team1_xg = match_data.iloc[0]['xg']
    
    team2_name = match_data.iloc[1]['team']
    team2_xg = match_data.iloc[1]['xg']
    
    # Skip matches with 0 data
    if team1_xg == 0 and team2_xg == 0:
        continue
        
    update_elo(team1_name, team2_name, team1_xg, team2_xg)

# 9. Print the Final Rankings!
print("\n" + "="*50)
print("🏆 FINAL WORLD CUP ELO RANKINGS 🏆")
print("="*50)
print(f"{'Team':<25} | {'Attack Elo':<12} | {'Defense Elo':<12}")
print("-"*55)

# Sort teams by Attacking Elo (highest to lowest)
sorted_teams = sorted(teams_elo.items(), key=lambda x: x[1]['attacking_elo'], reverse=True)

for team, elos in sorted_teams:
    print(f"{team:<25} | {elos['attacking_elo']:<12.0f} | {elos['defensive_elo']:<12.0f}")