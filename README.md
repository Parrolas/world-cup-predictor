# 2026 World Cup Match Predictor

A machine learning pipeline that predicts international soccer match outcomes by calculating Expected Goals (xG) from shot coordinates and simulating games using custom Attacking/Defensive Elo ratings.

## How It Works

The project is broken down into four main steps:

1. **Data Collection (`mass_pull.py`)**  
   Pulls real match event data and X/Y shot coordinates for 900+ international matches using the Sportradar Soccer API.

2. **xG Machine Learning Model (`train_xg_model.py`)**  
   Uses trigonometry to calculate the distance and angle of over 10,000 real shots. A Logistic Regression model is trained on this data to calculate the exact probability of a shot becoming a goal (Expected Goals or xG).

3. **Attacking / Defensive Elo (`elo_engine.py`)**  
   Instead of using actual goals, this engine uses the xG predictions to update custom Elo ratings for every team. Teams are seeded using official FIFA rankings to account for strength of schedule.

4. **Match Simulator (`simulator.py`)**  
   Takes two teams' Elo ratings, calculates expected goals, and runs a 10,000-iteration Monte Carlo simulation using the Poisson distribution to output win probabilities and exact scorelines.

## Example Output

```text
--- Match Simulation: France vs Brazil ---
Expected Goals: France 1.52 - 1.20 Brazil

--- Win Probabilities ---
France Win: 42.5%
Draw: 26.1%
Brazil Win: 31.4%

--- Top 5 Most Likely Scorelines ---
1 - 1 : 12.3%
1 - 0 : 10.5%
2 - 1 : 9.2%
0 - 0 : 8.8%
2 - 0 : 7.5%
```

## Tech Stack
* **Python**
* **Pandas & NumPy** (Data manipulation and trigonometry)
* **Scikit-Learn** (Logistic Regression for the xG model)
* **Matplotlib & mplsoccer** (Pitch visualizations)
* **Requests** (Sportradar API integration)

## How to Run

1. Clone the repository.

2. Install the required packages:
   ```bash
   pip install pandas numpy scikit-learn matplotlib mplsoccer requests python-dotenv
   ```
3. Get a Sportradar API key and save it in a `.env` file:
   ```text
   SPORTRADAR_API_KEY=your_api_key_here
   ```
4. Run the pipeline scripts in order:
   ```bash
   python src/get_qualifier_ids.py   # Finds match IDs
   python src/clean_matches.py       # Filters out youth/friendlies
   python src/mass_pull.py           # Pulls shot coordinates
   python src/train_xg_model.py      # Trains and saves the xG model
   python src/elo_engine.py          # Calculates team Elo ratings
   python src/simulator.py           # Run the interactive match predictor!
   ```

***