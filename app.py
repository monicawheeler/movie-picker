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
    if os.environ.get("GOOGLE_CREDENTIALS"):
        creds_dict = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
        gc = gspread.service_account_from_dict(creds_dict)
    else:
        gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    return gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/get-status', methods=['GET'])
def get_status():
    try:
        ws = get_db_connection()
        records = ws.get_all_records()
        
        # Default State
        current_turn = USER_A
        app_state = "ready" # ready | pending
        pending_category = ""

        if records:
            last_row = records[-1]
            last_picker = last_row.get('Picker_Name')
            last_movie = last_row.get('Movie_Title')
            last_category = last_row.get('Category')

            # CHECK: Is the last pick unfinished?
            if last_movie == "PENDING":
                app_state = "pending"
                current_turn = last_picker
                pending_category = last_category
            else:
                # Normal turn rotation
                current_turn = USER_B if last_picker == USER_A else USER_A

        # Get history (Filter out the pending row if it exists)
        history = [r for r in records if r.get('Movie_Title') != "PENDING"]
        history = history[-3:]
        history.reverse()

        return jsonify({
            "status": "success",
            "current_turn": current_turn,
            "app_state": app_state,
            "pending_category": pending_category,
            "history": history
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save-pick', methods=['POST'])
def save_pick():
    try:
        data = request.json
        ws = get_db_connection()
        action_type = data.get('type') # 'initial' or 'final'
        
        if action_type == 'initial':
            # STEP 1: Save Category, set Title to PENDING
            now = datetime.datetime.now()
            row_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                now.strftime("%B"),
                now.strftime("%Y"),
                data.get('picker'),
                data.get('category'),
                "PENDING",  # Movie Title
                ""          # Link
            ]
            ws.append_row(row_data)
            return jsonify({"status": "success", "message": "Category saved! Take your time choosing."})

        elif action_type == 'final':
            # STEP 2: Find the PENDING row and update it
            # We assume the pending row is the LAST row.
            records = ws.get_all_records()
            
            # Row index calculation: 
            # records length + 1 (header) is the last row index.
            row_index = len(records) + 1 
            
            # Double check it is actually pending to be safe
            if records[-1].get('Movie_Title') != "PENDING":
                return jsonify({"status": "error", "message": "No pending pick found at the end of the sheet."}), 400

            # Column F is Movie_Title (6), Column G is IMDb_Link (7)
            ws.update_cell(row_index, 6, data.get('movie_title'))
            ws.update_cell(row_index, 7, data.get('imdb_link'))
            
            return jsonify({"status": "success", "message": "Movie locked in!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
