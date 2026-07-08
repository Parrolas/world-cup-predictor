import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import requests.exceptions

# 1. SETUP: Load the API key securely from the .env file
load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# Sportradar API URL structure
ACCESS_LEVEL = "trial"
VERSION = "v4"  
LANGUAGE = "en"
BASE_URL = f"https://api.sportradar.com/soccer/{ACCESS_LEVEL}/{VERSION}/{LANGUAGE}"

# 2. THE MATCH IDS: Paste the IDs you found from the website here!
MATCH_IDS = [
    "sr:sport_event:66457026",  # 2026-06-28 | Jordan vs Argentina
    "sr:sport_event:66457028",  # 2026-06-28 | Algeria vs Austria
    "sr:sport_event:53452557",  # 2026-06-29 | Brazil vs Japan
    "sr:sport_event:53452541",  # 2026-06-29 | Germany vs Paraguay
    "sr:sport_event:53452547",  # 2026-06-30 | Netherlands vs Morocco
    "sr:sport_event:53452561",  # 2026-06-30 | Ivory Coast vs Norway
    "sr:sport_event:53452543",  # 2026-06-30 | France vs Sweden
    "sr:sport_event:53452555",  # 2026-07-01 | Belgium vs Senegal
    "sr:sport_event:53452565",  # 2026-07-01 | England vs Congo DR
    "sr:sport_event:53452563",  # 2026-07-01 | Mexico vs Ecuador
    "sr:sport_event:53452553",  # 2026-07-02 | USA vs Bosnia and Herzegovina
    "sr:sport_event:53452551",  # 2026-07-02 | Spain vs Austria
    "sr:sport_event:53452549",  # 2026-07-02 | Portugal vs Croatia
    "sr:sport_event:53452503",  # 2026-07-03 | Australia vs Egypt
    "sr:sport_event:53452505",  # 2026-07-03 | Switzerland vs Algeria
    "sr:sport_event:53452507",  # 2026-07-04 | Colombia vs Ghana
    "sr:sport_event:53452519",  # 2026-07-06 | Mexico vs England
    "sr:sport_event:53452513",  # 2026-07-06 | Portugal vs Spain
    "sr:sport_event:53452515",  # 2026-07-07 | USA vs Belgium
    "sr:sport_event:53452521",  # 2026-07-07 | Argentina vs Egypt
    "sr:sport_event:53452523",  # 2026-07-07 | Switzerland vs Colombia
]

def get_match_timeline(match_id, retries=0):
    """
    Fetches the timeline of a specific match, with max 3 retries.
    Handles BOTH Rate Limits (429) AND Network Drops (ConnectionError).
    """
    url = f"{BASE_URL}/sport_events/{match_id}/timeline.json"
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # THIS IS THE FIX! If the Wi-Fi drops, wait 5 seconds and try again.
        if retries < 3:
            print(f"   ⚠️ Network dropped on {match_id}. Retrying in 5 seconds... (Attempt {retries+1}/3)")
            time.sleep(5)
            return get_match_timeline(match_id, retries + 1)
        else:
            print(f"   ❌ Network failed 3 times on {match_id}. Skipping.")
            return None
    
    # If successful (Status 200), return the data
    if response.status_code == 200:
        return response.json()
    # If we hit the rate limit (Status 429)
    elif response.status_code == 429:
        if retries < 3:
            print(f"   ⚠️ Rate limit hit on {match_id}. Sleeping for 10 seconds... (Attempt {retries+1}/3)")
            time.sleep(10)
            return get_match_timeline(match_id, retries + 1)
        else:
            print(f"   ❌ Rate limit failed 3 times on {match_id}. Skipping.")
            return None
    else:
        print(f"   ❌ Error {response.status_code} on match {match_id}")
        return None

def extract_shots_from_timeline(timeline_data, match_id):
    """
    Parses the Sportradar timeline JSON and pulls out ONLY the shots 
    and their X/Y coordinates, AND maps the real team names!
    """
    shots_data = []
    events = timeline_data.get('timeline', [])
    
    # NEW: Grab the real team names from the match data!
    competitors = timeline_data.get('sport_event', {}).get('competitors', [])
    home_team = competitors[0].get('name', 'Home Team') if len(competitors) > 0 else 'Home Team'
    away_team = competitors[1].get('name', 'Away Team') if len(competitors) > 1 else 'Away Team'
    
    shot_types = ['shot_off_target', 'shot_on_target', 'shot_saved', 'score_change']
    
    for event in events:
        if event.get('type') in shot_types:
            
            # Get the X and Y coordinates
            x = event.get('x')
            y = event.get('y')
            
            # If coordinates exist, save the shot data
            if x is not None and y is not None:
                is_goal = 1 if event.get('type') == 'score_change' else 0
                
                # NEW: Map 'home' or 'away' to the actual country name!
                competitor_str = event.get('competitor', 'home')
                team_name = home_team if competitor_str == 'home' else away_team
                
                shots_data.append({
                    'match_id': match_id,
                    'x': x, 
                    'y': y,
                    'is_goal': is_goal,
                    'team': team_name  # Now this will say "Brazil" instead of "away"!
                })
                
    return pd.DataFrame(shots_data)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(base_dir, "data")
    os.makedirs(data_folder, exist_ok=True)
    final_path = os.path.join(data_folder, "all_qualifier_shots.csv")
    
    # --- THE INCREMENTAL UPDATE FIX ---
    pulled_match_ids = set()
    # Check if the CSV already exists
    if os.path.isfile(final_path):
        print("Reading existing CSV to see what we already pulled...")
        existing_df = pd.read_csv(final_path)
        # Grab all the match IDs we already have data for
        pulled_match_ids = set(existing_df['match_id'].unique())
        print(f"Found {len(pulled_match_ids)} matches already in the CSV.")
        
        # FILTER: Only pull matches that are NOT in our set!
        matches_to_pull = [m for m in MATCH_IDS if m not in pulled_match_ids]
        print(f"{len(MATCH_IDS) - len(matches_to_pull)} matches already pulled. Skipping them.")
    else:
        matches_to_pull = MATCH_IDS
        
    all_shots = [] # This list will hold the NEW shots
    
    # If there are no new matches, exit early!
    if len(matches_to_pull) == 0:
        print("\n✅ Database is already up to date! No new matches to pull.")
        exit()
        
    print(f"\nStarting mass pull of {len(matches_to_pull)} NEW matches...")
    
    for i, match_id in enumerate(matches_to_pull):
        print(f"Fetching match {i+1}/{len(matches_to_pull)} - ID: {match_id}")
        
        # Fetch the data
        timeline = get_match_timeline(match_id)
        
        # Extract the shots
        if timeline:
            shots_df = extract_shots_from_timeline(timeline, match_id)
            if not shots_df.empty:
                all_shots.append(shots_df)
                print(f"   ✅ Found {len(shots_df)} shots!")
            else:
                print("   ⚠️ No shots found in this match.")
        
        # THE COOLDOWN
        time.sleep(2.5)
        
        # Save progress every 50 matches
        if (i + 1) % 50 == 0 and all_shots:
            temp_df = pd.concat(all_shots, ignore_index=True)
            file_exists = os.path.isfile(final_path)
            temp_df.to_csv(final_path, mode='a', index=False, header=not file_exists)
            print("   💾 Progress saved!")
    
    # FINAL SAVE: Append the new shots to the existing CSV!
    if all_shots:
        final_df = pd.concat(all_shots, ignore_index=True)
        file_exists = os.path.isfile(final_path)
        # mode='a' means append! header=not file_exists means only write header if file is new.
        final_df.to_csv(final_path, mode='a', index=False, header=not file_exists)
        print(f"\n🎉 SUCCESS! Appended {len(final_df)} NEW shots to {final_path}")
    else:
        print("\n❌ No new shots found.")