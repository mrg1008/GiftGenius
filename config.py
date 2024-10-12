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
