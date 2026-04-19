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
races_collection = db.races
results_collection = db.results
standings_collection = db.standings
drivers_collection = db.drivers
constructors_collection = db.constructors

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
    return jsonify({'status': 'healthy', 'service': 'race-service'})

@app.route('/races', methods=['GET'])
def get_all_races():
    """Get all races"""
    try:
        limit = request.args.get('limit', 50, type=int)
        skip = request.args.get('skip', 0, type=int)
        season = request.args.get('season')
        circuit = request.args.get('circuit')
        
        query = {}
        if season:
            query['season'] = season
        if circuit:
            query['circuit.circuit_name'] = {'$regex': circuit, '$options': 'i'}
        
        races = list(races_collection.find(query).sort('season', -1).sort('round', -1).skip(skip).limit(limit))
        
        # Serialize documents
        races = [serialize_document(race) for race in races]
        
        total_count = races_collection.count_documents(query)
        
        logger.info(f"Retrieved {len(races)} races")
        return jsonify({
            'races': races,
            'total_count': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting races: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>', methods=['GET'])
def get_race(season, round):
    """Get specific race by season and round"""
    try:
        race = races_collection.find_one({'season': season, 'round': round})
        
        if not race:
            return jsonify({'message': 'Race not found'}), 404
        
        race = serialize_document(race)
        
        logger.info(f"Retrieved race: {season} Round {round}")
        return jsonify({'race': race}), 200
        
    except Exception as e:
        logger.error(f"Error getting race {season}/{round}: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/latest', methods=['GET'])
def get_latest_race():
    """Get the most recent race"""
    try:
        race = races_collection.find_one(sort=[('season', -1), ('round', -1)])
        
        if not race:
            return jsonify({'message': 'No races found'}), 404
        
        race = serialize_document(race)
        
        logger.info(f"Retrieved latest race: {race['season']} Round {race['round']}")
        return jsonify({'race': race}), 200
        
    except Exception as e:
        logger.error(f"Error getting latest race: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/results', methods=['GET'])
def get_race_results(season, round):
    """Get results for a specific race"""
    try:
        results = list(results_collection.find({
            'season': season,
            'round': round
        }).sort('position', 1))
        
        results = [serialize_document(result) for result in results]
        
        # Get race info
        race = races_collection.find_one({'season': season, 'round': round})
        race_info = serialize_document(race) if race else None
        
        logger.info(f"Retrieved {len(results)} results for {season} Round {round}")
        return jsonify({
            'race': race_info,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting race results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/podium', methods=['GET'])
def get_race_podium(season, round):
    """Get podium finishers for a specific race"""
    try:
        podium = list(results_collection.find({
            'season': season,
            'round': round,
            'position': {'$lte': 3}
        }).sort('position', 1))
        
        podium = [serialize_document(result) for result in podium]
        
        logger.info(f"Retrieved podium for {season} Round {round}")
        return jsonify({
            'podium': podium,
            'count': len(podium)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting race podium: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/fastest-lap', methods=['GET'])
def get_race_fastest_lap(season, round):
    """Get fastest lap for a specific race"""
    try:
        fastest_lap = results_collection.find_one({
            'season': season,
            'round': round,
            'fastest_lap.rank': 1
        })
        
        if not fastest_lap:
            return jsonify({'message': 'No fastest lap found'}), 404
        
        fastest_lap = serialize_document(fastest_lap)
        
        logger.info(f"Retrieved fastest lap for {season} Round {round}")
        return jsonify({'fastest_lap': fastest_lap}), 200
        
    except Exception as e:
        logger.error(f"Error getting fastest lap: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/dnf', methods=['GET'])
def get_race_dnf(season, round):
    """Get DNF (Did Not Finish) drivers for a specific race"""
    try:
        dnf_results = list(results_collection.find({
            'season': season,
            'round': round,
            'status': {'$nin': ['Finished', 'finished', '', None]}
        }))
        
        dnf_results = [serialize_document(result) for result in dnf_results]
        
        logger.info(f"Retrieved {len(dnf_results)} DNFs for {season} Round {round}")
        return jsonify({
            'dnf_results': dnf_results,
            'count': len(dnf_results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting DNF results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/stats', methods=['GET'])
def get_race_stats(season, round):
    """Get comprehensive stats for a specific race"""
    try:
        # Get race info
        race = races_collection.find_one({'season': season, 'round': round})
        if not race:
            return jsonify({'message': 'Race not found'}), 404
        
        # Get all results for the race
        results = list(results_collection.find({'season': season, 'round': round}))
        
        # Calculate stats
        stats = {
            'race_info': serialize_document(race),
            'total_drivers': len(results),
            'finishers': 0,
            'dnf_count': 0,
            'points_scored': 0,
            'fastest_lap': None,
            'pole_position': None,
            'constructor_results': {},
            'nationality_results': {},
            'average_race_time': None
        }
        
        total_time_millis = 0
        valid_times = 0
        
        for result in results:
            # Count finishers vs DNFs
            if result.get('status') and result['status'].lower() not in ['finished', '']:
                stats['dnf_count'] += 1
            else:
                stats['finishers'] += 1
            
            # Sum points
            if result.get('points'):
                stats['points_scored'] += result['points']
            
            # Find fastest lap
            if result.get('fastest_lap', {}).get('rank') == 1:
                stats['fastest_lap'] = serialize_document(result)
            
            # Find pole position (grid position 1)
            if result.get('grid') == 1:
                stats['pole_position'] = serialize_document(result)
            
            # Count constructor results
            constructor_name = result.get('constructor', {}).get('name', 'Unknown')
            if constructor_name not in stats['constructor_results']:
                stats['constructor_results'][constructor_name] = 0
            stats['constructor_results'][constructor_name] += 1
            
            # Count nationality results
            nationality = result.get('driver', {}).get('nationality', 'Unknown')
            if nationality not in stats['nationality_results']:
                stats['nationality_results'][nationality] = 0
            stats['nationality_results'][nationality] += 1
            
            # Calculate average race time
            if result.get('time', {}).get('millis'):
                total_time_millis += result['time']['millis']
                valid_times += 1
        
        # Calculate average race time
        if valid_times > 0:
            avg_time_millis = total_time_millis / valid_times
            stats['average_race_time'] = {
                'millis': avg_time_millis,
                'time': f"{int(avg_time_millis // 60000):02d}:{(int(avg_time_millis % 60000) // 1000):02d}.{int((avg_time_millis % 1000)):03d}"
            }
        
        logger.info(f"Calculated stats for {season} Round {round}")
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Error getting race stats: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>', methods=['GET'])
def get_season_races(season):
    """Get all races for a specific season"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        races = list(races_collection.find({'season': season}).sort('round', 1).limit(limit))
        races = [serialize_document(race) for race in races]
        
        logger.info(f"Retrieved {len(races)} races for {season}")
        return jsonify({
            'races': races,
            'season': season,
            'count': len(races)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting season races: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/circuits', methods=['GET'])
def get_circuits():
    """Get all unique circuits"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Get unique circuits
        pipeline = [
            {'$group': {
                '_id': '$circuit.circuit_id',
                'circuit_name': {'$first': '$circuit.circuit_name'},
                'country': {'$first': '$circuit.country'},
                'locality': {'$first': '$circuit.locality'},
                'lat': {'$first': '$circuit.lat'},
                'long': {'$first': '$circuit.long'},
                'race_count': {'$sum': 1}
            }},
            {'$sort': {'race_count': -1}},
            {'$limit': limit}
        ]
        
        circuits = list(races_collection.aggregate(pipeline))
        
        # Serialize documents
        circuits = [serialize_document(circuit) for circuit in circuits]
        
        logger.info(f"Retrieved {len(circuits)} circuits")
        return jsonify({
            'circuits': circuits,
            'count': len(circuits)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting circuits: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/<season>/<round>/comparison/<other_season>/<other_round>', methods=['GET'])
def compare_races(season, round, other_season, other_round):
    """Compare two races"""
    try:
        # Get both races
        race1 = races_collection.find_one({'season': season, 'round': round})
        race2 = races_collection.find_one({'season': other_season, 'round': other_round})
        
        if not race1 or not race2:
            return jsonify({'message': 'One or both races not found'}), 404
        
        # Get stats for both races
        stats1_response = get_race_stats(season, round)
        stats2_response = get_race_stats(other_season, other_round)
        
        if stats1_response[1] != 200 or stats2_response[1] != 200:
            return jsonify({'message': 'Error getting race stats'}), 500
        
        comparison = {
            'race1': {
                'info': serialize_document(race1),
                'stats': stats1_response[0].json['stats']
            },
            'race2': {
                'info': serialize_document(race2),
                'stats': stats2_response[0].json['stats']
            }
        }
        
        logger.info(f"Compared races {season}/{round} and {other_season}/{other_round}")
        return jsonify({'comparison': comparison}), 200
        
    except Exception as e:
        logger.error(f"Error comparing races: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/races/upcoming', methods=['GET'])
def get_upcoming_races():
    """Get upcoming races (future dates)"""
    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        races = list(races_collection.find({
            'date': {'$gte': current_date}
        }).sort('date', 1).limit(10))
        
        races = [serialize_document(race) for race in races]
        
        logger.info(f"Retrieved {len(races)} upcoming races")
        return jsonify({
            'upcoming_races': races,
            'count': len(races)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting upcoming races: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
