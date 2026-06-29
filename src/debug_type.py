import requests
import os
from collections import Counter
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
    
    # Let's count the 'type' of every single event in the timeline
    event_types = []
    for event in events:
        event_types.append(event.get('type', 'unknown'))
    
    # Count them up
    counts = Counter(event_types)
    
    print("\n--- Event Types Found in Match ---")
    for event_type, count in counts.items():
        print(f"{event_type}: {count}")
        
else:
    print(f"Error {response.status_code}: {response.text}")