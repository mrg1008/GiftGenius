import os
from ebaysdk.finding import Connection as Finding

class EbayIntegration:
    def __init__(self):
        self.api = Finding(appid=os.environ.get('EBAY_APP_ID'), config_file=None)

    def search_gifts(self, keywords, min_price, max_price, limit=10):
        try:
            response = self.api.execute('findItemsAdvanced', {
                'keywords': ' '.join(keywords),
                'itemFilter': [
                    {'name': 'MinPrice', 'value': min_price},
                    {'name': 'MaxPrice', 'value': max_price}
                ],
                'paginationInput': {
                    'entriesPerPage': limit
                },
                'sortOrder': 'BestMatch'
            })
            gifts = []
            for item in response.reply.searchResult.item:
                gift = {
                    'title': item.title,
                    'price': item.sellingStatus.currentPrice.value,
                    'currency_code': item.sellingStatus.currentPrice._currencyId,
                    'url': item.viewItemURL,
                    'image_url': item.galleryURL,
                    'source': 'eBay'
                }
                gifts.append(gift)
            return gifts
        except Exception as e:
            print(f"Error searching eBay gifts: {str(e)}")
            return []
