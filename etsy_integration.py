import os
import logging
import requests
from cachetools import TTLCache, cached

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EtsyIntegration:
    def __init__(self):
        self.api_key = os.environ.get('ETSY_API_KEY')
        if not self.api_key:
            raise ValueError("ETSY_API_KEY environment variable is not set")
        logger.info(f"Initializing Etsy API with API Key: {self.api_key[:5]}...{self.api_key[-5:]}")
        self.base_url = "https://openapi.etsy.com/v3"

    @cached(cache=TTLCache(maxsize=100, ttl=3600))  # Cache results for 1 hour
    def search_gifts(self, keywords, min_price, max_price, limit=10):
        try:
            logger.info(f"Searching Etsy for gifts with keywords: {keywords}, price range: ${min_price} - ${max_price}")
            url = f"{self.base_url}/application/listings/active"
            params = {
                "keywords": ' '.join(keywords),
                "min_price": min_price,
                "max_price": max_price,
                "limit": limit,
                "sort_on": "created",
                "sort_order": "desc"
            }
            headers = {
                "x-api-key": self.api_key,
                "Accept": "application/json"
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            gifts = []
            for item in results:
                gift = {
                    'title': item.get('title', 'No Title'),
                    'price': item.get('price', {}).get('amount', 'N/A'),
                    'currency_code': item.get('price', {}).get('currency_code', 'USD'),
                    'url': f"https://www.etsy.com/listing/{item['listing_id']}",
                    'image_url': item.get('images', [{}])[0].get('url_570xN', '#'),
                    'source': 'Etsy'
                }
                gifts.append(gift)
            logger.info(f"Found {len(gifts)} gifts on Etsy")
            return gifts
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Etsy gifts: {str(e)}")
            return []

    def get_gift_details(self, listing_id):
        try:
            url = f"{self.base_url}/application/listings/{listing_id}"
            headers = {
                "x-api-key": self.api_key,
                "Accept": "application/json"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            item = response.json()
            return {
                'title': item.get('title', 'No Title'),
                'price': item.get('price', {}).get('amount', 'N/A'),
                'currency_code': item.get('price', {}).get('currency_code', 'USD'),
                'url': f"https://www.etsy.com/listing/{listing_id}",
                'image_url': item.get('images', [{}])[0].get('url_570xN', '#'),
                'description': item.get('description', 'No description available'),
                'source': 'Etsy'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Etsy item details: {str(e)}")
            return None
