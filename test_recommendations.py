import unittest
from app import create_app, db
from models import User, Recipient, Event, Order, Feedback
from flask_login import login_user
from datetime import datetime
from flask import url_for
from unittest.mock import patch

class TestRecommendations(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SERVER_NAME'] = 'localhost:5000'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test data
        with self.app.app_context():
            user = User(email='test@example.com', name='Test User')
            user.set_password('password')
            db.session.add(user)

            recipient = Recipient(name='Test Recipient', age_group='adult', interests='books,music', user=user)
            db.session.add(recipient)

            event = Event(type='birthday', date=datetime(2024, 12, 25), budget_min=50, budget_max=200, recipient=recipient, user=user)
            db.session.add(event)

            order = Order(amazon_order_id='123456', status='completed', user=user, event=event)
            db.session.add(order)

            feedback = Feedback(rating=4, comment='Great gift!', order=order)
            db.session.add(feedback)

            db.session.commit()

            self.user_id = user.id
            self.event_id = event.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        user = User.query.get(self.user_id)
        with self.app.test_request_context():
            login_user(user)

    @patch('recommendations.GoogleShoppingIntegration')
    def test_get_recommendations(self, mock_google_shopping):
        mock_google_shopping.return_value.search_gifts.return_value = [
            {
                'title': 'Mock Gift 1',
                'price': '75.00',
                'currency_code': 'USD',
                'url': 'https://example.com/gift1',
                'image_url': 'https://example.com/image1.jpg',
                'source': 'Google Shopping'
            }
        ]

        self.login()
        with self.app.test_request_context():
            response = self.client.get(url_for('recommendations.get_recommendations', event_id=self.event_id))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Gift Recommendations', response.data)
            self.assertIn(b'Mock Gift 1', response.data)

    @patch('recommendations.GoogleShoppingIntegration')
    def test_filter_recommendations(self, mock_google_shopping):
        mock_google_shopping.return_value.search_gifts.return_value = [
            {
                'title': 'Mock Gift 2',
                'price': '100.00',
                'currency_code': 'USD',
                'url': 'https://example.com/gift2',
                'image_url': 'https://example.com/image2.jpg',
                'source': 'Google Shopping'
            }
        ]

        self.login()
        with self.app.test_request_context():
            data = {
                'min_price': 75,
                'max_price': 150
            }
            response = self.client.post(url_for('recommendations.filter_recommendations', event_id=self.event_id), json=data)
            self.assertEqual(response.status_code, 200)
            recommendations = response.get_json()
            self.assertIsInstance(recommendations, list)
            self.assertEqual(len(recommendations), 1)
            self.assertEqual(recommendations[0]['title'], 'Mock Gift 2')
            self.assertEqual(float(recommendations[0]['price']), 100.00)

if __name__ == '__main__':
    unittest.main()
