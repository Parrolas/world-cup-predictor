import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# ============================================================
# STRATEGY: Query by competition ID where we have them,
# then fall back to date scanning for UEFA + CONCACAF WCQ,
# filtering purely by qualified team names.
# ============================================================

# --- Competition IDs confirmed from debug runs ---
KNOWN_WCQ_COMPETITION_IDS = {
    "sr:competition:295":  "FIFA World Cup Qualification, CONMEBOL",
    "sr:competition:308":  "AFC Asian Qualifiers 2026",
    "sr:competition:1848": "Africa Cup of Nations Qualification",  # CAF WCQ
    "sr:competition:309":  "FIFA World Cup Qualification, OFC",
}

# --- All 48 qualified teams (Sportradar spelling) ---
QUALIFIED_TEAMS = {
    # CONMEBOL
    "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
    # UEFA
    "Austria", "Belgium", "Bosnia and Herzegovina", "Croatia", "Czech Republic",
    "England", "France", "Germany", "Netherlands", "Norway", "Portugal",
    "Scotland", "Spain", "Sweden", "Switzerland", "Turkey",
    # AFC
    "Australia", "Iraq", "Iran", "Japan", "Jordan",
    "South Korea", "Qatar", "Saudi Arabia", "Uzbekistan",
    # CAF
    "Algeria", "Cape Verde", "DR Congo", "Ivory Coast", "Egypt",
    "Ghana", "Morocco", "Senegal", "South Africa", "Tunisia",
    # CONCACAF
    "Canada", "Curacao", "Haiti", "Mexico", "Panama", "United States",
    # OFC
    "New Zealand",
}

# --- Date windows for UEFA + CONCACAF WCQ (not covered by competition ID) ---
# These are the only dates we need to scan
UEFA_CONCACAF_DATES = [
    # --- 2021/2022 Historical WCQ Dates ---
    "2021-09-01", "2021-09-02", "2021-09-03", "2021-09-04", "2021-09-05", "2021-09-06", "2021-09-07", "2021-09-08",
    "2021-10-07", "2021-10-08", "2021-10-09", "2021-10-10", "2021-10-11", "2021-10-12", "2021-10-13", "2021-10-14",
    "2021-11-11", "2021-11-12", "2021-11-13", "2021-11-14", "2021-11-15", "2021-11-16", "2021-11-17",
    "2022-01-27", "2022-01-28", "2022-01-29", "2022-01-30", "2022-01-31", "2022-02-01", "2022-02-02",
    "2022-03-24", "2022-03-25", "2022-03-26", "2022-03-27", "2022-03-28", "2022-03-29", "2022-03-30",
    
    # --- 2023 International Windows ---
    "2023-03-23", "2023-03-24", "2023-03-25", "2023-03-26", "2023-03-27", "2023-03-28",
    "2023-06-12", "2023-06-13", "2023-06-14", "2023-06-15", "2023-06-16", "2023-06-17", "2023-06-18", "2023-06-19", "2023-06-20",
    "2023-09-04", "2023-09-05", "2023-09-06", "2023-09-07", "2023-09-08", "2023-09-09", "2023-09-10", "2023-09-11", "2023-09-12",
    "2023-10-09", "2023-10-10", "2023-10-11", "2023-10-12", "2023-10-13", "2023-10-14", "2023-10-15", "2023-10-16", "2023-10-17",
    "2023-11-13", "2023-11-14", "2023-11-15", "2023-11-16", "2023-11-17", "2023-11-18", "2023-11-19", "2023-11-20", "2023-11-21",

    # CONCACAF WCQ Round 2 (Mar–Jun 2024)
    "2024-03-21", "2024-03-22", "2024-03-23", "2024-03-24", "2024-03-25", "2024-03-26",
    "2024-06-05", "2024-06-06", "2024-06-07", "2024-06-08", "2024-06-09", "2024-06-10",
    # CONCACAF WCQ Round 3 (Oct–Nov 2024)
    "2024-10-10", "2024-10-11", "2024-10-12", "2024-10-13", "2024-10-14", "2024-10-15",
    "2024-11-14", "2024-11-15", "2024-11-16", "2024-11-17", "2024-11-18", "2024-11-19",
    # UEFA WCQ (Mar–Nov 2025)
    "2025-03-20", "2025-03-21", "2025-03-22", "2025-03-23", "2025-03-24", "2025-03-25",
    "2025-06-05", "2025-06-06", "2025-06-07", "2025-06-08", "2025-06-09", "2025-06-10",
    "2025-09-04", "2025-09-05", "2025-09-06", "2025-09-07", "2025-09-08", "2025-09-09",
    "2025-10-09", "2025-10-10", "2025-10-11", "2025-10-12", "2025-10-13", "2025-10-14",
    "2025-11-13", "2025-11-14", "2025-11-15", "2025-11-16", "2025-11-17", "2025-11-18",
    # UEFA + inter-confederation playoffs (Mar 2026)
    "2026-03-20", "2026-03-21", "2026-03-22", "2026-03-23", "2026-03-24", "2026-03-25",
    "2026-03-26", "2026-03-27", "2026-03-28", "2026-03-29", "2026-03-30", "2026-03-31",
    "2026-06-11", "2026-06-12", "2026-06-13", "2026-06-14", "2026-06-15", "2026-06-16",
    "2026-06-17", "2026-06-18", "2026-06-19", "2026-06-20", "2026-06-21", "2026-06-22",
    "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26", "2026-06-27"
]

BASE_URL = "https://api.sportradar.com/soccer/trial/v4/en"
seen_match_ids = set()
all_matches = []

def is_qualified_match(home, away):
    """At least one team must be a qualified World Cup nation."""
    return home in QUALIFIED_TEAMS or away in QUALIFIED_TEAMS

def parse_matches(summaries, source_label):
    found = 0
    for match in summaries:
        sport_event = match.get('sport_event', {})
        match_id = sport_event.get('id')

        if not match_id or match_id in seen_match_ids:
            continue

        competitors = sport_event.get('competitors', [])
        if len(competitors) < 2:
            continue

        home = competitors[0].get('name', '')
        away = competitors[1].get('name', '')
        date = sport_event.get('start_time', '')[:10]
        ctx = sport_event.get('sport_event_context', {})
        comp_name = ctx.get('competition', {}).get('name', 'Unknown')

        if is_qualified_match(home, away):
            seen_match_ids.add(match_id)
            all_matches.append({
                'match_id': match_id,
                'home_team': home,
                'away_team': away,
                'date': date,
                'competition': comp_name,
                'source': source_label,
            })
            found += 1
    return found


# ============================================================
# PASS 1: Query known competition IDs directly
# ============================================================
print("=" * 60)
print("PASS 1: Querying known WCQ competition IDs")
print("=" * 60)

for comp_id, comp_name in KNOWN_WCQ_COMPETITION_IDS.items():
    url = f"{BASE_URL}/competitions/{comp_id}/schedules.json?api_key={API_KEY}"
    print(f"\n  Fetching {comp_name}...", end=" ", flush=True)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"HTTP {response.status_code} — skipping")
        time.sleep(1.2)
        continue

    data = response.json()
    # Competition schedules use 'sport_events' not 'summaries'
    sport_events = data.get('schedules', data.get('sport_events', []))

    # Wrap in the same shape as summaries for parse_matches
    wrapped = [{'sport_event': se.get('sport_event', se)} for se in sport_events]
    found = parse_matches(wrapped, comp_name)
    print(f"✅ {found} qualified matches")
    time.sleep(1.2)


# ============================================================
# PASS 2: Date scan for UEFA + CONCACAF (filter by team name)
# ============================================================
print(f"\n{'=' * 60}")
print(f"PASS 2: Date scanning for UEFA + CONCACAF ({len(UEFA_CONCACAF_DATES)} dates)")
print("=" * 60)

for date in UEFA_CONCACAF_DATES:
    url = f"{BASE_URL}/schedules/{date}/summaries.json?api_key={API_KEY}"
    print(f"  {date}...", end=" ", flush=True)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"HTTP {response.status_code}")
        time.sleep(1.2)
        continue

    summaries = response.json().get('summaries', [])

    # Only look at matches where competition name suggests international football
    # (eliminates NCAA, domestic leagues etc. before even checking team names)
    international_summaries = []
    for m in summaries:
        ctx = m.get('sport_event', {}).get('sport_event_context', {})
        comp = ctx.get('competition', {}).get('name', '').lower()
        category = ctx.get('category', {}).get('name', '').lower()
        # Keep if it looks like a senior international competition
        if ('friendly' in comp or 'nations' in comp or 'qualif' in comp or
                'world cup' in comp or 'international' in category):
            international_summaries.append(m)

    found = parse_matches(international_summaries, f"date_scan:{date}")
    if found:
        print(f"✅ {found} new qualified matches")
    else:
        print("—")
    time.sleep(1.2)


# ============================================================
# SAVE RESULTS
# ============================================================
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# Full CSV with metadata
df = pd.DataFrame(all_matches)
if not df.empty:
    df = df.sort_values('date')
    detail_path = os.path.join(data_dir, "qualifier_match_ids.csv")
    df.to_csv(detail_path, index=False)

    # Breakdown by competition
    print(f"\n{'=' * 60}")
    print("MATCHES BY COMPETITION")
    print("=" * 60)
    for comp, group in df.groupby('competition'):
        print(f"  {len(group):>4}  {comp}")

    # IDs-only file ready to paste into mass_pull.py
    ids_path = os.path.join(data_dir, "qualifier_match_ids_only.txt")
    with open(ids_path, 'w') as f:
        for _, row in df.iterrows():
            f.write(f'    "{row["match_id"]}",  # {row["date"]} | {row["home_team"]} vs {row["away_team"]}\n')

    print(f"\n✅  {len(df)} total matches saved")
    print(f"📄  Full CSV      → {detail_path}")
    print(f"📋  mass_pull IDs → {ids_path}")
else:
    print("\n❌ No matches found. Check API key and try again.")