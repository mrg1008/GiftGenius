from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Event, Recipient
from app import db
from google_shopping_integration import GoogleShoppingIntegration

# Note: We've chosen to integrate with Google Shopping instead of Etsy and eBay
# due to its wider product range and easier API integration. This decision
# was made to streamline our recommendation process and provide a more
# comprehensive selection of gifts to our users.

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/recommendations/<int:event_id>')
@login_required
def get_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    recipient = Recipient.query.get(event.recipient_id)
    
    keywords = recipient.interests.split(',')
    min_price = int(event.budget_min)
    max_price = int(event.budget_max)

    google_shopping_gifts = search_google_shopping_gifts(keywords, min_price, max_price)
    
    return render_template('recommendations.html', recommendations=google_shopping_gifts, event=event)

def search_google_shopping_gifts(keywords, min_price, max_price):
    google_shopping = GoogleShoppingIntegration()
    gifts = google_shopping.search_gifts(keywords, min_price, max_price)
    return gifts

@recommendations.route('/recommendations/<int:event_id>/filter', methods=['POST'])
@login_required
def filter_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    min_price = data.get('min_price')
    max_price = data.get('max_price')

    recipient = Recipient.query.get(event.recipient_id)
    keywords = recipient.interests.split(',')

    google_shopping_gifts = search_google_shopping_gifts(keywords, min_price, max_price)

    return jsonify(google_shopping_gifts)
