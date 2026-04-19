from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
from pymongo import MongoClient
import re

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics

# Source collections
drivers_collection = db.drivers
constructors_collection = db.constructors
races_collection = db.races
results_collection = db.results
standings_collection = db.standings
news_collection = db.news
lap_times_collection = db.lap_times
qualifying_collection = db.qualifying
additional_stats_collection = db.additional_stats

# Clean collections
clean_drivers_collection = db.clean_drivers
clean_constructors_collection = db.clean_constructors
clean_races_collection = db.clean_races
clean_results_collection = db.clean_results
clean_standings_collection = db.clean_standings
clean_news_collection = db.clean_news

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.cleaned_count = 0
    
    def clean_driver_data(self, driver_doc):
        """Clean and standardize driver data"""
        try:
            clean_driver = {
                'driver_id': driver_doc.get('driverId', ''),
                'permanent_number': driver_doc.get('permanentNumber'),
                'code': driver_doc.get('code', ''),
                'given_name': driver_doc.get('givenName', ''),
                'family_name': driver_doc.get('familyName', ''),
                'full_name': f"{driver_doc.get('givenName', '')} {driver_doc.get('familyName', '')}".strip(),
                'date_of_birth': driver_doc.get('dateOfBirth', ''),
                'nationality': driver_doc.get('nationality', ''),
                'url': driver_doc.get('url', ''),
                'is_active': True,
                'cleaned_at': datetime.utcnow(),
                'source': 'ergast_api'
            }
            
            # Clean and validate data
            if clean_driver['permanent_number']:
                try:
                    clean_driver['permanent_number'] = int(clean_driver['permanent_number'])
                except (ValueError, TypeError):
                    clean_driver['permanent_number'] = None
            
            # Validate nationality
            if clean_driver['nationality']:
                clean_driver['nationality'] = clean_driver['nationality'].strip().title()
            
            return clean_driver
            
        except Exception as e:
            logger.error(f"Error cleaning driver data: {str(e)}")
            return None
    
    def clean_constructor_data(self, constructor_doc):
        """Clean and standardize constructor data"""
        try:
            clean_constructor = {
                'constructor_id': constructor_doc.get('constructorId', ''),
                'name': constructor_doc.get('name', ''),
                'nationality': constructor_doc.get('nationality', ''),
                'url': constructor_doc.get('url', ''),
                'is_active': True,
                'cleaned_at': datetime.utcnow(),
                'source': 'ergast_api'
            }
            
            # Clean and validate data
            if clean_constructor['nationality']:
                clean_constructor['nationality'] = clean_constructor['nationality'].strip().title()
            
            return clean_constructor
            
        except Exception as e:
            logger.error(f"Error cleaning constructor data: {str(e)}")
            return None
    
    def clean_race_data(self, race_doc):
        """Clean and standardize race data"""
        try:
            circuit = race_doc.get('circuit', {})
            
            clean_race = {
                'season': race_doc.get('season', ''),
                'round': race_doc.get('round', ''),
                'race_name': race_doc.get('raceName', ''),
                'circuit': {
                    'circuit_id': circuit.get('circuitId', ''),
                    'circuit_name': circuit.get('circuitName', ''),
                    'country': circuit.get('Location', {}).get('country', ''),
                    'locality': circuit.get('Location', {}).get('locality', ''),
                    'lat': circuit.get('Location', {}).get('lat'),
                    'long': circuit.get('Location', {}).get('long')
                },
                'date': race_doc.get('date', ''),
                'time': race_doc.get('time', ''),
                'url': race_doc.get('url', ''),
                'cleaned_at': datetime.utcnow(),
                'source': 'ergast_api'
            }
            
            # Clean and validate data
            if clean_race['round']:
                try:
                    clean_race['round'] = int(clean_race['round'])
                except (ValueError, TypeError):
                    clean_race['round'] = None
            
            if clean_race['season']:
                try:
                    clean_race['season'] = int(clean_race['season'])
                except (ValueError, TypeError):
                    clean_race['season'] = None
            
            # Parse coordinates
            if clean_race['circuit']['lat']:
                try:
                    clean_race['circuit']['lat'] = float(clean_race['circuit']['lat'])
                except (ValueError, TypeError):
                    clean_race['circuit']['lat'] = None
            
            if clean_race['circuit']['long']:
                try:
                    clean_race['circuit']['long'] = float(clean_race['circuit']['long'])
                except (ValueError, TypeError):
                    clean_race['circuit']['long'] = None
            
            return clean_race
            
        except Exception as e:
            logger.error(f"Error cleaning race data: {str(e)}")
            return None
    
    def clean_result_data(self, result_doc):
        """Clean and standardize result data"""
        try:
            driver = result_doc.get('driver', {})
            constructor = result_doc.get('constructor', {})
            time_data = result_doc.get('time', {})
            fastest_lap = result_doc.get('fastestLap', {})
            
            clean_result = {
                'season': result_doc.get('season', ''),
                'round': result_doc.get('round', ''),
                'race_name': result_doc.get('raceName', ''),
                'position': result_doc.get('position'),
                'position_text': result_doc.get('positionText', ''),
                'points': result_doc.get('points'),
                'driver': {
                    'driver_id': driver.get('driverId', ''),
                    'permanent_number': driver.get('permanentNumber'),
                    'code': driver.get('code', ''),
                    'given_name': driver.get('givenName', ''),
                    'family_name': driver.get('familyName', ''),
                    'full_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip()
                },
                'constructor': {
                    'constructor_id': constructor.get('constructorId', ''),
                    'name': constructor.get('name', '')
                },
                'grid': result_doc.get('grid'),
                'laps': result_doc.get('laps'),
                'status': result_doc.get('status', ''),
                'time': {
                    'millis': time_data.get('millis'),
                    'time': time_data.get('time', '')
                },
                'fastest_lap': {
                    'rank': fastest_lap.get('rank'),
                    'lap': fastest_lap.get('lap'),
                    'time': fastest_lap.get('Time', {}).get('time', ''),
                    'average_speed': fastest_lap.get('AverageSpeed', {}).get('speed')
                },
                'cleaned_at': datetime.utcnow(),
                'source': 'ergast_api'
            }
            
            # Clean and validate numeric data
            for field in ['position', 'points', 'grid', 'laps']:
                if clean_result[field]:
                    try:
                        clean_result[field] = int(clean_result[field])
                    except (ValueError, TypeError):
                        clean_result[field] = None
            
            if clean_result['time']['millis']:
                try:
                    clean_result['time']['millis'] = int(clean_result['time']['millis'])
                except (ValueError, TypeError):
                    clean_result['time']['millis'] = None
            
            if clean_result['fastest_lap']['rank']:
                try:
                    clean_result['fastest_lap']['rank'] = int(clean_result['fastest_lap']['rank'])
                except (ValueError, TypeError):
                    clean_result['fastest_lap']['rank'] = None
            
            if clean_result['fastest_lap']['lap']:
                try:
                    clean_result['fastest_lap']['lap'] = int(clean_result['fastest_lap']['lap'])
                except (ValueError, TypeError):
                    clean_result['fastest_lap']['lap'] = None
            
            if clean_result['fastest_lap']['average_speed']:
                try:
                    clean_result['fastest_lap']['average_speed'] = float(clean_result['fastest_lap']['average_speed'])
                except (ValueError, TypeError):
                    clean_result['fastest_lap']['average_speed'] = None
            
            return clean_result
            
        except Exception as e:
            logger.error(f"Error cleaning result data: {str(e)}")
            return None
    
    def clean_standings_data(self, standings_doc):
        """Clean and standardize standings data"""
        try:
            standings = standings_doc.get('standings', [])
            clean_standings = []
            
            for standing in standings:
                driver = standing.get('Driver', {})
                constructor = standing.get('Constructors', [{}])[0]
                
                clean_standing = {
                    'season': standings_doc.get('season', ''),
                    'round': standings_doc.get('round', ''),
                    'type': standings_doc.get('type', ''),
                    'position': standing.get('position'),
                    'position_text': standing.get('positionText', ''),
                    'points': standing.get('points'),
                    'wins': standing.get('wins'),
                    'driver': {
                        'driver_id': driver.get('driverId', ''),
                        'permanent_number': driver.get('permanentNumber'),
                        'code': driver.get('code', ''),
                        'given_name': driver.get('givenName', ''),
                        'family_name': driver.get('familyName', ''),
                        'full_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip()
                    },
                    'constructor': {
                        'constructor_id': constructor.get('constructorId', ''),
                        'name': constructor.get('name', '')
                    },
                    'cleaned_at': datetime.utcnow(),
                    'source': 'ergast_api'
                }
                
                # Clean and validate numeric data
                for field in ['position', 'points', 'wins']:
                    if clean_standing[field]:
                        try:
                            clean_standing[field] = int(clean_standing[field])
                        except (ValueError, TypeError):
                            clean_standing[field] = None
                
                clean_standings.append(clean_standing)
            
            return clean_standings
            
        except Exception as e:
            logger.error(f"Error cleaning standings data: {str(e)}")
            return []
    
    def clean_news_data(self, news_doc):
        """Clean and standardize news data"""
        try:
            clean_news = {
                'title': news_doc.get('title', ''),
                'link': news_doc.get('link', ''),
                'date': news_doc.get('date', ''),
                'source': news_doc.get('source', ''),
                'scraped_at': news_doc.get('scraped_at'),
                'cleaned_at': datetime.utcnow()
            }
            
            # Clean title
            if clean_news['title']:
                clean_news['title'] = clean_news['title'].strip()
            
            # Clean source
            if clean_news['source']:
                clean_news['source'] = clean_news['source'].strip()
            
            return clean_news
            
        except Exception as e:
            logger.error(f"Error cleaning news data: {str(e)}")
            return None

data_cleaner = DataCleaner()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'data-cleaner-service'})

@app.route('/clean/drivers', methods=['POST'])
def clean_drivers():
    """Clean all driver data"""
    try:
        drivers = list(drivers_collection.find())
        cleaned_count = 0
        
        for driver in drivers:
            clean_driver = data_cleaner.clean_driver_data(driver)
            if clean_driver:
                clean_drivers_collection.update_one(
                    {'driver_id': clean_driver['driver_id']},
                    {'$set': clean_driver},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} drivers")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} drivers',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/constructors', methods=['POST'])
def clean_constructors():
    """Clean all constructor data"""
    try:
        constructors = list(constructors_collection.find())
        cleaned_count = 0
        
        for constructor in constructors:
            clean_constructor = data_cleaner.clean_constructor_data(constructor)
            if clean_constructor:
                clean_constructors_collection.update_one(
                    {'constructor_id': clean_constructor['constructor_id']},
                    {'$set': clean_constructor},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} constructors")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} constructors',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning constructors: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/races', methods=['POST'])
def clean_races():
    """Clean all race data"""
    try:
        races = list(races_collection.find())
        cleaned_count = 0
        
        for race in races:
            clean_race = data_cleaner.clean_race_data(race)
            if clean_race:
                clean_races_collection.update_one(
                    {'season': clean_race['season'], 'round': clean_race['round']},
                    {'$set': clean_race},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} races")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} races',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning races: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/results', methods=['POST'])
def clean_results():
    """Clean all result data"""
    try:
        results = list(results_collection.find())
        cleaned_count = 0
        
        for result in results:
            clean_result = data_cleaner.clean_result_data(result)
            if clean_result:
                clean_results_collection.update_one(
                    {
                        'season': clean_result['season'],
                        'round': clean_result['round'],
                        'driver.driver_id': clean_result['driver']['driver_id']
                    },
                    {'$set': clean_result},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} results")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} results',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/standings', methods=['POST'])
def clean_standings():
    """Clean all standings data"""
    try:
        standings_docs = list(standings_collection.find())
        cleaned_count = 0
        
        for standings_doc in standings_docs:
            clean_standings = data_cleaner.clean_standings_data(standings_doc)
            
            for clean_standing in clean_standings:
                clean_standings_collection.update_one(
                    {
                        'season': clean_standing['season'],
                        'round': clean_standing['round'],
                        'type': clean_standing['type'],
                        'driver.driver_id': clean_standing['driver']['driver_id']
                    },
                    {'$set': clean_standing},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} standings")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} standings',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning standings: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/news', methods=['POST'])
def clean_news():
    """Clean all news data"""
    try:
        news_items = list(news_collection.find())
        cleaned_count = 0
        
        for news_item in news_items:
            clean_news = data_cleaner.clean_news_data(news_item)
            if clean_news:
                clean_news_collection.update_one(
                    {'title': clean_news['title'], 'source': clean_news['source']},
                    {'$set': clean_news},
                    upsert=True
                )
                cleaned_count += 1
        
        logger.info(f"Cleaned {cleaned_count} news items")
        return jsonify({
            'message': f'Successfully cleaned {cleaned_count} news items',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning news: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/clean/all', methods=['POST'])
def clean_all():
    """Clean all data"""
    try:
        results = {}
        
        # Clean all data types
        clean_drivers()
        clean_constructors()
        clean_races()
        clean_results()
        clean_standings()
        clean_news()
        
        logger.info("Successfully cleaned all data")
        return jsonify({
            'message': 'Successfully cleaned all data',
            'status': 'completed'
        }), 200
        
    except Exception as e:
        logger.error(f"Error cleaning all data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
