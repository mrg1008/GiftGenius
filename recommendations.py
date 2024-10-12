from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Event, Recipient
from app import db
import boto3
from botocore.exceptions import ClientError

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/recommendations/<int:event_id>')
@login_required
def get_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    recipient = Recipient.query.get(event.recipient_id)
    
    # Prepare search parameters based on recipient's interests and event details
    keywords = recipient.interests.split(',')
    min_price = str(int(event.budget_min))
    max_price = str(int(event.budget_max))

    try:
        # Initialize Amazon Product Advertising API client
        amazon_client = boto3.client(
            'paapi5',
            region_name='us-west-2',
            aws_access_key_id=current_app.config['AMAZON_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AMAZON_SECRET_KEY']
        )

        response = amazon_client.search_items(
            PartnerTag=current_app.config['AMAZON_ASSOCIATE_TAG'],
            Keywords='+'.join(keywords),
            SearchIndex='All',
            Resources=['ItemInfo.Title', 'Offers.Listings.Price', 'Images.Primary.Medium'],
            MinPrice=min_price,
            MaxPrice=max_price,
            ItemCount=10
        )

        items = response['SearchResult']['Items']
        recommendations = []

        for item in items:
            recommendation = {
                'title': item['ItemInfo']['Title']['DisplayValue'],
                'price': item['Offers']['Listings'][0]['Price']['DisplayAmount'],
                'image_url': item['Images']['Primary']['Medium']['URL'],
                'product_url': item['DetailPageURL']
            }
            recommendations.append(recommendation)

        return render_template('recommendations.html', recommendations=recommendations, event=event)

    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@recommendations.route('/recommendations/<int:event_id>/filter', methods=['POST'])
@login_required
def filter_recommendations(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    category = data.get('category')
    min_price = data.get('min_price')
    max_price = data.get('max_price')

    # Implement filtering logic here
    # This is a placeholder and should be replaced with actual filtering logic
    filtered_recommendations = []

    return jsonify(filtered_recommendations)
