import numpy as np
import json
import os
from collections import Counter

# 1. Load the Elo Ratings from the JSON file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
elo_path = os.path.join(base_dir, "data", "team_elos.json")

with open(elo_path, 'r') as f:
    teams_elo = json.load(f)

print("🏆" * 20)
print("  WORLD CUP MATCH SIMULATOR")
print("🏆" * 20)
print(f"\nDatabase loaded: {len(teams_elo)} teams available.\n")

# 2. Get User Input
team_a_name = input("Enter Team A (e.g., France): ").strip()
team_b_name = input("Enter Team B (e.g., Haiti): ").strip()

# 3. Validate Input
if team_a_name not in teams_elo:
    print(f"\n❌ Error: '{team_a_name}' is not in the database. Check your spelling!")
    exit()
if team_b_name not in teams_elo:
    print(f"\n❌ Error: '{team_b_name}' is not in the database. Check your spelling!")
    exit()
if team_a_name == team_b_name:
    print("\n❌ Error: A team cannot play against itself!")
    exit()

# 4. Fetch the Elo Ratings
team_a_elo = teams_elo[team_a_name]
team_b_elo = teams_elo[team_b_name]

# 5. Calculate Expected Goals (xG)
base_xg_a = ((team_a_elo['attacking_elo'] / team_b_elo['defensive_elo']) ** 3) * 1.35
base_xg_b = ((team_b_elo['attacking_elo'] / team_a_elo['defensive_elo']) ** 3) * 1.35

# 6. The Unpredictability Factor 
rating_diff = abs(team_a_elo['attacking_elo'] - team_b_elo['attacking_elo'])
upset_factor = 1.0 + (rating_diff / 1000)

print(f"\n--- Match Simulation: {team_a_name} vs {team_b_name} ---")
print(f"Expected Goals: {team_a_name} {base_xg_a:.2f} - {base_xg_b:.2f} {team_b_name}\n")

# 7. The Poisson Simulation (Monte Carlo)
NUM_SIMULATIONS = 10000
results = []

for _ in range(NUM_SIMULATIONS):
    # Roll match-specific variation dynamically inside each simulation iteration
    sim_xg_a = max(0.1, base_xg_a * np.random.normal(1.0, upset_factor * 0.1))
    sim_xg_b = max(0.1, base_xg_b * np.random.normal(1.0, upset_factor * 0.1))
    
    goals_a = np.random.poisson(sim_xg_a)
    goals_b = np.random.poisson(sim_xg_b)
    results.append((goals_a, goals_b))


# 8. Tally up the results
wins_a = sum(1 for r in results if r[0] > r[1])
wins_b = sum(1 for r in results if r[1] > r[0])
draws = sum(1 for r in results if r[0] == r[1])
scorelines = Counter(results)

prob_a_win = (wins_a / NUM_SIMULATIONS) * 100
prob_b_win = (wins_b / NUM_SIMULATIONS) * 100
prob_draw = (draws / NUM_SIMULATIONS) * 100

print("--- Win Probabilities ---")
print(f"{team_a_name} Win: {prob_a_win:.1f}%")
print(f"Draw: {prob_draw:.1f}%")
print(f"{team_b_name} Win: {prob_b_win:.1f}%")

print("\n--- Top 5 Most Likely Scorelines ---")
for scoreline, count in scorelines.most_common(5):
    prob = (count / NUM_SIMULATIONS) * 100
    print(f"{scoreline[0]} - {scoreline[1]} : {prob:.1f}%")