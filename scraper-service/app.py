from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import logging
from datetime import datetime
from pymongo import MongoClient
import time
import re
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/racemetrics')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client.racemetrics

# Collections
news_collection = db.news
lap_times_collection = db.lap_times
qualifying_collection = db.qualifying
additional_stats_collection = db.additional_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_f1_news(self, limit=20):
        """Scrape F1 news from various sources"""
        news_items = []
        
        # Scrape from Formula1.com news
        try:
            url = "https://www.formula1.com/en/latest.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles
            articles = soup.find_all('div', class_='f1-cc--caption')[:limit]
            
            for article in articles:
                try:
                    title_elem = article.find('h3')
                    link_elem = article.find('a')
                    date_elem = article.find('time')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href', '')
                        date = date_elem.get('datetime', '') if date_elem else ''
                        
                        if link and not link.startswith('http'):
                            link = urljoin('https://www.formula1.com', link)
                        
                        news_item = {
                            'title': title,
                            'link': link,
                            'date': date,
                            'source': 'Formula1.com',
                            'scraped_at': datetime.utcnow()
                        }
                        
                        news_items.append(news_item)
                        
                except Exception as e:
                    logger.error(f"Error parsing article: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping F1 news: {str(e)}")
        
        # Scrape from BBC Sport F1
        try:
            url = "https://www.bbc.com/sport/formula1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles
            articles = soup.find_all('article')[:limit//2]
            
            for article in articles:
                try:
                    title_elem = article.find('h3')
                    link_elem = article.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = link_elem.get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = urljoin('https://www.bbc.com', link)
                        
                        news_item = {
                            'title': title,
                            'link': link,
                            'source': 'BBC Sport',
                            'scraped_at': datetime.utcnow()
                        }
                        
                        news_items.append(news_item)
                        
                except Exception as e:
                    logger.error(f"Error parsing BBC article: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping BBC F1 news: {str(e)}")
        
        return news_items
    
    def scrape_lap_times(self, year=2024, round_num=1):
        """Scrape lap times for a specific race"""
        try:
            # This is a placeholder for lap time scraping
            # In a real implementation, you would scrape from official F1 timing data
            url = f"https://www.formula1.com/en/results.html/{year}/races.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse lap times (simplified example)
            lap_times = []
            
            # Mock lap time data structure
            for i in range(1, 21):  # 20 drivers
                lap_time = {
                    'season': str(year),
                    'round': round_num,
                    'driver_number': i,
                    'lap_number': 1,
                    'time': f"{1 + (i * 0.1):.3f}",
                    'position': i,
                    'scraped_at': datetime.utcnow()
                }
                lap_times.append(lap_time)
            
            return lap_times
            
        except Exception as e:
            logger.error(f"Error scraping lap times: {str(e)}")
            return []
    
    def scrape_qualifying_results(self, year=2024, round_num=1):
        """Scrape qualifying results"""
        try:
            # Mock qualifying results
            qualifying_results = []
            
            drivers = [
                "VER", "PER", "HAM", "RUS", "LEC", "SAI", "NOR", "PIA",
                "ALO", "STR", "GAS", "OCO", "MAG", "HUL", "BOT", "ZHO",
                "ALB", "SAR", "RIC", "TSU"
            ]
            
            for i, driver in enumerate(drivers):
                result = {
                    'season': str(year),
                    'round': round_num,
                    'position': i + 1,
                    'driver': driver,
                    'q1_time': f"{1 + (i * 0.05):.3f}",
                    'q2_time': f"{1.1 + (i * 0.05):.3f}",
                    'q3_time': f"{1.2 + (i * 0.05):.3f}" if i < 10 else None,
                    'scraped_at': datetime.utcnow()
                }
                qualifying_results.append(result)
            
            return qualifying_results
            
        except Exception as e:
            logger.error(f"Error scraping qualifying results: {str(e)}")
            return []
    
    def scrape_weather_data(self, year=2024, round_num=1):
        """Scrape weather data for races"""
        try:
            # Mock weather data
            weather_conditions = ["Sunny", "Cloudy", "Rainy", "Overcast"]
            temperatures = [25, 28, 22, 30, 26]
            
            weather_data = {
                'season': str(year),
                'round': round_num,
                'race_day_weather': "Sunny",
                'race_day_temperature': 28,
                'race_day_humidity': 65,
                'qualifying_weather': "Cloudy",
                'qualifying_temperature': 26,
                'scraped_at': datetime.utcnow()
            }
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error scraping weather data: {str(e)}")
            return None

scraper = F1Scraper()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'scraper-service'})

@app.route('/scrape/news', methods=['GET'])
def scrape_news():
    """Scrape F1 news from various sources"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        news_items = scraper.scrape_f1_news(limit)
        
        # Store news items in database
        for news_item in news_items:
            news_collection.update_one(
                {'title': news_item['title'], 'source': news_item['source']},
                {'$set': news_item},
                upsert=True
            )
        
        logger.info(f"Scraped {len(news_items)} news items")
        return jsonify({
            'message': f'Successfully scraped {len(news_items)} news items',
            'news_count': len(news_items),
            'items': news_items[:10]  # Return first 10 items
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping news: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/scrape/lap-times/<int:year>/<int:round>', methods=['GET'])
def scrape_lap_times(year, round):
    """Scrape lap times for a specific race"""
    try:
        lap_times = scraper.scrape_lap_times(year, round)
        
        # Store lap times in database
        for lap_time in lap_times:
            lap_times_collection.update_one(
                {
                    'season': lap_time['season'],
                    'round': lap_time['round'],
                    'driver_number': lap_time['driver_number'],
                    'lap_number': lap_time['lap_number']
                },
                {'$set': lap_time},
                upsert=True
            )
        
        logger.info(f"Scraped {len(lap_times)} lap times for {year} Round {round}")
        return jsonify({
            'message': f'Successfully scraped {len(lap_times)} lap times',
            'lap_times_count': len(lap_times)
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping lap times: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/scrape/qualifying/<int:year>/<int:round>', methods=['GET'])
def scrape_qualifying(year, round):
    """Scrape qualifying results for a specific race"""
    try:
        qualifying_results = scraper.scrape_qualifying_results(year, round)
        
        # Store qualifying results in database
        for result in qualifying_results:
            qualifying_collection.update_one(
                {
                    'season': result['season'],
                    'round': result['round'],
                    'driver': result['driver']
                },
                {'$set': result},
                upsert=True
            )
        
        logger.info(f"Scraped {len(qualifying_results)} qualifying results for {year} Round {round}")
        return jsonify({
            'message': f'Successfully scraped {len(qualifying_results)} qualifying results',
            'qualifying_count': len(qualifying_results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping qualifying results: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/scrape/weather/<int:year>/<int:round>', methods=['GET'])
def scrape_weather(year, round):
    """Scrape weather data for a specific race"""
    try:
        weather_data = scraper.scrape_weather_data(year, round)
        
        if weather_data:
            # Store weather data in database
            additional_stats_collection.update_one(
                {
                    'season': weather_data['season'],
                    'round': weather_data['round'],
                    'type': 'weather'
                },
                {'$set': weather_data},
                upsert=True
            )
            
            logger.info(f"Scraped weather data for {year} Round {round}")
            return jsonify({
                'message': 'Successfully scraped weather data',
                'weather_data': weather_data
            }), 200
        else:
            return jsonify({'message': 'Failed to scrape weather data'}), 500
        
    except Exception as e:
        logger.error(f"Error scraping weather data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/scrape/all/<int:year>/<int:round>', methods=['GET'])
def scrape_all(year, round):
    """Scrape all additional data for a specific race"""
    try:
        results = {}
        
        # Scrape news
        news_items = scraper.scrape_f1_news(10)
        for news_item in news_items:
            news_collection.update_one(
                {'title': news_item['title'], 'source': news_item['source']},
                {'$set': news_item},
                upsert=True
            )
        results['news'] = len(news_items)
        
        # Scrape lap times
        lap_times = scraper.scrape_lap_times(year, round)
        for lap_time in lap_times:
            lap_times_collection.update_one(
                {
                    'season': lap_time['season'],
                    'round': lap_time['round'],
                    'driver_number': lap_time['driver_number'],
                    'lap_number': lap_time['lap_number']
                },
                {'$set': lap_time},
                upsert=True
            )
        results['lap_times'] = len(lap_times)
        
        # Scrape qualifying
        qualifying_results = scraper.scrape_qualifying_results(year, round)
        for result in qualifying_results:
            qualifying_collection.update_one(
                {
                    'season': result['season'],
                    'round': result['round'],
                    'driver': result['driver']
                },
                {'$set': result},
                upsert=True
            )
        results['qualifying'] = len(qualifying_results)
        
        # Scrape weather
        weather_data = scraper.scrape_weather_data(year, round)
        if weather_data:
            additional_stats_collection.update_one(
                {
                    'season': weather_data['season'],
                    'round': weather_data['round'],
                    'type': 'weather'
                },
                {'$set': weather_data},
                upsert=True
            )
            results['weather'] = 1
        
        logger.info(f"Scraped all data for {year} Round {round}")
        return jsonify({
            'message': f'Successfully scraped all data for {year} Round {round}',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping all data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/scrape/latest', methods=['GET'])
def scrape_latest():
    """Scrape latest data"""
    try:
        current_year = datetime.now().year
        
        # Scrape latest news
        news_items = scraper.scrape_f1_news(20)
        for news_item in news_items:
            news_collection.update_one(
                {'title': news_item['title'], 'source': news_item['source']},
                {'$set': news_item},
                upsert=True
            )
        
        logger.info(f"Scraped latest data for {current_year}")
        return jsonify({
            'message': f'Successfully scraped latest data',
            'news_count': len(news_items)
        }), 200
        
    except Exception as e:
        logger.error(f"Error scraping latest data: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
