import os
import datetime
from flask import Flask, render_template, request, jsonify
import gspread

app = Flask(__name__)

# --- CONFIGURATION ---
SHEET_NAME = "Movie Night Log"  # Name of your Google Sheet File
WORKSHEET_NAME = "Log"          # Name of the specific tab
SERVICE_ACCOUNT_FILE = 'service_account.json'

# User Configuration
USER_A = "Monica"
USER_B = "John"

# Hardcoded Categories
CATEGORIES = [
    "90s Action", "Foreign Language", "Psychological Thriller", "Cult Classic",
    "80s Sci-Fi", "Oscar Best Picture Winner", "Animated Feature", "Black & White",
    "Directorial Debut", "Horror Comedy", "Whodunit / Mystery", "Documentary",
    "Post-Apocalyptic", "Based on a True Story", "Cyberpunk", "Western",
    "Musical", "A24 / Indie", "Comedy Special", "Spy / Espionage"
]

def get_db_connection():
    """Connects to Google Sheets and returns the worksheet object."""
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open(SHEET_NAME)
    return sh.worksheet(WORKSHEET_NAME)

@app.route('/')
def home():
    """Serves the main HTML page."""
    # Pass categories to frontend to avoid hardcoding in JS too
    return render_template('index.html', categories=CATEGORIES)

@app.route('/get-status', methods=['GET'])
def get_status():
    """Determines whose turn it is and fetches recent history."""
    try:
        ws = get_db_connection()
        records = ws.get_all_records()
        
        # 1. Determine Turn
        if not records:
            current_turn = USER_A # Default start
        else:
            last_picker = records[-1].get('Picker_Name')
            # Toggle logic
            current_turn = USER_B if last_picker == USER_A else USER_A

        # 2. Get Recent History (Last 3, reversed)
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
    """Saves the chosen movie to the sheet."""
    try:
        data = request.json
        ws = get_db_connection()
        
        now = datetime.datetime.now()
        
        row_data = [
            now.strftime("%Y-%m-%d %H:%M:%S"), # Date Timestamp
            now.strftime("%B"),                 # Month
            now.strftime("%Y"),                 # Year
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
    