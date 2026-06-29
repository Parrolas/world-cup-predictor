import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import os

# 1. Load the data
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "data", "all_qualifier_shots.csv")

print(f"Loading shots data from: {data_path}")
df = pd.read_csv(data_path)


# 2. COORDINATE FLIP (THE SMART FIX!)
# If the shot was taken on the left half of the pitch (x < 50), 
# it means they are attacking the left goal. We flip those coordinates 
# so ALL shots attack the right goal (x=100).
df['x_standard'] = df.apply(lambda row: 100 - row['x'] if row['x'] < 50 else row['x'], axis=1)
df['y_standard'] = df.apply(lambda row: 100 - row['y'] if row['x'] < 50 else row['y'], axis=1)

# 3. FEATURE ENGINEERING: Calculate Distance and Angle
goal_x = 100
goal_y = 50

# Now we calculate distance using the standardized coordinates
df['distance'] = np.sqrt((goal_x - df['x_standard'])**2 + (goal_y - df['y_standard'])**2)

left_post_y = 53.66
right_post_y = 46.34

angle_left = np.arctan2(left_post_y - df['y_standard'], goal_x - df['x_standard'])
angle_right = np.arctan2(right_post_y - df['y_standard'], goal_x - df['x_standard'])

df['angle'] = np.abs(np.degrees(angle_left - angle_right))

print("\n--- Shots with Fixed Features ---")
print(df[['x_standard', 'y_standard', 'distance', 'angle', 'is_goal']].head(10))

# 4. VISUALIZATION
pitch = Pitch(pitch_type='statsbomb', line_color='black', pitch_color='#aabb97')
fig, ax = pitch.draw(figsize=(10, 6))

# Convert 0-100 scale to 0-120 (x) and 0-80 (y) for plotting
df['x_plot'] = df['x_standard'] * 1.2
df['y_plot'] = df['y_standard'] * 0.8

for index, row in df.iterrows():
    color = 'red' if row['distance'] < 30 else 'blue'
    size = row['angle'] * 15
    
    if row['is_goal'] == 1:
        ax.scatter(row['x_plot'], row['y_plot'], s=200, color='yellow', marker='*', edgecolors='black', zorder=5)
    else:
        ax.scatter(row['x_plot'], row['y_plot'], s=size, color=color, alpha=0.7, edgecolors='black', zorder=3)

plt.title("Stage 3: Fixed Shot Map (All Attacking Right)", color='black', fontsize=14)
plt.show()