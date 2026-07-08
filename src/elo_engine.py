import pandas as pd
import numpy as np
import joblib
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Load xG model
model_path = os.path.join(base_dir, "models", "xg_model.joblib")
xg_model = joblib.load(model_path)
print("✅ xG Model loaded successfully!")

# 2. FIFA seed rankings
FIFA_RANKINGS = {
    "Argentina": 1,  "France": 2,    "Spain": 3,     "England": 4,   "Brazil": 5,
    "Morocco": 6,    "Netherlands": 7,"Portugal": 8,  "Mexico": 9,    "Belgium": 10,
    "Colombia": 11,  "Germany": 12,  "Croatia": 13,  "Italy": 14,    "USA": 15,
    "Switzerland": 16,"Japan": 17,   "Senegal": 18,  "Uruguay": 19,  "Denmark": 20,
    "Iran": 21,      "Austria": 22,  "Norway": 23,   "Ecuador": 24,  "Nigeria": 25,
    "Egypt": 26,     "Turkey": 27,   "Australia": 28,"Algeria": 29,  "Canada": 30,
    "Korea Republic":32,"Ukraine":33, "Russia": 34,   "Poland": 35,   "Sweden": 36,
    "Paraguay": 37,  "Wales": 38,    "Serbia": 40,   "Scotland": 42, "Cameroon": 43,
    "Panama": 44,    "Slovakia": 45, "Greece": 46,   "Czechia": 48,  "Chile": 49,
    "Peru": 50,      "Costa Rica": 51,"Romania": 52, "Mali": 53,     "Ghana": 65,
    "Republic of Ireland":55,"Saudi Arabia":58,"Qatar":59,"Uzbekistan":60,
    "Bosnia and Herzegovina":61,"Burkina Faso":62,"Iraq":63,"Cape Verde":64,
    "Jordan": 73,    "Finland": 75,  "South Africa": 47, "Ivory Coast": 31,
    "DR Congo": 56,  "Tunisia": 57,  "New Zealand": 100, "Curacao": 90, "Haiti": 85
}

def get_fifa_rank(team_name):
    return FIFA_RANKINGS.get(team_name, 100)

# 3. Elo dictionary
teams_elo = {}

def get_team_elo(team_name):
    if team_name not in teams_elo:
        rank = get_fifa_rank(team_name)
        seed = max(1200, 1900 - (rank * 6))
        teams_elo[team_name] = {
            'attacking_elo': float(seed),
            'defensive_elo': float(seed),
        }
    return teams_elo[team_name]

# 4. Elo update
def update_elo(home_team, away_team, home_xg, away_xg):
    home = get_team_elo(home_team)
    away = get_team_elo(away_team)

    k_factor = 20.0

    # Upset multiplier
    home_rank = get_fifa_rank(home_team)
    away_rank = get_fifa_rank(away_team)
    rank_diff = abs(home_rank - away_rank)
    upset_multiplier = 1.0
    if home_xg > away_xg and home_rank > away_rank:
        upset_multiplier = 1.0 + (rank_diff / 20.0)
    elif away_xg > home_xg and away_rank > home_rank:
        upset_multiplier = 1.0 + (rank_diff / 20.0)

    effective_k = k_factor * upset_multiplier

    # THE MATH FIX: Add an exponent (^3) to amplify the difference between good and bad teams!
    # Now a 1900 attack vs 1300 defense will result in a MUCH higher expected xG.
    exp_home_xg = ((home['attacking_elo'] / away['defensive_elo']) ** 3) * 1.35
    exp_away_xg = ((away['attacking_elo'] / home['defensive_elo']) ** 3) * 1.35

    home_delta = (home_xg - exp_home_xg) * effective_k
    away_delta = (away_xg - exp_away_xg) * effective_k

    home['attacking_elo'] += home_delta
    away['defensive_elo'] -= home_delta

    away['attacking_elo'] += away_delta
    home['defensive_elo'] -= away_delta

    # Clamp
    for team in [home, away]:
        team['attacking_elo'] = max(800, min(2200, team['attacking_elo']))
        team['defensive_elo'] = max(800, min(2200, team['defensive_elo']))

# 5. Load shot data
data_path = os.path.join(base_dir, "data", "all_qualifier_shots.csv")
df = pd.read_csv(data_path)

# 6. Feature engineering
df['x_standard'] = df['x'].where(df['x'] >= 50, 100 - df['x'])
df['y_standard'] = df.apply(lambda r: 100 - r['y'] if r['x'] < 50 else r['y'], axis=1)

goal_x, goal_y = 100, 50
df['distance'] = np.sqrt((goal_x - df['x_standard'])**2 + (goal_y - df['y_standard'])**2)

left_post_y, right_post_y = 53.66, 46.34
angle_left  = np.arctan2(left_post_y - df['y_standard'], goal_x - df['x_standard'])
angle_right = np.arctan2(right_post_y - df['y_standard'], goal_x - df['x_standard'])
df['angle'] = np.abs(np.degrees(angle_left - angle_right))


# 7. Calculate xG per shot
df['xg'] = xg_model.predict_proba(df[['distance', 'angle']])[:, 1]

# ==========================================
# THE TIMELINE FIX: Sort Data Chronologically
# ==========================================
# We look for common date/time column names to sort the matches correctly
date_column = None
for col in ['match_date', 'date', 'timestamp']:
    if col in df.columns:
        date_column = col
        break

if date_column:
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(by=date_column).reset_index(drop=True)
    print(f"📅 Timeline Sorted: Processing matches chronologically using '{date_column}'")
else:
    # Fallback: if match_ids are sequential numeric strings/integers, sort by them
    try:
        df = df.sort_values(by='match_id').reset_index(drop=True)
        print("🔢 Timeline Sorted: Processing matches sequentially by 'match_id'")
    except Exception:
        print("⚠️ Warning: No explicit date or sorting column found. Using default sequence.")

# 8. Group by match and team 
# CRITICAL FIX: We add sort=False so pandas preserves our clean chronological order!
match_xg = df.groupby(['match_id', 'team'], sort=False)['xg'].sum().reset_index()

print(f"\nUpdating Elo across {match_xg['match_id'].nunique()} matches...")

skipped = 0
# Because match_xg preserves row order, .unique() returns match_ids in perfect chronological order
for match_id in match_xg['match_id'].unique():
    match_data = match_xg[match_xg['match_id'] == match_id]

    # ==========================================
    # THE 0-SHOT FIX: Handle Dominant Clean Sheets
    # ==========================================
    if len(match_data) == 2:
        # Standard case: Both teams registered at least one shot
        team1_name = match_data.iloc[0]['team']
        team1_xg = match_data.iloc[0]['xg']
        
        team2_name = match_data.iloc[1]['team']
        team2_xg = match_data.iloc[1]['xg']
        
    elif len(match_data) == 1:
        # Edge case fix: One team choked or was locked down to exactly 0 shots!
        team1_name = match_data.iloc[0]['team']
        team1_xg = match_data.iloc[0]['xg']
        
        # Look back at the original dataset row for this match to find who they played against
        raw_match_row = df[df['match_id'] == match_id].iloc[0]
        
        if 'opponent' in df.columns:
            team2_name = raw_match_row['opponent']
        elif 'home_team' in df.columns and 'away_team' in df.columns:
            team2_name = raw_match_row['away_team'] if raw_match_row['home_team'] == team1_name else raw_match_row['home_team']
        else:
            # If your CSV doesn't track opponents on the same row, we must skip
            skipped += 1
            continue
            
        team2_xg = 0.0  # They took 0 shots, so their generated xG is exactly zero
        
    else:
        skipped += 1
        continue

    # Skip matches where nothing happened at all
    if team1_xg == 0 and team2_xg == 0:
        skipped += 1
        continue

    # Feed the verified match details into your Elo calculator
    update_elo(team1_name, team2_name, team1_xg, team2_xg)

print(f"Skipped {skipped} matches (missing data or zero overall xG)")

# 9. Print final rankings
print("\n" + "="*55)
print("🏆  FINAL WORLD CUP ELO RANKINGS")
print("="*55)
print(f"{'Rank':<5} {'Team':<25} {'Attack':>10} {'Defense':>10}")
print("-"*55)

sorted_teams = sorted(teams_elo.items(), key=lambda x: x[1]['attacking_elo'], reverse=True)
for i, (team, elos) in enumerate(sorted_teams, 1):
    print(f"{i:<5} {team:<25} {elos['attacking_elo']:>10.0f} {elos['defensive_elo']:>10.0f}")



# 11. Save the Elo dictionary to a JSON file!
elo_json_path = os.path.join(base_dir, "data", "team_elos.json")
with open(elo_json_path, 'w') as f:
    # Convert the dictionary to JSON format and save it
    json.dump(teams_elo, f, indent=4)

print(f"\n💾 Elo ratings saved to: {elo_json_path}")
print("You can now run simulator.py!")