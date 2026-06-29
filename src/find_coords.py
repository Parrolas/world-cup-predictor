import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

MATCH_ID = "sr:sport_event:54622891" # Venezuela vs Brazil
url = f"https://api.sportradar.com/soccer/trial/v4/en/sport_events/{MATCH_ID}/timeline.json?api_key={API_KEY}"

print("Fetching raw data...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    events = data.get('timeline', [])
    
    shot_types = ['shot_off_target', 'shot_on_target', 'shot_saved', 'score_change']
    
    print("\nSearching for the first shot in the match...")
    for event in events:
        if event.get('type') in shot_types:
            print("\n--- RAW JSON OF A SHOT ---")
            # This prints the raw JSON beautifully formatted
            print(json.dumps(event, indent=2))
            break # Stop after finding the first one!
else:
    print(f"Error {response.status_code}: {response.text}")