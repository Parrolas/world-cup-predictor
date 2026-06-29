import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "data", "qualifier_match_ids.csv")
df = pd.read_csv(csv_path)

print(f"Original matches: {len(df)}")

# Added 'Women' and ' W' to drop women's youth and senior tournaments
drop_keywords = ['U17', 'U18', 'U19', 'U20', 'U21', 'U23', 'Youth', 'Toulon', 'Women', ' W']
mask = df['competition'].str.contains('|'.join(drop_keywords), case=False, na=False)
df_clean = df[~mask]

print(f"After dropping youth and women's tournaments: {len(df_clean)}")

# Save the cleaned IDs to the mass_pull file
ids_path = os.path.join(base_dir, "data", "qualifier_match_ids_only.txt")
with open(ids_path, 'w') as f:
    for _, row in df_clean.iterrows():
        f.write(f'    "{row["match_id"]}",  # {row["date"]} | {row["home_team"]} vs {row["away_team"]}\n')

print(f"\n✅ Cleaned IDs saved to: {ids_path}")
print("You can now copy and paste these directly into mass_pull.py!")