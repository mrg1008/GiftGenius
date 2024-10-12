from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Event, Recipient
from app import db
from ebay_integration import EbayIntegration

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/recommendations/<int:event_id>')
@login_required
def get_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    recipient = Recipient.query.get(event.recipient_id)
    
    keywords = recipient.interests.split(',')
    min_price = str(int(event.budget_min))
    max_price = str(int(event.budget_max))

    ebay_gifts = search_ebay_gifts(keywords, min_price, max_price)

    all_gifts = ebay_gifts
    
    return render_template('recommendations.html', recommendations=all_gifts, event=event)

def search_ebay_gifts(keywords, min_price, max_price):
    ebay = EbayIntegration()
    gifts = ebay.search_gifts(keywords, min_price, max_price)
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

    gifts = search_ebay_gifts(keywords, min_price, max_price)

    return jsonify(gifts)
