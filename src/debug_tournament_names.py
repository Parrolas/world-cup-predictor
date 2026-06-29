import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# CONCACAF WCQ Round 3 ran Nov 2024, UEFA WCQ ran Mar-Nov 2025
TEST_DATES = [
    "2024-11-19",  # CONCACAF R3 final window
    "2025-03-26",  # UEFA first matchday (5-team groups)
    "2025-09-09",  # UEFA mid-campaign
    "2025-11-15",  # UEFA final group matchday
    "2026-03-26",  # UEFA playoffs
]

WCQ_KEYWORDS = [
    'world cup qualif',
    'asian qualif',
    'africa cup of nations qualif',
    'concacaf w',   # catches "CONCACAF W Cup Qual" but not "CONCACAF Nations League"
]

seen_ids = set()

for date in TEST_DATES:
    url = f"https://api.sportradar.com/soccer/trial/v4/en/schedules/{date}/summaries.json?api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"{date} → HTTP {response.status_code}")
        time.sleep(1.2)
        continue

    summaries = response.json().get('summaries', [])
    print(f"\n{date}  |  {len(summaries)} matches")

    for match in summaries:
        ctx = match.get('sport_event', {}).get('sport_event_context', {})
        comp = ctx.get('competition', {})
        name = comp.get('name', '')
        comp_id = comp.get('id', '')

        # Print ANY competition we haven't seen yet that contains
        # "world cup", "qualif", "concacaf", or "uefa" — wide net
        lower = name.lower()
        if ('world cup' in lower or 'qualif' in lower or
            ('concacaf' in lower and 'nations' not in lower) or
            ('uefa' in lower and 'nations' not in lower and 'u1' not in lower and 'u2' not in lower)):
            if comp_id not in seen_ids:
                seen_ids.add(comp_id)
                print(f"  ✅ ID: {comp_id}  |  Name: '{name}'")

    time.sleep(1.2)