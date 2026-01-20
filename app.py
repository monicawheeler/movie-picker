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
    },
    {
        "name": "Paranoia Thrillers",
        "desc": "Everyone is lying, watched, or hiding something. Trust no one.",
        "examples": ["The Thing", "Arlington Road", "The Parallax View"]
    },
    {
        "name": "Tech Goes Wrong",
        "desc": "Technology meant to help becomes the problem.",
        "examples": ["Upgrade", "Eagle Eye", "Cam"]
    },
    {
        "name": "Home Invasion (Serious)",
        "desc": "High-tension home invasion stories without cheesy slasher vibes.",
        "examples": ["Funny Games", "Hush", "The Strangers"]
    },
    {
        "name": "Apocalypse Adjacent",
        "desc": "The world is ending, just ended, or quietly falling apart.",
        "examples": ["Children of Men", "The Road", "A Quiet Place"]
    },
    {
        "name": "Single-Location Survival",
        "desc": "One place, no escape, escalating tension.",
        "examples": ["Phone Booth", "Devil", "Frozen"]
    },
    {
        "name": "Man vs the System",
        "desc": "One person pushed to the edge by institutions or bureaucracy.",
        "examples": ["Brazil", "Dark Waters", "Snowpiercer"]
    },
    {
        "name": "Cold & Isolated",
        "desc": "Isolation plus brutal environments equals dread.",
        "examples": ["The Thing", "The Lodge", "30 Days of Night"]
    },
    {
        "name": "Urban Nightmares",
        "desc": "Cities as hostile, dangerous ecosystems.",
        "examples": ["Escape from New York", "Candyman", "The Warriors"]
    },
    {
        "name": "Revenge, But Smart",
        "desc": "Calculated, satisfying revenge without mindless brutality.",
        "examples": ["Blue Ruin", "Oldboy", "I Saw the Devil"]
    },
    {
        "name": "Time Is the Enemy",
        "desc": "Deadlines, loops, or ticking clocks drive everything.",
        "examples": ["Run Lola Run", "Source Code", "In Time"]
    },
    {
        "name": "Hidden Cult Energy",
        "desc": "Something is off, and it’s definitely a cult.",
        "examples": ["The Invitation", "Midsommar", "Kill List"]
    },
    {
        "name": "Psych Experiments Gone Wrong",
        "desc": "People pushed past moral or mental limits.",
        "examples": ["The Stanford Prison Experiment", "Exam", "The Platform"]
    },
    {
        "name": "Neo-Noir Modern",
        "desc": "Dark crime stories with modern polish.",
        "examples": ["Prisoners", "Gone Girl", "Nightcrawler"]
    },
    {
        "name": "One Person Against the Wild",
        "desc": "Solo survival stories with real stakes.",
        "examples": ["All Is Lost", "Arctic", "127 Hours"]
    },
    {
        "name": "Disaster Escalation",
        "desc": "Everything keeps getting worse in spectacular ways.",
        "examples": ["Deepwater Horizon", "Greenland", "The Impossible"]
    },
    {
        "name": "Twisted Family Dynamics",
        "desc": "Families as the source of tension or horror.",
        "examples": ["Hereditary", "The Killing of a Sacred Deer", "We Need to Talk About Kevin"]
    },
    {
        "name": "Contained Sci-Fi Concepts",
        "desc": "Small-scale sci-fi ideas executed tightly.",
        "examples": ["Moon", "Primer", "Coherence"]
    },
    {
        "name": "Lawless Places",
        "desc": "Settings where rules don’t apply and danger reigns.",
        "examples": ["Sicario", "No Country for Old Men", "Elite Squad"]
    },
    {
        "name": "People Trapped Together",
        "desc": "Forced proximity turns volatile fast.",
        "examples": ["The Hateful Eight", "The Mist", "Cube"]
    },
    {
        "name": "Unreliable Reality",
        "desc": "You can’t trust what you’re seeing.",
        "examples": ["Jacob’s Ladder", "Enemy", "Perfect Blue"]
    },
    {
        "name": "Dark What-Ifs",
        "desc": "One speculative idea taken seriously.",
        "examples": ["The Purge", "The Lobster", "The Platform"]
    },
    {
        "name": "Survival Horror Lite",
        "desc": "Scary and tense without extreme gore.",
        "examples": ["The Descent", "The Ruins", "As Above, So Below"]
    },
    {
        "name": "Criminal Masterminds",
        "desc": "Smart criminals executing bold plans.",
        "examples": ["Heat", "Inside Man", "The Town"]
    },
    {
        "name": "Escapes & Breakouts",
        "desc": "Break free or die trying.",
        "examples": ["The Shawshank Redemption", "Escape from Alcatraz", "Papillon"]
    },
    {
        "name": "Nature Is Angry",
        "desc": "Animals or environments turning lethal.",
        "examples": ["Backcountry", "The Edge", "Crawl"]
    },
    {
        "name": "Claustrophobic Horror",
        "desc": "Tight spaces amplify the fear.",
        "examples": ["The Descent", "Buried", "The Cave"]
    },
    {
        "name": "Conspiracy Thrillers",
        "desc": "Layers of secrets and powerful enemies.",
        "examples": ["Enemy of the State", "The Conversation", "Three Days of the Condor"]
    },
    {
        "name": "Morality Under Pressure",
        "desc": "Ethical choices with no good outcomes.",
        "examples": ["Eye in the Sky", "Prisoners", "Gone Baby Gone"]
    },
    {
        "name": "Strangers in Trouble",
        "desc": "Ordinary people caught in extraordinary danger.",
        "examples": ["Calibre", "Breakdown", "Judgment Night"]
    },
    {
        "name": "Reality TV From Hell",
        "desc": "Games, competitions, or shows with deadly stakes.",
        "examples": ["Battle Royale", "The Running Man", "Circle"]
    },
    {
        "name": "Psychological Survival",
        "desc": "Endurance of the mind matters as much as the body.",
        "examples": ["Black Swan", "The Lighthouse", "The Machinist"]
    },
    {
        "name": "Slow-Burn Payoff",
        "desc": "Patient storytelling with strong final acts.",
        "examples": ["The Witch", "Take Shelter", "The Night House"]
    },
    {
        "name": "Hostile Journeys",
        "desc": "Travel becomes a nightmare.",
        "examples": ["The Hitcher", "Calibre", "Wrong Turn"]
    },
    {
        "name": "Rules-Based Horror",
        "desc": "The horror follows clear but terrifying rules.",
        "examples": ["It Follows", "A Quiet Place", "Smile"]
    },
    {
        "name": "Contained Action",
        "desc": "Action movies set in tight spaces.",
        "examples": ["Dredd", "The Raid", "Snowpiercer"]
    },
    {
        "name": "Manhunts",
        "desc": "Someone is being hunted relentlessly.",
        "examples": ["No Country for Old Men", "The Fugitive", "Hardcore Henry"]
    },
    {
        "name": "Moral Gray Heroes",
        "desc": "Protagonists doing bad things for understandable reasons.",
        "examples": ["Sicario", "Drive", "A History of Violence"]
    },
    {
        "name": "Contained Mysteries",
        "desc": "Mysteries limited to one place or event.",
        "examples": ["Identity", "Bad Times at the El Royale", "Devil"]
    },
    {
        "name": "Late-Night Chaos",
        "desc": "Movies that feel best watched after dark.",
        "examples": ["After Hours", "Good Time", "Nightcrawler"]
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
    try:
        # 1. Fetch the log from the spreadsheet
        ws = get_db_connection()
        records = ws.get_all_records()
        
        # 2. Create a set of all category names that appear in the 'Category' column
        #    (We use a set for faster lookups)
        used_names = {row['Category'] for row in records if row.get('Category')}
        
    except Exception as e:
        # Fallback: If DB fails, assume nothing is used so the app still loads
        print(f"Error fetching used categories: {e}")
        used_names = set()

    # 3. Create a new list with the 'used' flag attached
    categories_with_status = []
    for cat in CATEGORIES:
        new_cat = cat.copy() # Create a copy so we don't edit the global list
        # Check if this category name exists in our 'used' set
        new_cat['used'] = (cat['name'] in used_names)
        categories_with_status.append(new_cat)

    # 4. Pass this "smart" list to the frontend
    return render_template('index.html', categories=categories_with_status, user_a=USER_A, user_b=USER_B)

@app.route('/get-status', methods=['GET'])
def get_status():
    try:
        ws = get_db_connection()
        records = ws.get_all_records()
        
        app_state = "ready"
        pending_category = ""

        # Check last row for "PENDING"
        if records:
            last_row = records[-1]
            # In the new sheet structure, check if picks are empty or marked PENDING
            if last_row.get('User_A_Pick') == "PENDING":
                app_state = "pending"
                pending_category = last_row.get('Category')

        # Get history (Filter out pending)
        history = [r for r in records if r.get('User_A_Pick') != "PENDING"]
        history = history[-3:]
        history.reverse()

        return jsonify({
            "status": "success",
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
        action_type = data.get('type') 
        
        # --- CASE 1: "Save for Later" (User clicked the hourglass button)
        if action_type == 'initial':
            now = datetime.datetime.now()
            row_data = [
                now.strftime("%Y-%m-%d"), 
                data.get('category'),     
                "PENDING",                
                "",                       
                "PENDING",                
                ""                        
            ]
            ws.append_row(row_data)
            return jsonify({"status": "success", "message": "Category saved! You can finish this later."})

        # --- CASE 2: "Lock in Both Movies" (User clicked the lock button)
        elif action_type == 'final':
            records = ws.get_all_records()
            
            # 1. Determine if we are UPDATING a pending row or CREATING a new one
            is_pending_update = False
            
            # Check if records exist AND if the last one is marked PENDING
            if records and records[-1].get('User_A_Pick') == "PENDING":
                is_pending_update = True
            
            if is_pending_update:
                # --- UPDATE EXISTING ROW ---
                row_index = len(records) + 1 
                updates = [
                    {'range': f'C{row_index}', 'values': [[data.get('user_a_title')]]},
                    {'range': f'D{row_index}', 'values': [[data.get('user_a_link')]]},
                    {'range': f'E{row_index}', 'values': [[data.get('user_b_title')]]},
                    {'range': f'F{row_index}', 'values': [[data.get('user_b_link')]]},
                ]
                ws.batch_update(updates)
                
            else:
                # --- CREATE NEW COMPLETE ROW ---
                # This handles the "Spin -> Immediate Save" flow
                now = datetime.datetime.now()
                row_data = [
                    now.strftime("%Y-%m-%d"), 
                    data.get('category'),  # Ensure JS sends this!
                    data.get('user_a_title'),
                    data.get('user_a_link'),
                    data.get('user_b_title'),
                    data.get('user_b_link')
                ]
                ws.append_row(row_data)
            
            return jsonify({"status": "success", "message": "Both movies locked in!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2828)
