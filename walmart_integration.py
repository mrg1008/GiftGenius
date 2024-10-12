import os
import logging
import requests
from cachetools import TTLCache, cached

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalmartIntegration:
    def __init__(self):
        self.client_id = os.environ.get('WALMART_CLIENT_ID')
        self.client_secret = os.environ.get('WALMART_CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("WALMART_CLIENT_ID or WALMART_CLIENT_SECRET environment variable is not set")
        self.base_url = "https://api.walmart.com/v3/items/search"
        logger.info(f"Initializing Walmart API with Client ID: {self.client_id[:5]}...{self.client_id[-5:]}")

    def get_access_token(self):
        auth_url = "https://marketplace.walmartapis.com/v3/token"
        headers = {
            "WM_SVC.NAME": "Walmart Marketplace",
            "WM_QOS.CORRELATION_ID": "test",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
        }
        try:
            response = requests.post(auth_url, headers=headers, data=data, auth=(self.client_id, self.client_secret))
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.RequestException as e:
            logger.error(f"Error getting Walmart access token: {str(e)}")
            return None

    @cached(cache=TTLCache(maxsize=100, ttl=3600))  # Cache results for 1 hour
    def search_gifts(self, keywords, min_price, max_price, limit=10):
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to obtain Walmart access token")
            return []

        headers = {
            "Authorization": f"Bearer {access_token}",
            "WM_SEC.ACCESS_TOKEN": access_token,
            "WM_CONSUMER.ID": self.client_id,
            "WM_CONSUMER.INTIMESTAMP": "1621535077000",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        params = {
            "query": " ".join(keywords),
            "numItems": limit,
            "minPrice": min_price,
            "maxPrice": max_price,
        }

        try:
            logger.info(f"Searching Walmart for gifts with keywords: {keywords}, price range: ${min_price} - ${max_price}")
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            gifts = []
            for item in data.get("items", []):
                gift = {
                    'title': item.get("name", "No Title"),
                    'price': item.get("salePrice", "N/A"),
                    'currency_code': "USD",
                    'url': item.get("productUrl", "#"),
                    'image_url': item.get("mediumImage", "#"),
                    'source': 'Walmart'
                }
                gifts.append(gift)
            
            logger.info(f"Found {len(gifts)} gifts on Walmart")
            return gifts
        except requests.RequestException as e:
            logger.error(f"Error searching Walmart gifts: {str(e)}")
            return []

    def get_gift_details(self, item_id):
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Failed to obtain Walmart access token")
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "WM_SEC.ACCESS_TOKEN": access_token,
            "WM_CONSUMER.ID": self.client_id,
            "WM_CONSUMER.INTIMESTAMP": "1621535077000",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        url = f"https://api.walmart.com/v3/items/{item_id}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            item = response.json()

            return {
                'title': item.get("name", "No Title"),
                'price': item.get("salePrice", "N/A"),
                'currency_code': "USD",
                'url': item.get("productUrl", "#"),
                'image_url': item.get("largeImage", "#"),
                'description': item.get("longDescription", "No description available"),
                'source': 'Walmart'
            }
        except requests.RequestException as e:
            logger.error(f"Error getting Walmart item details: {str(e)}")
            return None
