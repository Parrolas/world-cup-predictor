import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# Venezuela vs Brazil
MATCH_ID = "sr:sport_event:54622891" 

url = f"https://api.sportradar.com/soccer/trial/v4/en/sport_events/{MATCH_ID}/timeline.json?api_key={API_KEY}"

print("Fetching raw data...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Let's see what the top level of the data looks like
    print("\n--- Top Level Keys ---")
    print(list(data.keys()))
    
    # Let's look at the timeline
    timeline = data.get('timeline', [])
    print(f"\nNumber of periods in timeline: {len(timeline)}")
    
    if len(timeline) > 0:
        print("\n--- Raw JSON of the FIRST period ---")
        # This prints the raw JSON beautifully formatted so we can read it
        print(json.dumps(timeline[0], indent=2)[:3000]) # Only printing first 3000 characters so it doesn't crash your screen
    else:
        print("\nTimeline is completely empty! Sportradar is not sending event data.")
        print("Here is the entire response:")
        print(json.dumps(data, indent=2)[:3000])
else:
    print(f"Error {response.status_code}: {response.text}")