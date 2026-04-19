from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics

# Collections
drivers_collection = db.drivers
results_collection = db.results
standings_collection = db.standings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_document(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    return doc

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'driver-service'})

@app.route('/drivers', methods=['GET'])
def get_all_drivers():
    """Get all drivers"""
    try:
        limit = request.args.get('limit', 50, type=int)
        skip = request.args.get('skip', 0, type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = {}
        # OpenF1 data doesn't have is_active field, so we'll return all drivers
        
        drivers = list(drivers_collection.find(query).skip(skip).limit(limit))
        
        # Serialize documents
        drivers = [serialize_document(driver) for driver in drivers]
        
        total_count = drivers_collection.count_documents(query)
        
        logger.info(f"Retrieved {len(drivers)} drivers")
        return jsonify({
            'drivers': drivers,
            'total_count': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/<driver_id>', methods=['GET'])
def get_driver(driver_id):
    """Get specific driver by ID"""
    try:
        driver = drivers_collection.find_one({'driver_id': driver_id})
        
        if not driver:
            return jsonify({'message': 'Driver not found'}), 404
        
        driver = serialize_document(driver)
        
        logger.info(f"Retrieved driver: {driver_id}")
        return jsonify({'driver': driver}), 200
        
    except Exception as e:
        logger.error(f"Error getting driver {driver_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/search', methods=['GET'])
def search_drivers():
    """Search drivers by name or code"""
    try:
        query_param = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query_param:
            return jsonify({'message': 'Query parameter is required'}), 400
        
        # Create search query
        search_query = {
            '$or': [
                {'full_name': {'$regex': query_param, '$options': 'i'}},
                {'given_name': {'$regex': query_param, '$options': 'i'}},
                {'family_name': {'$regex': query_param, '$options': 'i'}},
                {'code': {'$regex': query_param, '$options': 'i'}},
                {'driver_id': {'$regex': query_param, '$options': 'i'}}
            ],
            'is_active': True
        }
        
        drivers = list(drivers_collection.find(search_query).limit(limit))
        drivers = [serialize_document(driver) for driver in drivers]
        
        logger.info(f"Found {len(drivers)} drivers matching '{query_param}'")
        return jsonify({
            'drivers': drivers,
            'query': query_param,
            'count': len(drivers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/top', methods=['GET'])
def get_top_drivers():
    """Get top drivers by points or wins"""
    try:
        limit = request.args.get('limit', 10, type=int)
        season = request.args.get('season', str(datetime.now().year))
        sort_by = request.args.get('sort_by', 'points')  # points or wins
        
        # Get current season standings
        standings = list(standings_collection.find({
            'season': season,
            'type': 'driverStandings'
        }).sort('position', 1).limit(limit))
        
        # Get driver details for each standing
        top_drivers = []
        for standing in standings:
            driver_id = standing['driver']['driver_id']
            driver = drivers_collection.find_one({'driver_id': driver_id})
            
            if driver:
                driver_info = serialize_document(driver)
                driver_info['points'] = standing.get('points', 0)
                driver_info['wins'] = standing.get('wins', 0)
                driver_info['position'] = standing.get('position', 0)
                top_drivers.append(driver_info)
        
        # Sort by requested criteria
        if sort_by == 'wins':
            top_drivers.sort(key=lambda x: x.get('wins', 0), reverse=True)
        else:
            top_drivers.sort(key=lambda x: x.get('points', 0), reverse=True)
        
        logger.info(f"Retrieved top {len(top_drivers)} drivers for {season}")
        return jsonify({
            'drivers': top_drivers,
            'season': season,
            'sort_by': sort_by
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting top drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/<driver_id>/results', methods=['GET'])
def get_driver_results(driver_id):
    """Get race results for a specific driver"""
    try:
        season = request.args.get('season')
        limit = request.args.get('limit', 50, type=int)
        
        query = {'driver.driver_id': driver_id}
        if season:
            query['season'] = season
        
        results = list(results_collection.find(query).sort('season', -1).sort('round', -1).limit(limit))
        results = [serialize_document(result) for result in results]
        
        logger.info(f"Retrieved {len(results)} results for driver {driver_id}")
        return jsonify({
            'driver_id': driver_id,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting driver results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/<driver_id>/stats', methods=['GET'])
def get_driver_stats(driver_id):
    """Get comprehensive stats for a specific driver"""
    try:
        season = request.args.get('season')
        
        # Get driver info
        driver = drivers_collection.find_one({'driver_id': driver_id})
        if not driver:
            return jsonify({'message': 'Driver not found'}), 404
        
        # Build query for results
        results_query = {'driver.driver_id': driver_id}
        if season:
            results_query['season'] = season
        
        # Get race results
        results = list(results_collection.find(results_query))
        
        # Calculate stats
        stats = {
            'driver_id': driver_id,
            'driver_info': serialize_document(driver),
            'total_races': len(results),
            'wins': 0,
            'podiums': 0,
            'points': 0,
            'fastest_laps': 0,
            'pole_positions': 0,
            'average_position': 0,
            'dnf_count': 0,
            'seasons': set(),
            'constructors': set()
        }
        
        if results:
            total_position = 0
            valid_positions = 0
            
            for result in results:
                # Count wins (position 1)
                if result.get('position') == 1:
                    stats['wins'] += 1
                
                # Count podiums (positions 1-3)
                if result.get('position') and result['position'] <= 3:
                    stats['podiums'] += 1
                
                # Sum points
                if result.get('points'):
                    stats['points'] += result['points']
                
                # Count fastest laps
                if result.get('fastest_lap', {}).get('rank') == 1:
                    stats['fastest_laps'] += 1
                
                # Track seasons and constructors
                if result.get('season'):
                    stats['seasons'].add(result['season'])
                
                if result.get('constructor', {}).get('name'):
                    stats['constructors'].add(result['constructor']['name'])
                
                # Calculate average position
                if result.get('position') and result['position'] > 0:
                    total_position += result['position']
                    valid_positions += 1
                
                # Count DNFs
                if result.get('status') and result['status'].lower() not in ['finished', '']:
                    stats['dnf_count'] += 1
            
            # Calculate average position
            if valid_positions > 0:
                stats['average_position'] = round(total_position / valid_positions, 2)
        
        # Convert sets to lists for JSON serialization
        stats['seasons'] = sorted(list(stats['seasons']), reverse=True)
        stats['constructors'] = list(stats['constructors'])
        
        logger.info(f"Calculated stats for driver {driver_id}")
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Error getting driver stats: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/<driver_id>/comparison/<other_driver_id>', methods=['GET'])
def compare_drivers(driver_id, other_driver_id):
    """Compare two drivers"""
    try:
        season = request.args.get('season')
        
        # Get both drivers
        driver1 = drivers_collection.find_one({'driver_id': driver_id})
        driver2 = drivers_collection.find_one({'driver_id': other_driver_id})
        
        if not driver1 or not driver2:
            return jsonify({'message': 'One or both drivers not found'}), 404
        
        # Get stats for both drivers
        stats1_response = get_driver_stats(driver_id)
        stats2_response = get_driver_stats(other_driver_id)
        
        if stats1_response[1] != 200 or stats2_response[1] != 200:
            return jsonify({'message': 'Error getting driver stats'}), 500
        
        comparison = {
            'driver1': {
                'info': serialize_document(driver1),
                'stats': stats1_response[0].json['stats']
            },
            'driver2': {
                'info': serialize_document(driver2),
                'stats': stats2_response[0].json['stats']
            }
        }
        
        logger.info(f"Compared drivers {driver_id} and {other_driver_id}")
        return jsonify({'comparison': comparison}), 200
        
    except Exception as e:
        logger.error(f"Error comparing drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/drivers/by-nationality/<nationality>', methods=['GET'])
def get_drivers_by_nationality(nationality):
    """Get drivers by nationality"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        drivers = list(drivers_collection.find({
            'nationality': {'$regex': nationality, '$options': 'i'},
            'is_active': True
        }).limit(limit))
        
        drivers = [serialize_document(driver) for driver in drivers]
        
        logger.info(f"Found {len(drivers)} drivers from {nationality}")
        return jsonify({
            'drivers': drivers,
            'nationality': nationality,
            'count': len(drivers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting drivers by nationality: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
