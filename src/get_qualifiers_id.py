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
    "2026-06-28", "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02",
    "2026-07-03", "2026-07-04", "2026-07-05", "2026-07-06", "2026-07-07"
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