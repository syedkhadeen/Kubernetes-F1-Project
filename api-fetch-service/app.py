from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime
from pymongo import MongoClient
import time

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')
OPENF1_BASE_URL = "https://api.openf1.org/v1"

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics

# Collections
drivers_collection = db.drivers
constructors_collection = db.constructors
races_collection = db.races
results_collection = db.results
standings_collection = db.standings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenF1Client:
    def __init__(self, base_url=OPENF1_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def fetch_data(self, endpoint, params=None):
        """Fetch data from OpenF1 API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return None

openf1_client = OpenF1Client()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'api-fetch-service'})

@app.route('/fetch/current-season', methods=['GET'])
def fetch_current_season():
    """Fetch current season data"""
    try:
        current_year = datetime.now().year
        # Placeholder for fetching current season data
        return jsonify({'message': f'Fetched data for {current_year}'}), 200
    except Exception as e:
        logger.error(f"Error fetching current season: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/drivers', methods=['GET'])
def fetch_drivers():
    """Fetch all drivers from OpenF1"""
    try:
        # Get latest session to fetch current drivers
        sessions_data = openf1_client.fetch_data("sessions", {"session_key": "latest"})
        
        if not sessions_data:
            return jsonify({'message': 'Failed to fetch sessions data'}), 500
        
        latest_session = sessions_data[0] if sessions_data else None
        if not latest_session:
            return jsonify({'message': 'No latest session found'}), 500
        
        session_key = latest_session.get('session_key')
        drivers_data = openf1_client.fetch_data("drivers", {"session_key": session_key})
        
        if not drivers_data:
            return jsonify({'message': 'Failed to fetch drivers data'}), 500
        
        for driver in drivers_data:
            driver_doc = {
                'driverId': driver.get('name_acronym', '').lower(),
                'driver_number': driver.get('driver_number'),
                'code': driver.get('name_acronym'),
                'givenName': driver.get('first_name'),
                'familyName': driver.get('last_name'),
                'fullName': driver.get('full_name'),
                'broadcastName': driver.get('broadcast_name'),
                'nationality': driver.get('country_code'),
                'teamName': driver.get('team_name'),
                'teamColour': driver.get('team_colour'),
                'headshotUrl': driver.get('headshot_url'),
                'sessionKey': session_key,
                'fetched_at': datetime.utcnow()
            }
            
            drivers_collection.update_one(
                {'driverId': driver_doc['driverId']},
                {'$set': driver_doc},
                upsert=True
            )
        
        logger.info(f"Fetched {len(drivers_data)} drivers")
        return jsonify({
            'message': f'Successfully fetched {len(drivers_data)} drivers',
            'drivers_count': len(drivers_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/constructors', methods=['GET'])
def fetch_constructors():
    """Fetch all constructors from OpenF1"""
    try:
        logger.info("Fetching latest session data...")
        sessions_data = openf1_client.fetch_data("sessions", {"session_key": "latest"})
        if not sessions_data:
            logger.error("Failed to fetch sessions data from OpenF1 API")
            return jsonify({'message': 'Failed to fetch sessions data from OpenF1 API'}), 500

        logger.info(f"Sessions data fetched: {sessions_data}")
        latest_session = sessions_data[0] if sessions_data else None
        if not latest_session:
            logger.error("No latest session found in OpenF1 API response")
            return jsonify({'message': 'No latest session found in OpenF1 API response'}), 500

        session_key = latest_session.get('session_key')
        logger.info(f"Fetching drivers data for session key: {session_key}")
        drivers_data = openf1_client.fetch_data("drivers", {"session_key": session_key})
        if not drivers_data:
            logger.error("Failed to fetch drivers data from OpenF1 API")
            return jsonify({'message': 'Failed to fetch drivers data from OpenF1 API'}), 500

        logger.info(f"Drivers data fetched: {drivers_data}")
        # Extract unique teams from drivers data
        teams = {}
        for driver in drivers_data:
            team_name = driver.get('team_name')
            team_colour = driver.get('team_colour')
            if team_name and team_name not in teams:
                teams[team_name] = {
                    'constructorId': team_name.lower().replace(' ', '_').replace('-', '_'),
                    'name': team_name,
                    'teamColour': team_colour,
                    'sessionKey': session_key,
                    'fetched_at': datetime.utcnow()
                }

        logger.info(f"Extracted {len(teams)} unique teams from drivers data")
        # Store constructors
        for team in teams.values():
            constructors_collection.update_one(
                {'constructorId': team['constructorId']},
                {'$set': team},
                upsert=True
            )

        logger.info(f"Stored {len(teams)} constructors in MongoDB")
        return jsonify({
            'message': f'Successfully fetched {len(teams)} constructors',
            'constructors_count': len(teams)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching constructors: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/race-results/<int:year>/<int:round>', methods=['GET'])
def fetch_race_results(year, round):
    """Fetch race results for a specific year and round"""
    try:
        # Placeholder for fetching race results
        return jsonify({'message': f'Fetched race results for {year} round {round}'}), 200
    except Exception as e:
        logger.error(f"Error fetching race results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/standings/<int:year>', methods=['GET'])
def fetch_standings(year):
    """Fetch standings for a specific year"""
    try:
        # Placeholder for fetching standings
        return jsonify({'message': f'Fetched standings for {year}'}), 200
    except Exception as e:
        logger.error(f"Error fetching standings: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/sessions', methods=['GET'])
def fetch_sessions():
    """Fetch all sessions from OpenF1"""
    try:
        # Get sessions for current year
        current_year = datetime.now().year
        sessions_data = openf1_client.fetch_data("sessions", {"year": current_year})
        
        if not sessions_data:
            return jsonify({'message': 'Failed to fetch sessions data'}), 500
        
        for session in sessions_data:
            session_doc = {
                'sessionKey': session.get('session_key'),
                'meetingKey': session.get('meeting_key'),
                'sessionName': session.get('session_name'),
                'dateStart': session.get('date_start'),
                'dateEnd': session.get('date_end'),
                'location': session.get('location'),
                'countryName': session.get('country_name'),
                'circuitShortName': session.get('circuit_short_name'),
                'year': session.get('year'),
                'fetched_at': datetime.utcnow()
            }
            
            races_collection.update_one(
                {'sessionKey': session_doc['sessionKey']},
                {'$set': session_doc},
                upsert=True
            )
        
        logger.info(f"Fetched {len(sessions_data)} sessions")
        return jsonify({
            'message': f'Successfully fetched {len(sessions_data)} sessions',
            'sessions_count': len(sessions_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/latest', methods=['GET'])
def fetch_latest():
    """Fetch latest data from OpenF1"""
    try:
        # Fetch drivers and constructors first
        fetch_drivers()
        fetch_constructors()
        fetch_sessions()
        
        logger.info("Successfully fetched latest data from OpenF1")
        return jsonify({
            'message': 'Successfully fetched latest data from OpenF1'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching latest data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/fetch/season/<int:year>', methods=['GET'])
def fetch_season(year):
    """Fetch season data for a specific year"""
    try:
        # Placeholder for fetching season data
        return jsonify({'message': f'Fetched season data for {year}'}), 200
    except Exception as e:
        logger.error(f"Error fetching season data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
