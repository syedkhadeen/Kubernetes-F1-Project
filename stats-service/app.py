from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import statistics

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics

# Collections
results_collection = db.clean_results
standings_collection = db.clean_standings
races_collection = db.clean_races
drivers_collection = db.clean_drivers
constructors_collection = db.clean_constructors

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

class F1Analytics:
    def __init__(self):
        pass
    
    def calculate_driver_consistency(self, driver_id, season=None):
        """Calculate driver consistency metrics"""
        query = {'driver.driver_id': driver_id}
        if season:
            query['season'] = season
        
        results = list(results_collection.find(query))
        
        if not results:
            return None
        
        positions = [r['position'] for r in results if r.get('position')]
        points = [r['points'] for r in results if r.get('points')]
        
        if not positions:
            return None
        
        consistency_metrics = {
            'total_races': len(results),
            'average_position': round(statistics.mean(positions), 2),
            'position_std_dev': round(statistics.stdev(positions) if len(positions) > 1 else 0, 2),
            'best_position': min(positions),
            'worst_position': max(positions),
            'total_points': sum(points),
            'average_points': round(statistics.mean(points) if points else 0, 2),
            'points_std_dev': round(statistics.stdev(points) if len(points) > 1 else 0, 2),
            'consistency_score': 0  # Lower std dev = higher consistency
        }
        
        # Calculate consistency score (0-100)
        if consistency_metrics['position_std_dev'] > 0:
            max_std = 20  # Maximum expected standard deviation
            consistency_metrics['consistency_score'] = max(0, 100 - (consistency_metrics['position_std_dev'] / max_std) * 100)
        else:
            consistency_metrics['consistency_score'] = 100
        
        return consistency_metrics
    
    def calculate_season_standings_trends(self, season):
        """Calculate standings trends throughout a season"""
        # Get standings after each race
        standings_data = list(standings_collection.find({
            'season': season,
            'type': {'$in': ['driverStandings', 'constructorStandings']}
        }).sort('round', 1))
        
        trends = {
            'season': season,
            'driver_trends': {},
            'constructor_trends': {},
            'total_races': 0
        }
        
        # Group by round and type
        for standing in standings_data:
            round_num = standing.get('round')
            standings_type = standing.get('type')
            
            if standings_type == 'driverStandings':
                driver_id = standing.get('driver', {}).get('driver_id')
                if driver_id:
                    if driver_id not in trends['driver_trends']:
                        trends['driver_trends'][driver_id] = {
                            'driver_name': f"{standing['driver'].get('given_name', '')} {standing['driver'].get('family_name', '')}".strip(),
                            'positions': [],
                            'points': []
                        }
                    trends['driver_trends'][driver_id]['positions'].append(standing.get('position', 0))
                    trends['driver_trends'][driver_id]['points'].append(standing.get('points', 0))
            
            elif standings_type == 'constructorStandings':
                constructor_id = standing.get('constructor', {}).get('constructor_id')
                if constructor_id:
                    if constructor_id not in trends['constructor_trends']:
                        trends['constructor_trends'][constructor_id] = {
                            'constructor_name': standing['constructor'].get('name', ''),
                            'positions': [],
                            'points': []
                        }
                    trends['constructor_trends'][constructor_id]['positions'].append(standing.get('position', 0))
                    trends['constructor_trends'][constructor_id]['points'].append(standing.get('points', 0))
            
            trends['total_races'] = max(trends['total_races'], int(round_num) if round_num else 0)
        
        return trends
    
    def calculate_race_pace_analysis(self, season, round_num):
        """Analyze race pace and performance"""
        results = list(results_collection.find({
            'season': season,
            'round': round_num
        }).sort('position', 1))
        
        if not results:
            return None
        
        pace_analysis = {
            'season': season,
            'round': round_num,
            'total_drivers': len(results),
            'pace_metrics': [],
            'gap_analysis': {}
        }
        
        # Calculate pace metrics for each driver
        for result in results:
            pace_metric = {
                'driver': result.get('driver', {}),
                'constructor': result.get('constructor', {}),
                'position': result.get('position'),
                'points': result.get('points', 0),
                'grid_position': result.get('grid'),
                'position_change': 0,
                'pace_score': 0
            }
            
            # Calculate position change from grid
            if result.get('grid') and result.get('position'):
                pace_metric['position_change'] = result['grid'] - result['position']
            
            # Calculate pace score (points + position change bonus)
            pace_metric['pace_score'] = result.get('points', 0) + (pace_metric['position_change'] * 0.5)
            
            pace_analysis['pace_metrics'].append(pace_metric)
        
        # Calculate gaps between positions
        for i in range(len(results) - 1):
            current = results[i]
            next_driver = results[i + 1]
            
            if current.get('time', {}).get('millis') and next_driver.get('time', {}).get('millis'):
                gap = next_driver['time']['millis'] - current['time']['millis']
                pace_analysis['gap_analysis'][f"P{i+1}_to_P{i+2}"] = {
                    'gap_millis': gap,
                    'gap_seconds': round(gap / 1000, 3)
                }
        
        return pace_analysis
    
    def calculate_championship_progressions(self, season):
        """Calculate championship progression analysis"""
        # Get final standings
        final_driver_standings = list(standings_collection.find({
            'season': season,
            'type': 'driverStandings'
        }).sort('round', -1).limit(1))
        
        final_constructor_standings = list(standings_collection.find({
            'season': season,
            'type': 'constructorStandings'
        }).sort('round', -1).limit(1))
        
        progressions = {
            'season': season,
            'driver_championship': [],
            'constructor_championship': [],
            'championship_decided_race': None,
            'tightest_battle': None
        }
        
        # Process driver championship
        if final_driver_standings:
            standings = final_driver_standings[0].get('standings', [])
            for standing in standings[:10]:  # Top 10
                driver_progression = {
                    'driver': standing.get('Driver', {}),
                    'final_position': standing.get('position'),
                    'final_points': standing.get('points'),
                    'wins': standing.get('wins'),
                    'podiums': standing.get('wins', 0) + sum(1 for s in standings if s.get('position') <= 3 and s.get('Driver', {}).get('driverId') == standing.get('Driver', {}).get('driverId'))
                }
                progressions['driver_championship'].append(driver_progression)
        
        # Process constructor championship
        if final_constructor_standings:
            standings = final_constructor_standings[0].get('standings', [])
            for standing in standings[:10]:  # Top 10
                constructor_progression = {
                    'constructor': standing.get('Constructors', [{}])[0],
                    'final_position': standing.get('position'),
                    'final_points': standing.get('points'),
                    'wins': standing.get('wins')
                }
                progressions['constructor_championship'].append(constructor_progression)
        
        return progressions

analytics = F1Analytics()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'stats-service'})

@app.route('/stats/fastest-lap', methods=['GET'])
def get_fastest_laps():
    """Get fastest lap statistics"""
    try:
        limit = request.args.get('limit', 10, type=int)
        season = request.args.get('season')
        
        query = {'fastest_lap.rank': 1}
        if season:
            query['season'] = season
        
        fastest_laps = list(results_collection.find(query).sort('season', -1).sort('round', -1).limit(limit))
        fastest_laps = [serialize_document(lap) for lap in fastest_laps]
        
        logger.info(f"Retrieved {len(fastest_laps)} fastest laps")
        return jsonify({
            'fastest_laps': fastest_laps,
            'count': len(fastest_laps)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting fastest laps: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/podium-frequency', methods=['GET'])
def get_podium_frequency():
    """Get podium frequency statistics"""
    try:
        limit = request.args.get('limit', 20, type=int)
        season = request.args.get('season')
        
        query = {'position': {'$lte': 3}}
        if season:
            query['season'] = season
        
        # Aggregate podium statistics
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$driver.driver_id',
                'driver_name': {'$first': '$driver.full_name'},
                'podiums': {'$sum': 1},
                'wins': {'$sum': {'$cond': [{'$eq': ['$position', 1]}, 1, 0]}},
                'second_places': {'$sum': {'$cond': [{'$eq': ['$position', 2]}, 1, 0]}},
                'third_places': {'$sum': {'$cond': [{'$eq': ['$position', 3]}, 1, 0]}}
            }},
            {'$sort': {'podiums': -1}},
            {'$limit': limit}
        ]
        
        podium_stats = list(results_collection.aggregate(pipeline))
        
        logger.info(f"Retrieved podium frequency for {len(podium_stats)} drivers")
        return jsonify({
            'podium_frequency': podium_stats,
            'count': len(podium_stats)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting podium frequency: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/average-speed', methods=['GET'])
def get_average_speed():
    """Get average speed statistics"""
    try:
        limit = request.args.get('limit', 20, type=int)
        season = request.args.get('season')
        
        query = {'fastest_lap.average_speed': {'$exists': True, '$ne': None}}
        if season:
            query['season'] = season
        
        # Aggregate speed statistics
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$driver.driver_id',
                'driver_name': {'$first': '$driver.full_name'},
                'average_speeds': {'$push': '$fastest_lap.average_speed'},
                'max_speed': {'$max': '$fastest_lap.average_speed'},
                'min_speed': {'$min': '$fastest_lap.average_speed'},
                'count': {'$sum': 1}
            }},
            {'$addFields': {
                'overall_average_speed': {'$avg': '$average_speeds'}
            }},
            {'$sort': {'overall_average_speed': -1}},
            {'$limit': limit}
        ]
        
        speed_stats = list(results_collection.aggregate(pipeline))
        
        logger.info(f"Retrieved speed statistics for {len(speed_stats)} drivers")
        return jsonify({
            'speed_statistics': speed_stats,
            'count': len(speed_stats)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting speed statistics: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/driver-consistency/<driver_id>', methods=['GET'])
def get_driver_consistency(driver_id):
    """Get driver consistency analysis"""
    try:
        season = request.args.get('season')
        
        consistency_metrics = analytics.calculate_driver_consistency(driver_id, season)
        
        if not consistency_metrics:
            return jsonify({'message': 'Driver not found or no data available'}), 404
        
        logger.info(f"Calculated consistency metrics for driver {driver_id}")
        return jsonify({
            'driver_id': driver_id,
            'consistency_metrics': consistency_metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating driver consistency: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/season-trends/<season>', methods=['GET'])
def get_season_trends(season):
    """Get season standings trends"""
    try:
        trends = analytics.calculate_season_standings_trends(season)
        
        logger.info(f"Calculated trends for {season} season")
        return jsonify({'trends': trends}), 200
        
    except Exception as e:
        logger.error(f"Error calculating season trends: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/race-pace/<season>/<round>', methods=['GET'])
def get_race_pace(season, round):
    """Get race pace analysis"""
    try:
        pace_analysis = analytics.calculate_race_pace_analysis(season, round)
        
        if not pace_analysis:
            return jsonify({'message': 'Race not found or no data available'}), 404
        
        logger.info(f"Calculated pace analysis for {season} Round {round}")
        return jsonify({'pace_analysis': pace_analysis}), 200
        
    except Exception as e:
        logger.error(f"Error calculating race pace: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/championship-progression/<season>', methods=['GET'])
def get_championship_progression(season):
    """Get championship progression analysis"""
    try:
        progressions = analytics.calculate_championship_progressions(season)
        
        logger.info(f"Calculated championship progression for {season}")
        return jsonify({'progression': progressions}), 200
        
    except Exception as e:
        logger.error(f"Error calculating championship progression: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/constructor-performance', methods=['GET'])
def get_constructor_performance():
    """Get constructor performance statistics"""
    try:
        limit = request.args.get('limit', 10, type=int)
        season = request.args.get('season')
        
        query = {}
        if season:
            query['season'] = season
        
        # Aggregate constructor performance
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$constructor.constructor_id',
                'constructor_name': {'$first': '$constructor.name'},
                'total_races': {'$sum': 1},
                'wins': {'$sum': {'$cond': [{'$eq': ['$position', 1]}, 1, 0]}},
                'podiums': {'$sum': {'$cond': [{'$lte': ['$position', 3]}, 1, 0]}},
                'points': {'$sum': '$points'},
                'fastest_laps': {'$sum': {'$cond': [{'$eq': ['$fastest_lap.rank', 1]}, 1, 0]}},
                'average_position': {'$avg': '$position'},
                'dnf_count': {'$sum': {'$cond': [{'$ne': ['$status', 'Finished']}, 1, 0]}}
            }},
            {'$addFields': {
                'win_percentage': {'$multiply': [{'$divide': ['$wins', '$total_races']}, 100]},
                'podium_percentage': {'$multiply': [{'$divide': ['$podiums', '$total_races']}, 100]},
                'reliability_score': {'$multiply': [{'$divide': [{'$subtract': ['$total_races', '$dnf_count']}, '$total_races']}, 100]}
            }},
            {'$sort': {'points': -1}},
            {'$limit': limit}
        ]
        
        constructor_performance = list(results_collection.aggregate(pipeline))
        
        logger.info(f"Retrieved performance statistics for {len(constructor_performance)} constructors")
        return jsonify({
            'constructor_performance': constructor_performance,
            'count': len(constructor_performance)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting constructor performance: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/stats/driver-form/<driver_id>', methods=['GET'])
def get_driver_form(driver_id):
    """Get driver form analysis (recent performance)"""
    try:
        races_back = request.args.get('races_back', 5, type=int)
        
        # Get recent results for the driver
        recent_results = list(results_collection.find({
            'driver.driver_id': driver_id
        }).sort('season', -1).sort('round', -1).limit(races_back))
        
        if not recent_results:
            return jsonify({'message': 'Driver not found or no recent results'}), 404
        
        # Calculate form metrics
        form_analysis = {
            'driver_id': driver_id,
            'driver_name': recent_results[0].get('driver', {}).get('full_name', ''),
            'races_analyzed': len(recent_results),
            'recent_results': [serialize_document(r) for r in recent_results],
            'form_metrics': {
                'average_position': 0,
                'total_points': 0,
                'podiums': 0,
                'wins': 0,
                'form_trend': 'stable',  # improving, declining, stable
                'form_score': 0  # 0-100
            }
        }
        
        if recent_results:
            positions = [r['position'] for r in recent_results if r.get('position')]
            points = [r['points'] for r in recent_results if r.get('points')]
            
            if positions:
                form_analysis['form_metrics']['average_position'] = round(statistics.mean(positions), 2)
                form_analysis['form_metrics']['total_points'] = sum(points)
                form_analysis['form_metrics']['podiums'] = len([p for p in positions if p <= 3])
                form_analysis['form_metrics']['wins'] = len([p for p in positions if p == 1])
                
                # Calculate form trend (comparing first half vs second half)
                if len(positions) >= 4:
                    first_half = positions[:len(positions)//2]
                    second_half = positions[len(positions)//2:]
                    
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    if second_avg < first_avg:
                        form_analysis['form_metrics']['form_trend'] = 'improving'
                    elif second_avg > first_avg:
                        form_analysis['form_metrics']['form_trend'] = 'declining'
                
                # Calculate form score (0-100)
                # Based on recent positions and points
                position_score = max(0, 100 - (form_analysis['form_metrics']['average_position'] - 1) * 5)
                points_score = min(100, form_analysis['form_metrics']['total_points'] * 5)
                form_analysis['form_metrics']['form_score'] = round((position_score + points_score) / 2, 1)
        
        logger.info(f"Calculated form analysis for driver {driver_id}")
        return jsonify({'form_analysis': form_analysis}), 200
        
    except Exception as e:
        logger.error(f"Error calculating driver form: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
