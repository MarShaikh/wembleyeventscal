# app.py

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import json
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVENTS_URL = "https://raw.githubusercontent.com/MarShaikh/wembleyeventscal/main/wembleyCalendar/events_data.json"

def fetch_events():
    try:
        response = requests.get(EVENTS_URL)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching events data: {str(e)}")
        return []
    except json.JSONDecodeError:
        logger.error("Error decoding events data. Returning empty list.")
        return []

@app.route('/api/events')
def get_events():
    try:
        events = fetch_events()
        return jsonify(events), 200
    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Serve the main site at the root URL
@app.route('/')
def main_site():
    return send_from_directory('/home/marshaikh/mysite/static/main_site', 'index.html')

# Serve the calendar site at /cal/
@app.route('/cal/')
def cal_site():
    return send_from_directory('/home/marshaikh/mysite/static/cal_site', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)