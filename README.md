# 🎬 Movie Night Picker

A Flask web application that helps two people alternate picking movies for movie night. The app randomly selects a category from a curated list, tracks whose turn it is, and logs all picks to a Google Sheet.

## Features

- **Random Category Generator**: Spin to get a random movie category from 20 curated options
- **Turn Tracking**: Automatically tracks whose turn it is to pick (alternates between two users)
- **Google Sheets Integration**: Automatically logs all picks with timestamps to Google Sheets
- **Watch History**: Displays the last 3 movies that were picked
- **Modern Dark Theme UI**: Clean, mobile-friendly interface

## Prerequisites

- Python 3.7 or higher
- A Google account with access to Google Sheets API
- A Google Sheet named "Movie Night Log" with a tab named "Log"
- Google Service Account credentials (JSON file)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd movie-picker
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API for your project
4. Create a Service Account:
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and create it
   - Click on the service account, go to "Keys" tab
   - Click "Add Key" > "Create new key" > Choose JSON
   - Download the JSON file and save it as `service_account.json` in the project root

### 5. Configure Your Google Sheet

1. Create a Google Sheet named "Movie Night Log" (or update `SHEET_NAME` in `app.py`)
2. Create a tab named "Log" (or update `WORKSHEET_NAME` in `app.py`)
3. Set up the following headers in row 1 (in this order):
   - `Date_Timestamp`
   - `Month`
   - `Year`
   - `Picker_Name`
   - `Category`
   - `Movie_Title`
   - `IMDb_Link`
4. Share the Google Sheet with the service account email address (found in `service_account.json`). Give it "Editor" permissions.

### 6. Configure Users

Edit `app.py` and update the user names:

```python
USER_A = "Monica"  # Change to your name
USER_B = "John"    # Change to the other person's name
```

### 7. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

1. **Check whose turn it is**: The status bar at the top shows whose turn it is to pick
2. **Spin for a category**: Click "Spin for Category" to get a random category
3. **Enter movie details**: After spinning, enter:
   - Movie title (required)
   - IMDb link (optional)
4. **Lock it in**: Click "Lock it in 🔒" to save the pick
5. **View history**: The "Recent Watches" section shows the last 3 movies picked

## Project Structure

```
movie-picker/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── service_account.json   # Google Service Account credentials (not in git)
├── templates/
│   └── index.html        # Frontend HTML with embedded JavaScript
├── static/
│   └── style.css         # Dark theme styling
└── README.md             # This file
```

## Configuration

You can customize the following in `app.py`:

- `SHEET_NAME`: Name of your Google Sheet (default: "Movie Night Log")
- `WORKSHEET_NAME`: Name of the worksheet tab (default: "Log")
- `USER_A` and `USER_B`: Names of the two users
- `CATEGORIES`: List of 20 movie categories

## Categories

The app includes 20 predefined categories:
- 90s Action
- Foreign Language
- Psychological Thriller
- Cult Classic
- 80s Sci-Fi
- Oscar Best Picture Winner
- Animated Feature
- Black & White
- Directorial Debut
- Horror Comedy
- Whodunit / Mystery
- Documentary
- Post-Apocalyptic
- Based on a True Story
- Cyberpunk
- Western
- Musical
- A24 / Indie
- Comedy Special
- Spy / Espionage

## Security Note

⚠️ **Important**: Never commit `service_account.json` to version control. This file contains sensitive credentials. It should be listed in `.gitignore` and kept secure.

## Technologies Used

- **Flask 3.0.0**: Web framework
- **gspread 6.0.0**: Google Sheets API wrapper
- **google-auth 2.27.0**: Google authentication library

## License

This project is for personal use.
