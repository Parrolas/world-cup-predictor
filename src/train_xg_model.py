import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import joblib
import os

# 1. Load the data
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "data", "all_qualifier_shots.csv")
df = pd.read_csv(data_path)

# 2. SMART COORDINATE FLIP (Same as build_xg_model.py)
df['x_standard'] = df.apply(lambda row: 100 - row['x'] if row['x'] < 50 else row['x'], axis=1)
df['y_standard'] = df.apply(lambda row: 100 - row['y'] if row['x'] < 50 else row['y'], axis=1)

# 3. FEATURE ENGINEERING: Calculate Distance and Angle
goal_x = 100
goal_y = 50
df['distance'] = np.sqrt((goal_x - df['x_standard'])**2 + (goal_y - df['y_standard'])**2)

left_post_y = 53.66
right_post_y = 46.34
angle_left = np.arctan2(left_post_y - df['y_standard'], goal_x - df['x_standard'])
angle_right = np.arctan2(right_post_y - df['y_standard'], goal_x - df['x_standard'])
df['angle'] = np.abs(np.degrees(angle_left - angle_right))

# 4. Prepare the data for Machine Learning
X = df[['distance', 'angle']]
y = df['is_goal']

# Split the data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train the Model!
print("Training Logistic Regression model on 2,241 shots...")
model = LogisticRegression()
model.fit(X_train, y_train)

# 6. Evaluate the Model
predictions = model.predict_proba(X_test)[:, 1]
try:
    auc = roc_auc_score(y_test, predictions)
    print(f"Model ROC AUC Score: {auc:.2f} (1.0 is perfect, 0.5 is random guessing)")
except ValueError:
    print("Not enough goals in the test set to calculate ROC AUC, but model is trained!")

# 7. Save the Model
models_folder = os.path.join(base_dir, "models")
os.makedirs(models_folder, exist_ok=True)
model_path = os.path.join(models_folder, "xg_model.joblib")
joblib.dump(model, model_path)
print(f"\n✅ Model saved to: {model_path}")

# 8. Test it out!
# Test a shot from 10 meters out, directly in front of the goal (angle ~ 20 degrees)
test_shot = pd.DataFrame({'distance': [10.0], 'angle': [20.0]})
predicted_xg = model.predict_proba(test_shot)[0][1]

print(f"\n--- PREDICTION TEST ---")
print(f"Shot from 10m, angle 20° -> xG = {predicted_xg:.2f}")