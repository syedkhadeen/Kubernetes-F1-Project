from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from pymongo import MongoClient
from functools import wraps
import logging

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET')
if not app.config['SECRET_KEY']:
    raise ValueError("JWT_SECRET environment variable is required")
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics
users_collection = db.users

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users_collection.find_one({'username': data['username']})
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth-service'})

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'message': 'Username, password, and email are required!'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'username': data['username']}):
            return jsonify({'message': 'Username already exists!'}), 400
        
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'message': 'Email already exists!'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(data['password'])
        
        # Create user document
        user_doc = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow(),
            'is_active': True,
            'role': 'user'
        }
        
        # Insert user
        result = users_collection.insert_one(user_doc)
        
        if result.inserted_id:
            logger.info(f"User registered: {data['username']}")
            return jsonify({'message': 'User registered successfully!'}), 201
        else:
            return jsonify({'message': 'Failed to register user!'}), 500
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Internal server error!'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required!'}), 400
        
        # Find user
        user = users_collection.find_one({'username': data['username']})
        
        if not user:
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        # Check password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        if not user.get('is_active', True):
            return jsonify({'message': 'Account is deactivated!'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'username': user['username'],
            'user_id': str(user['_id']),
            'role': user.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        logger.info(f"User logged in: {data['username']}")
        return jsonify({
            'token': token,
            'user': {
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error!'}), 500

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    return jsonify({
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user.get('role', 'user'),
        'created_at': current_user['created_at'].isoformat()
    }), 200

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided!'}), 400
        
        update_fields = {}
        
        if 'email' in data and data['email'] != current_user['email']:
            # Check if email is already taken
            if users_collection.find_one({'email': data['email'], '_id': {'$ne': current_user['_id']}}):
                return jsonify({'message': 'Email already exists!'}), 400
            update_fields['email'] = data['email']
        
        if 'password' in data and data['password']:
            update_fields['password'] = generate_password_hash(data['password'])
        
        if update_fields:
            update_fields['updated_at'] = datetime.datetime.utcnow()
            users_collection.update_one(
                {'_id': current_user['_id']},
                {'$set': update_fields}
            )
            logger.info(f"Profile updated for user: {current_user['username']}")
        
        return jsonify({'message': 'Profile updated successfully!'}), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'message': 'Internal server error!'}), 500

@app.route('/validate-token', methods=['POST'])
def validate_token():
    """Validate JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'valid': False, 'message': 'Token is missing!'}), 400
        
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
        
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        current_user = users_collection.find_one({'username': data['username']})
        
        if not current_user:
            return jsonify({'valid': False, 'message': 'User not found!'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'username': current_user['username'],
                'email': current_user['email'],
                'role': current_user.get('role', 'user')
            }
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Token is invalid!'}), 401
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'valid': False, 'message': 'Internal server error!'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
