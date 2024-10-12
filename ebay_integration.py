import os
import logging
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from cachetools import TTLCache, cached

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EbayIntegration:
    def __init__(self):
        self.app_id = os.environ.get('EBAY_APP_ID')
        if not self.app_id:
            raise ValueError("EBAY_APP_ID environment variable is not set")
        logger.info(f"Initializing eBay API with App ID: {self.app_id[:5]}...{self.app_id[-5:]}")
        try:
            self.api = Finding(appid=self.app_id, config_file=None, siteid="EBAY-US")
        except Exception as e:
            logger.error(f"Failed to initialize eBay API: {str(e)}")
            raise

    @cached(cache=TTLCache(maxsize=100, ttl=3600))  # Cache results for 1 hour
    def search_gifts(self, keywords, min_price, max_price, limit=10):
        try:
            logger.info(f"Searching eBay for gifts with keywords: {keywords}, price range: ${min_price} - ${max_price}")
            response = self.api.execute('findItemsAdvanced', {
                'keywords': ' '.join(keywords),
                'itemFilter': [
                    {'name': 'MinPrice', 'value': min_price},
                    {'name': 'MaxPrice', 'value': max_price},
                    {'name': 'ListingType', 'value': 'FixedPrice'},
                    {'name': 'Condition', 'value': 'New'}
                ],
                'paginationInput': {
                    'entriesPerPage': limit
                },
                'sortOrder': 'BestMatch'
            })
            
            gifts = []
            if isinstance(response, dict) and 'searchResult' in response.get('reply', {}):
                items = response['reply']['searchResult'].get('item', [])
                for item in items:
                    gift = {
                        'title': item.get('title', 'No Title'),
                        'price': item.get('sellingStatus', {}).get('currentPrice', {}).get('value', 'N/A'),
                        'currency_code': item.get('sellingStatus', {}).get('currentPrice', {}).get('_currencyId', 'USD'),
                        'url': item.get('viewItemURL', '#'),
                        'image_url': item.get('galleryURL', '#'),
                        'source': 'eBay'
                    }
                    gifts.append(gift)
                logger.info(f"Found {len(gifts)} gifts on eBay")
            else:
                logger.error("Unexpected response structure from eBay API")
            return gifts
        except ConnectionError as e:
            logger.error(f"eBay API ConnectionError: {str(e)}")
            if hasattr(e, 'response') and isinstance(e.response, dict):
                logger.error(f"Error details: {e.response}")
            if "Invalid Application" in str(e):
                logger.error("The eBay Application ID seems to be invalid. Please check your EBAY_APP_ID environment variable.")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching eBay gifts: {str(e)}")
            return []

    def get_gift_details(self, item_id):
        try:
            response = self.api.execute('GetSingleItem', {'ItemID': item_id})
            if isinstance(response, dict) and 'Item' in response.get('reply', {}):
                item = response['reply']['Item']
                return {
                    'title': item.get('Title', 'No Title'),
                    'price': item.get('CurrentPrice', {}).get('value', 'N/A'),
                    'currency_code': item.get('CurrentPrice', {}).get('_currencyId', 'USD'),
                    'url': item.get('ViewItemURLForNaturalSearch', '#'),
                    'image_url': item.get('PictureURL', [None])[0],
                    'description': item.get('Description', 'No description available'),
                    'condition': item.get('Condition', {}).get('ConditionDisplayName', 'N/A'),
                    'source': 'eBay'
                }
            else:
                logger.error("Unexpected response structure from eBay API for item details")
                return None
        except Exception as e:
            logger.error(f"Error getting eBay item details: {str(e)}")
            return None
