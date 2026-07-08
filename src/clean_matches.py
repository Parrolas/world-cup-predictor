import pandas as pd
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "data", "qualifier_match_ids.csv")
df = pd.read_csv(csv_path)

print(f"Original matches found: {len(df)}")

# 1. Let's count how many ACTUAL World Cup tournament matches we have!
# (Looking for 'world cup' but NOT 'qualif')
wc_mask = df['competition'].str.contains('world cup', case=False, na=False) & ~df['competition'].str.contains('qualif', case=False, na=False)
print(f"🏆 FIFA World Cup tournament matches found: {wc_mask.sum()}")

# 2. Drop Youth and Women's tournaments
drop_keywords = ['U17', 'U18', 'U19', 'U20', 'U21', 'U23', 'Youth', 'Toulon', 'Women']
youth_mask = df['competition'].str.contains('|'.join(drop_keywords), case=False, na=False)
df_clean = df[~youth_mask]

print(f"After dropping youth and women's tournaments: {len(df_clean)}")

# 3. OPTIONAL: Drop Friendlies?
# Friendlies can mess up Elo because teams don't try their hardest.
# Remove the '#' from the next 3 lines if you want ONLY competitive games!
# friendly_mask = df_clean['competition'].str.contains('friendly', case=False, na=False)
# df_clean = df_clean[~friendly_mask]
# print(f"After dropping friendlies: {len(df_clean)}")

# Save the cleaned IDs to the mass_pull file
ids_path = os.path.join(base_dir, "data", "qualifier_match_ids_only.txt")
with open(ids_path, 'w') as f:
    for _, row in df_clean.iterrows():
        f.write(f'    "{row["match_id"]}",  # {row["date"]} | {row["home_team"]} vs {row["away_team"]}\n')

print(f"\n✅ Cleaned IDs saved to: {ids_path}")
print("You can now copy and paste these directly into mass_pull.py!")