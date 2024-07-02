import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from ratelimit import limits, sleep_and_retry
from cachetools import TTLCache, cached
import json
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure cache
cache = TTLCache(maxsize=100, ttl=3600)  # Cache for 1 hour

# Unset proxy settings if they exist
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# Rate limiting: 5 calls per minute
@sleep_and_retry
@limits(calls=5, period=60)
@cached(cache)
def fetch_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        time.sleep(5)  # Wait for 5 seconds before retrying
        return None

def scrape_events():
    url = os.getenv('SCRAPE_URL', "https://www.wembleystadium.com/events")
    html_content = fetch_url(url)

    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')

    events = []
    for item in soup.select('.fa-filter-content__item'):
        date_element = item.select_one('.col-xs-6.align-left.no-padding .small-text')
        date_str = date_element.text.strip() if date_element else 'Unknown Date'
        event_name = item.select_one('h2').text.strip() if item.select_one('h2') else 'Unknown Event'

        # Convert date string to ISO format
        try:
            date_obj = datetime.strptime(date_str, "%d %b %Y")
            iso_date = date_obj.isoformat() + "Z"  # Adding Z for UTC timezone
        except ValueError:
            iso_date = None
            logger.warning(f"Invalid date format for event: {event_name}")

        events.append({'name': event_name, 'date': iso_date})

    # Store the scraped data
    with open('./events_data.json', 'w') as f:
        json.dump(events, f)

    logger.info("Events scraped and stored successfully")

if __name__ == '__main__':
    scrape_events()
