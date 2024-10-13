from flask import request, session
from models import db, User, Event, Recipient, Order, Feedback
from datetime import datetime
import json

class Analytics:
    @staticmethod
    def track_event(event_type, user_id, data=None):
        """
        Track a user event
        """
        event = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': json.dumps(data) if data else None
        }
        # In a production environment, we would send this to a data warehouse or analytics service
        print(f"Analytics Event: {event}")

    @staticmethod
    def track_page_view(user_id):
        """
        Track a page view
        """
        Analytics.track_event('page_view', user_id, {
            'url': request.path,
            'referrer': request.referrer
        })

    @staticmethod
    def track_recommendation_click(user_id, gift_id):
        """
        Track when a user clicks on a recommendation
        """
        Analytics.track_event('recommendation_click', user_id, {
            'gift_id': gift_id
        })

    @staticmethod
    def track_purchase(user_id, order_id):
        """
        Track a purchase
        """
        order = Order.query.get(order_id)
        if order:
            Analytics.track_event('purchase', user_id, {
                'order_id': order_id,
                'amount': str(order.amount),
                'items': [item.id for item in order.items]
            })

    @staticmethod
    def get_user_behavior_score(user_id):
        """
        Calculate a user behavior score based on their interactions
        """
        user = User.query.get(user_id)
        if not user:
            return 0

        score = 0
        
        # Score based on number of events created
        events_count = Event.query.filter_by(user_id=user_id).count()
        score += events_count * 10

        # Score based on number of recipients added
        recipients_count = Recipient.query.filter_by(user_id=user_id).count()
        score += recipients_count * 5

        # Score based on number of orders placed
        orders_count = Order.query.filter_by(user_id=user_id).count()
        score += orders_count * 20

        # Score based on feedback provided
        feedback_count = Feedback.query.join(Order).filter(Order.user_id == user_id).count()
        score += feedback_count * 15

        return score

    @staticmethod
    def get_popular_interests(limit=10):
        """
        Get the most popular interests among all recipients
        """
        recipients = Recipient.query.all()
        interests = {}
        for recipient in recipients:
            for interest in recipient.interests.split(','):
                interest = interest.strip().lower()
                if interest:
                    interests[interest] = interests.get(interest, 0) + 1
        
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        return [interest for interest, count in sorted_interests[:limit]]

analytics = Analytics()
