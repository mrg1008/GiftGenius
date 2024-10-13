import unittest
from app import create_app, db
from models import User, Referral
from flask_login import login_user
from datetime import datetime

class TestReferral(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_with_referral(self):
        # Create a referrer
        referrer = User(email='referrer@example.com', name='Referrer')
        referrer.set_password('password')
        referrer.generate_referral_code()
        db.session.add(referrer)
        db.session.commit()

        # Signup a new user with the referral code
        response = self.client.post('/signup', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'password',
            'referral_code': referrer.referral_code
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Check if the new user was created
        new_user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)

        # Check if the referral was recorded
        referral = Referral.query.filter_by(referrer_id=referrer.id, referred_id=new_user.id).first()
        self.assertIsNotNone(referral)
        self.assertEqual(referral.status, 'Completed')

        # Check if the referrer's count was incremented
        self.assertEqual(referrer.referral_count, 1)

    def test_referral_code_generation(self):
        user = User(email='test@example.com', name='Test User')
        user.set_password('password')
        user.generate_referral_code()
        
        self.assertIsNotNone(user.referral_code)
        self.assertEqual(len(user.referral_code), 10)

if __name__ == '__main__':
    unittest.main()
