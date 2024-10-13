from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Event, Recipient, Feedback, Order
from app import db
from google_shopping_integration import GoogleShoppingIntegration
from ml_model import GiftRecommendationModel

recommendations = Blueprint('recommendations', __name__)
ml_model = GiftRecommendationModel()

@recommendations.route('/recommendations/<int:event_id>')
@login_required
def get_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    recipient = Recipient.query.get(event.recipient_id)
    
    keywords = recipient.interests.split(',') if recipient.interests else []
    min_price = float(event.budget_min)
    max_price = float(event.budget_max)

    google_shopping_gifts = search_google_shopping_gifts(keywords, min_price, max_price)
    
    # Get user feedback and generate recommendations using ML model
    user_feedback = get_user_feedback(current_user.id)
    user_interests = recipient.interests.split(',') if recipient.interests else []
    ml_recommendations = ml_model.generate_recommendations(google_shopping_gifts, user_feedback, user_interests, min_price, max_price)
    
    return render_template('recommendations.html', recommendations=ml_recommendations, event=event)

def search_google_shopping_gifts(keywords, min_price, max_price):
    google_shopping = GoogleShoppingIntegration()
    gifts = google_shopping.search_gifts(keywords, min_price, max_price)
    # Ensure all necessary attributes are present
    for gift in gifts:
        gift['id'] = gift.get('id', gift['url'])  # Use URL as ID if not present
        gift['description'] = gift.get('description', '')  # Empty string if no description
    return gifts

def get_user_feedback(user_id):
    user_orders = Order.query.filter_by(user_id=user_id).all()
    feedback_list = []
    for order in user_orders:
        feedback = Feedback.query.filter_by(order_id=order.id).first()
        if feedback:
            feedback_list.append({
                'gift_id': order.amazon_order_id,
                'rating': feedback.rating
            })
    return feedback_list

@recommendations.route('/recommendations/<int:event_id>/filter', methods=['POST'])
@login_required
def filter_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    min_price = float(data.get('min_price', event.budget_min))
    max_price = float(data.get('max_price', event.budget_max))

    recipient = Recipient.query.get(event.recipient_id)
    keywords = recipient.interests.split(',') if recipient.interests else []

    google_shopping_gifts = search_google_shopping_gifts(keywords, min_price, max_price)
    
    # Get user feedback and generate recommendations using ML model
    user_feedback = get_user_feedback(current_user.id)
    user_interests = recipient.interests.split(',') if recipient.interests else []
    ml_recommendations = ml_model.generate_recommendations(google_shopping_gifts, user_feedback, user_interests, min_price, max_price)

    return jsonify(ml_recommendations)
