import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'a-very-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    AMAZON_ACCESS_KEY = os.environ.get('AMAZON_ACCESS_KEY')
    AMAZON_SECRET_KEY = os.environ.get('AMAZON_SECRET_KEY')
    AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_ASSOCIATE_TAG')
    
    # Google OAuth config
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

    # Google Shopping API config
    GOOGLE_SHOPPING_API_KEY = os.environ.get('GOOGLE_SHOPPING_API_KEY')
    GOOGLE_SHOPPING_MERCHANT_ID = os.environ.get('GOOGLE_SHOPPING_MERCHANT_ID')

    # Remove Etsy and eBay configs as they are no longer needed
    # ETSY_API_KEY = os.environ.get('ETSY_API_KEY')
    # ETSY_OAUTH_SECRET = os.environ.get('ETSY_OAUTH_SECRET')
    # EBAY_APP_ID = os.environ.get('EBAY_APP_ID')
