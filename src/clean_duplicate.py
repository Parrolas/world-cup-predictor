import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base_dir, "data", "all_qualifier_shots.csv")
df = pd.read_csv(path)

print(f"Shots before deduplication: {len(df)}")
df_clean = df.drop_duplicates()
print(f"Shots after deduplication: {len(df_clean)}")

df_clean.to_csv(path, index=False)
print("✅ CSV cleaned and saved!")