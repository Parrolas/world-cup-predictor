import numpy as np
from collections import Counter

# 1. Real Teams and their Elo Ratings (from your new leaderboard!)
team_a = {'name': 'Portugal', 'attacking_elo': 1925, 'defensive_elo': 1811}
team_b = {'name': 'Croatia', 'attacking_elo': 1850, 'defensive_elo': 1764}

# 2. Calculate Expected Goals (xG) for the match
# Formula: (Attack of Team A / Defense of Team B) * Average Goals (1.35)
expected_goals_a = (team_a['attacking_elo'] / team_b['defensive_elo']) * 1.35
expected_goals_b = (team_b['attacking_elo'] / team_a['defensive_elo']) * 1.35

# 3. The Unpredictability Factor 
rating_diff = abs(team_a['attacking_elo'] - team_b['attacking_elo'])
upset_factor = 1.0 + (rating_diff / 1000)

expected_goals_a = max(0.1, expected_goals_a * np.random.normal(1.0, upset_factor * 0.1))
expected_goals_b = max(0.1, expected_goals_b * np.random.normal(1.0, upset_factor * 0.1))

print(f"--- Match Simulation: {team_a['name']} vs {team_b['name']} ---")
print(f"Expected Goals: {team_a['name']} {expected_goals_a:.2f} - {expected_goals_b:.2f} {team_b['name']}\n")

# 4. The Poisson Simulation (Monte Carlo)
NUM_SIMULATIONS = 10000
results = []

for _ in range(NUM_SIMULATIONS):
    goals_a = np.random.poisson(expected_goals_a)
    goals_b = np.random.poisson(expected_goals_b)
    results.append((goals_a, goals_b))

# 5. Tally up the results
wins_a = sum(1 for r in results if r[0] > r[1])
wins_b = sum(1 for r in results if r[1] > r[0])
draws = sum(1 for r in results if r[0] == r[1])
scorelines = Counter(results)

prob_a_win = (wins_a / NUM_SIMULATIONS) * 100
prob_b_win = (wins_b / NUM_SIMULATIONS) * 100
prob_draw = (draws / NUM_SIMULATIONS) * 100

print("--- Win Probabilities ---")
print(f"{team_a['name']} Win: {prob_a_win:.1f}%")
print(f"Draw: {prob_draw:.1f}%")
print(f"{team_b['name']} Win: {prob_b_win:.1f}%")

print("\n--- Top 5 Most Likely Scorelines ---")
for scoreline, count in scorelines.most_common(5):
    prob = (count / NUM_SIMULATIONS) * 100
    print(f"{scoreline[0]} - {scoreline[1]} : {prob:.1f}%")