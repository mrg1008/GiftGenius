import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleShoppingIntegration:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.setup_credentials()

    def setup_credentials(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/content'])
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = Flow.from_client_secrets_file(
                    'client_secrets.json',
                    scopes=['https://www.googleapis.com/auth/content']
                )
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('content', 'v2.1', credentials=self.credentials)

    def search_gifts(self, keywords, min_price, max_price, limit=10):
        try:
            query = ' '.join(keywords)
            request = self.service.products().list(
                merchantId=Config.GOOGLE_SHOPPING_MERCHANT_ID,
                maxResults=limit,
                q=query
            )
            response = request.execute()

            gifts = []
            for item in response.get('resources', []):
                if min_price <= float(item['price']['value']) <= max_price:
                    gift = {
                        'title': item['title'],
                        'price': item['price']['value'],
                        'currency_code': item['price']['currency'],
                        'url': item['link'],
                        'image_url': item['imageLink'],
                        'source': 'Google Shopping'
                    }
                    gifts.append(gift)

            logger.info(f"Found {len(gifts)} gifts on Google Shopping")
            return gifts
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def get_gift_details(self, product_id):
        try:
            request = self.service.products().get(
                merchantId=Config.GOOGLE_SHOPPING_MERCHANT_ID,
                productId=product_id
            )
            item = request.execute()

            return {
                'title': item['title'],
                'price': item['price']['value'],
                'currency_code': item['price']['currency'],
                'url': item['link'],
                'image_url': item['imageLink'],
                'description': item.get('description', 'No description available'),
                'source': 'Google Shopping'
            }
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

# Example usage
if __name__ == "__main__":
    google_shopping = GoogleShoppingIntegration()
    # Test the integration
    results = google_shopping.search_gifts(["watch"], 50, 200, 5)
    print(results)
