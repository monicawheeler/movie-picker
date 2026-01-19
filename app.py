import os
import datetime
import json
from flask import Flask, render_template, request, jsonify
import gspread

app = Flask(__name__)

# --- CONFIGURATION ---
SHEET_NAME = "Movie Night Log"  
WORKSHEET_NAME = "Log"          
SERVICE_ACCOUNT_FILE = 'service_account.json'

# User Configuration
USER_A = "Monica"
USER_B = "John"

# Expanded Category Data
CATEGORIES = [
    {
        "name": "High-Stakes Thrillers",
        "desc": "Tight pacing, constant tension, and escalating danger with no downtime.",
        "examples": ["Sicario", "Prisoners", "Green Room"]
    },
    {
        "name": "Nightmare Fuel (But Not Gross)",
        "desc": "Deeply unsettling horror that sticks with you without crossing into torture porn.",
        "examples": ["Hereditary", "The Dark and the Wicked", "Sinister"]
    },
    {
        "name": "Sci-Fi With Consequences",
        "desc": "Big sci-fi ideas paired with real emotional, moral, or survival stakes.",
        "examples": ["Ex Machina", "Children of Men", "Arrival"]
    },
    {
        "name": "Creature Features",
        "desc": "Monsters, aliens, or unknown beings that hunt, stalk, or overwhelm.",
        "examples": ["The Descent", "Cloverfield", "Annihilation"]
    },
    {
        "name": "Action That Actually Slaps",
        "desc": "Well-executed action with momentum, clarity, and satisfying set pieces.",
        "examples": ["Mad Max: Fury Road", "The Raid", "John Wick"]
    },
    {
        "name": "Survival Mode",
        "desc": "People versus nature, isolation, or overwhelming odds.",
        "examples": ["The Grey", "28 Days Later", "Fall"]
    },
    {
        "name": "Stylish & Suspenseful",
        "desc": "Atmospheric, visually cool films with slow-burn tension.",
        "examples": ["Drive", "Nocturnal Animals", "Nightcrawler"]
    },
    {
        "name": "Bad Decisions Spiral",
        "desc": "Every choice makes things worse, and you can’t look away.",
        "examples": ["Uncut Gems", "Good Time", "Calibre"]
    },
    {
        "name": "Smart Horror",
        "desc": "Clever concepts, eerie vibes, and payoffs that make sense.",
        "examples": ["It Follows", "The Witch", "Barbarian"]
    },
    {
        "name": "Mind-Bendy (But It Clicks)",
        "desc": "Twists and layered storytelling that reward attention.",
        "examples": ["Coherence", "Shutter Island", "The Prestige"]
    },
    {
        "name": "Sci-Fi Horror Crossover",
        "desc": "Science, space, or tech colliding with fear and dread.",
        "examples": ["Alien", "Event Horizon", "Sunshine"]
    },
    {
        "name": "Mid-Budget Chaos Energy",
        "desc": "Lean, intense movies that punch above their budget.",
        "examples": ["Upgrade", "The Invisible Man", "Dredd"]
    },
    {
        "name": "Under 110 Minutes",
        "desc": "Fast, efficient movies that respect your time.",
        "examples": ["Run Lola Run", "The Invitation", "Host"]
    },
    {
        "name": "Psychological Warfare",
        "desc": "Mental games, manipulation, paranoia, and unraveling minds.",
        "examples": ["Black Swan", "The Game", "Enemy"]
    },
    {
        "name": "Foreign Genre Gems",
        "desc": "International thrillers, horror, or sci-fi that go hard.",
        "examples": ["Train to Busan", "The Wailing", "Headhunters"]
    },
    {
        "name": "Mystery With Teeth",
        "desc": "Dark mysteries where danger is always close.",
        "examples": ["Gone Girl", "Wind River", "Memories of Murder"]
    },
    {
        "name": "Unexpectedly Good",
        "desc": "Low expectations, high payoff, and surprise favorites.",
        "examples": ["The Guest", "Happy Death Day", "Ready or Not"]
    },
    {
        "name": "Edge-of-Your-Seat Sci-Fi",
        "desc": "Momentum-driven sci-fi that never lets the tension drop.",
        "examples": ["Edge of Tomorrow", "Source Code", "District 9"]
    },
    {
        "name": "Fun but Serious",
        "desc": "Entertaining and gripping without being dumb or cheesy.",
        "examples": ["The Departed", "Inception", "Collateral"]
    },
    {
        "name": "Contained Pressure Cookers",
        "desc": "Small casts, limited settings, and maximum tension.",
        "examples": ["10 Cloverfield Lane", "Buried", "The Platform"]
    }
]

def get_db_connection():
    """Connects to Google Sheets using Env Vars (Prod) or local file (Dev)."""
    if os.environ.get("GOOGLE_CREDENTIALS"):
        creds_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
        gc = gspread.service_account_from_dict(creds_dict)
    else:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(WORKSHEET_NAME)

@app.route('/')
def home():
    """Serves the main HTML page."""
    return render_template('index.html', categories=CATEGORIES)

@app.route('/get-status', methods=['GET'])
def get_status():
    try:
        ws = get_db_connection()
        records = ws.get_all_records()
        
        if not records:
            current_turn = USER_A 
        else:
            last_picker = records[-1].get('Picker_Name')
            current_turn = USER_B if last_picker == USER_A else USER_A

        history = records[-3:]
        history.reverse()

        return jsonify({
            "status": "success",
            "current_turn": current_turn,
            "history": history
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save-pick', methods=['POST'])
def save_pick():
    try:
        data = request.json
        ws = get_db_connection()
        now = datetime.datetime.now()
        
        row_data = [
            now.strftime("%Y-%m-%d %H:%M:%S"),
            now.strftime("%B"),
            now.strftime("%Y"),
            data.get('picker'),
            data.get('category'),
            data.get('movie_title'),
            data.get('imdb_link', '')
        ]
        
        ws.append_row(row_data)
        return jsonify({"status": "success", "message": "Movie locked in!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)