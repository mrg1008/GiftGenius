import unittest
from app import create_app, db
from models import User, Event, Recipient, Order
from datetime import datetime

class TestGiftOptions(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test user, recipient, and event
        self.user = User(email='test@example.com', name='Test User')
        self.user.set_password('password')
        self.recipient = Recipient(name='Test Recipient', age_group='adult', user=self.user)
        self.event = Event(type='birthday', date=datetime.utcnow(), budget_min=10, budget_max=100, recipient=self.recipient, user=self.user)
        db.session.add_all([self.user, self.recipient, self.event])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_order_with_gift_options(self):
        order = Order(
            amazon_order_id='TEST123',
            status='Pending',
            user_id=self.user.id,
            event_id=self.event.id,
            gift_wrapping=True,
            personalization='Happy Birthday!'
        )
        db.session.add(order)
        db.session.commit()

        retrieved_order = Order.query.filter_by(amazon_order_id='TEST123').first()
        self.assertIsNotNone(retrieved_order)
        self.assertTrue(retrieved_order.gift_wrapping)
        self.assertEqual(retrieved_order.personalization, 'Happy Birthday!')

    def test_update_order_gift_options(self):
        order = Order(
            amazon_order_id='TEST456',
            status='Pending',
            user_id=self.user.id,
            event_id=self.event.id,
            gift_wrapping=False,
            personalization=''
        )
        db.session.add(order)
        db.session.commit()

        order.gift_wrapping = True
        order.personalization = 'Merry Christmas!'
        db.session.commit()

        updated_order = Order.query.filter_by(amazon_order_id='TEST456').first()
        self.assertTrue(updated_order.gift_wrapping)
        self.assertEqual(updated_order.personalization, 'Merry Christmas!')

    def test_order_without_gift_options(self):
        order = Order(
            amazon_order_id='TEST789',
            status='Pending',
            user_id=self.user.id,
            event_id=self.event.id
        )
        db.session.add(order)
        db.session.commit()

        retrieved_order = Order.query.filter_by(amazon_order_id='TEST789').first()
        self.assertIsNotNone(retrieved_order)
        self.assertFalse(retrieved_order.gift_wrapping)
        self.assertIsNone(retrieved_order.personalization)

if __name__ == '__main__':
    unittest.main()
