import os
from etsy_python.api import EtsyAPI

class EtsyIntegration:
    def __init__(self):
        self.api = EtsyAPI(
            api_key=os.environ.get('ETSY_API_KEY'),
            oauth_secret=os.environ.get('ETSY_OAUTH_SECRET')
        )

    def search_gifts(self, keywords, min_price, max_price, limit=10):
        try:
            results = self.api.findAllListingActive(
                keywords=keywords,
                min_price=min_price,
                max_price=max_price,
                limit=limit
            )
            gifts = []
            for item in results:
                gift = {
                    'title': item['title'],
                    'price': item['price'],
                    'currency_code': item['currency_code'],
                    'url': item['url'],
                    'image_url': item['MainImage']['url_570xN']
                }
                gifts.append(gift)
            return gifts
        except Exception as e:
            print(f"Error searching Etsy gifts: {str(e)}")
            return []
