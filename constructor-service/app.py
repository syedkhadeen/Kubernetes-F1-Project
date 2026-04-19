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
constructors_collection = db.constructors
results_collection = db.results
standings_collection = db.standings
drivers_collection = db.drivers

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
    return jsonify({'status': 'healthy', 'service': 'constructor-service'})

@app.route('/constructors', methods=['GET'])
def get_all_constructors():
    """Get all constructors"""
    try:
        limit = request.args.get('limit', 50, type=int)
        skip = request.args.get('skip', 0, type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = {}
        # OpenF1 data doesn't have is_active field, so we'll return all constructors
        
        constructors = list(constructors_collection.find(query).skip(skip).limit(limit))
        
        # Serialize documents
        constructors = [serialize_document(constructor) for constructor in constructors]
        
        total_count = constructors_collection.count_documents(query)
        
        logger.info(f"Retrieved {len(constructors)} constructors")
        return jsonify({
            'constructors': constructors,
            'total_count': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructors: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/<constructor_id>', methods=['GET'])
def get_constructor(constructor_id):
    """Get specific constructor by ID"""
    try:
        constructor = constructors_collection.find_one({'constructor_id': constructor_id})
        
        if not constructor:
            return jsonify({'message': 'Constructor not found'}), 404
        
        constructor = serialize_document(constructor)
        
        logger.info(f"Retrieved constructor: {constructor_id}")
        return jsonify({'constructor': constructor}), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor {constructor_id}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/search', methods=['GET'])
def search_constructors():
    """Search constructors by name"""
    try:
        query_param = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query_param:
            return jsonify({'message': 'Query parameter is required'}), 400
        
        # Create search query
        search_query = {
            '$or': [
                {'name': {'$regex': query_param, '$options': 'i'}},
                {'constructor_id': {'$regex': query_param, '$options': 'i'}},
                {'nationality': {'$regex': query_param, '$options': 'i'}}
            ],
            'is_active': True
        }
        
        constructors = list(constructors_collection.find(search_query).limit(limit))
        constructors = [serialize_document(constructor) for constructor in constructors]
        
        logger.info(f"Found {len(constructors)} constructors matching '{query_param}'")
        return jsonify({
            'constructors': constructors,
            'query': query_param,
            'count': len(constructors)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching constructors: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/rankings', methods=['GET'])
def get_constructor_rankings():
    """Get constructor rankings/standings"""
    try:
        season = request.args.get('season', str(datetime.now().year))
        limit = request.args.get('limit', 20, type=int)
        
        # Get constructor standings
        standings = list(standings_collection.find({
            'season': season,
            'type': 'constructorStandings'
        }).sort('position', 1).limit(limit))
        
        # Get constructor details for each standing
        rankings = []
        for standing in standings:
            constructor_id = standing['constructor']['constructor_id']
            constructor = constructors_collection.find_one({'constructor_id': constructor_id})
            
            if constructor:
                constructor_info = serialize_document(constructor)
                constructor_info['points'] = standing.get('points', 0)
                constructor_info['wins'] = standing.get('wins', 0)
                constructor_info['position'] = standing.get('position', 0)
                rankings.append(constructor_info)
        
        logger.info(f"Retrieved constructor rankings for {season}")
        return jsonify({
            'rankings': rankings,
            'season': season,
            'count': len(rankings)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor rankings: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/<constructor_id>/results', methods=['GET'])
def get_constructor_results(constructor_id):
    """Get race results for a specific constructor"""
    try:
        season = request.args.get('season')
        limit = request.args.get('limit', 50, type=int)
        
        query = {'constructor.constructor_id': constructor_id}
        if season:
            query['season'] = season
        
        results = list(results_collection.find(query).sort('season', -1).sort('round', -1).limit(limit))
        results = [serialize_document(result) for result in results]
        
        logger.info(f"Retrieved {len(results)} results for constructor {constructor_id}")
        return jsonify({
            'constructor_id': constructor_id,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/<constructor_id>/drivers', methods=['GET'])
def get_constructor_drivers(constructor_id):
    """Get drivers who have driven for a specific constructor"""
    try:
        season = request.args.get('season')
        
        # Get unique drivers from results
        pipeline = [
            {'$match': {'constructor.constructor_id': constructor_id}},
            {'$group': {'_id': '$driver.driver_id'}},
            {'$limit': 50}
        ]
        
        if season:
            pipeline[0]['$match']['season'] = season
        
        driver_ids = [doc['_id'] for doc in results_collection.aggregate(pipeline)]
        
        # Get driver details
        drivers = list(drivers_collection.find({'driver_id': {'$in': driver_ids}}))
        drivers = [serialize_document(driver) for driver in drivers]
        
        logger.info(f"Found {len(drivers)} drivers for constructor {constructor_id}")
        return jsonify({
            'constructor_id': constructor_id,
            'drivers': drivers,
            'count': len(drivers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor drivers: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/<constructor_id>/stats', methods=['GET'])
def get_constructor_stats(constructor_id):
    """Get comprehensive stats for a specific constructor"""
    try:
        season = request.args.get('season')
        
        # Get constructor info
        constructor = constructors_collection.find_one({'constructor_id': constructor_id})
        if not constructor:
            return jsonify({'message': 'Constructor not found'}), 404
        
        # Build query for results
        results_query = {'constructor.constructor_id': constructor_id}
        if season:
            results_query['season'] = season
        
        # Get race results
        results = list(results_collection.find(results_query))
        
        # Calculate stats
        stats = {
            'constructor_id': constructor_id,
            'constructor_info': serialize_document(constructor),
            'total_races': len(results),
            'wins': 0,
            'podiums': 0,
            'points': 0,
            'fastest_laps': 0,
            'pole_positions': 0,
            'average_position': 0,
            'dnf_count': 0,
            'seasons': set(),
            'drivers': set(),
            'best_result': None,
            'worst_result': None
        }
        
        if results:
            total_position = 0
            valid_positions = 0
            positions = []
            
            for result in results:
                position = result.get('position')
                
                if position:
                    positions.append(position)
                    
                    # Count wins (position 1)
                    if position == 1:
                        stats['wins'] += 1
                    
                    # Count podiums (positions 1-3)
                    if position <= 3:
                        stats['podiums'] += 1
                    
                    # Sum points
                    if result.get('points'):
                        stats['points'] += result['points']
                    
                    # Calculate average position
                    total_position += position
                    valid_positions += 1
                
                # Count fastest laps
                if result.get('fastest_lap', {}).get('rank') == 1:
                    stats['fastest_laps'] += 1
                
                # Track seasons and drivers
                if result.get('season'):
                    stats['seasons'].add(result['season'])
                
                if result.get('driver', {}).get('full_name'):
                    stats['drivers'].add(result['driver']['full_name'])
                
                # Count DNFs
                if result.get('status') and result['status'].lower() not in ['finished', '']:
                    stats['dnf_count'] += 1
            
            # Calculate average position
            if valid_positions > 0:
                stats['average_position'] = round(total_position / valid_positions, 2)
            
            # Find best and worst results
            if positions:
                stats['best_result'] = min(positions)
                stats['worst_result'] = max(positions)
        
        # Convert sets to lists for JSON serialization
        stats['seasons'] = sorted(list(stats['seasons']), reverse=True)
        stats['drivers'] = list(stats['drivers'])
        
        logger.info(f"Calculated stats for constructor {constructor_id}")
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor stats: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/<constructor_id>/comparison/<other_constructor_id>', methods=['GET'])
def compare_constructors(constructor_id, other_constructor_id):
    """Compare two constructors"""
    try:
        season = request.args.get('season')
        
        # Get both constructors
        constructor1 = constructors_collection.find_one({'constructor_id': constructor_id})
        constructor2 = constructors_collection.find_one({'constructor_id': other_constructor_id})
        
        if not constructor1 or not constructor2:
            return jsonify({'message': 'One or both constructors not found'}), 404
        
        # Get stats for both constructors
        stats1_response = get_constructor_stats(constructor_id)
        stats2_response = get_constructor_stats(other_constructor_id)
        
        if stats1_response[1] != 200 or stats2_response[1] != 200:
            return jsonify({'message': 'Error getting constructor stats'}), 500
        
        comparison = {
            'constructor1': {
                'info': serialize_document(constructor1),
                'stats': stats1_response[0].json['stats']
            },
            'constructor2': {
                'info': serialize_document(constructor2),
                'stats': stats2_response[0].json['stats']
            }
        }
        
        logger.info(f"Compared constructors {constructor_id} and {other_constructor_id}")
        return jsonify({'comparison': comparison}), 200
        
    except Exception as e:
        logger.error(f"Error comparing constructors: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/by-nationality/<nationality>', methods=['GET'])
def get_constructors_by_nationality(nationality):
    """Get constructors by nationality"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        constructors = list(constructors_collection.find({
            'nationality': {'$regex': nationality, '$options': 'i'},
            'is_active': True
        }).limit(limit))
        
        constructors = [serialize_document(constructor) for constructor in constructors]
        
        logger.info(f"Found {len(constructors)} constructors from {nationality}")
        return jsonify({
            'constructors': constructors,
            'nationality': nationality,
            'count': len(constructors)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructors by nationality: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/constructors/performance', methods=['GET'])
def get_constructor_performance():
    """Get constructor performance analysis"""
    try:
        season = request.args.get('season', str(datetime.now().year))
        limit = request.args.get('limit', 10, type=int)
        
        # Get constructor standings
        standings = list(standings_collection.find({
            'season': season,
            'type': 'constructorStandings'
        }).sort('position', 1).limit(limit))
        
        performance_data = []
        
        for standing in standings:
            constructor_id = standing['constructor']['constructor_id']
            constructor = constructors_collection.find_one({'constructor_id': constructor_id})
            
            if constructor:
                # Get detailed stats
                stats_response = get_constructor_stats(constructor_id)
                if stats_response[1] == 200:
                    stats = stats_response[0].json['stats']
                    
                    performance = {
                        'constructor': serialize_document(constructor),
                        'position': standing.get('position', 0),
                        'points': standing.get('points', 0),
                        'wins': stats.get('wins', 0),
                        'podiums': stats.get('podiums', 0),
                        'fastest_laps': stats.get('fastest_laps', 0),
                        'average_position': stats.get('average_position', 0),
                        'total_races': stats.get('total_races', 0)
                    }
                    
                    performance_data.append(performance)
        
        logger.info(f"Retrieved performance data for {len(performance_data)} constructors")
        return jsonify({
            'performance': performance_data,
            'season': season,
            'count': len(performance_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor performance: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
