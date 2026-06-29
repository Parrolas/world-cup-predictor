import requests
import os
from dotenv import load_dotenv

# Load your API key
load_dotenv()
API_KEY = os.getenv("SPORTRADAR_API_KEY")

# DEBUG CHECK: Let's see exactly what Python is reading from your .env file
if not API_KEY:
    print("❌ ERROR: API Key is not loading! Check your .env file.")
else:
    # This prints the first 4 and last 4 characters just to be safe
    print(f"✅ API Key loaded: {API_KEY[:4]}...{API_KEY[-4:]}")

# The date we want to check
date = "2024-11-14"

# We will pass the API key directly in the URL this time
url = f"https://api.sportradar.com/soccer/trial/v4/en/schedules/2024-11-14/summaries.json?api_key={API_KEY}"

print(f"\nFetching matches for 2024-11-14...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    summaries = data.get('summaries', [])
    
    print(f"Found {len(summaries)} matches!\n")
    
    # Loop through and print the Match IDs
    for match in summaries:
        match_id = match.get('sport_event', {}).get('id')
        home_team = match.get('sport_event', {}).get('competitors', [{}])[0].get('name', 'Unknown')
        away_team = match.get('sport_event', {}).get('competitors', [{}])[1].get('name', 'Unknown')
        
        print(f"Match ID: {match_id} | {home_team} vs {away_team}")
else:
    print(f"Error {response.status_code}: {response.text}")