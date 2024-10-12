from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import Order, Event
from app import db
import boto3
from botocore.exceptions import ClientError

orders = Blueprint('orders', __name__)

@orders.route('/cart')
@login_required
def view_cart():
    # Implement cart view logic
    return render_template('cart.html')

@orders.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.json
    # Implement add to cart logic
    return jsonify({'message': 'Item added to cart'})

@orders.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.json
    # Implement remove from cart logic
    return jsonify({'message': 'Item removed from cart'})

@orders.route('/order', methods=['POST'])
@login_required
def place_order():
    data = request.json
    event_id = data.get('event_id')
    items = data.get('items')  # List of Amazon product ASINs

    try:
        # Initialize Amazon Product Advertising API client
        amazon_client = boto3.client(
            'paapi5',
            region_name='us-west-2',
            aws_access_key_id=current_app.config['AMAZON_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AMAZON_SECRET_KEY']
        )

        # Use Amazon Product Advertising API to place the order
        response = amazon_client.add_to_cart(
            PartnerTag=current_app.config['AMAZON_ASSOCIATE_TAG'],
            Items=[{'ASIN': item, 'Quantity': 1} for item in items]
        )

        cart_id = response['Cart']['CartId']
        purchase_url = response['Cart']['PurchaseURL']

        # Create a new order in our database
        new_order = Order(
            amazon_order_id=cart_id,
            status='Pending',
            user_id=current_user.id,
            event_id=event_id
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': 'Order placed successfully',
            'order_id': new_order.id,
            'purchase_url': purchase_url
        })

    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@orders.route('/orders')
@login_required
def get_orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders)

@orders.route('/orders/<int:order_id>')
@login_required
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Initialize Amazon Product Advertising API client
        amazon_client = boto3.client(
            'paapi5',
            region_name='us-west-2',
            aws_access_key_id=current_app.config['AMAZON_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AMAZON_SECRET_KEY']
        )

        # Fetch order details from Amazon API
        response = amazon_client.get_order(
            PartnerTag=current_app.config['AMAZON_ASSOCIATE_TAG'],
            AmazonOrderId=order.amazon_order_id
        )
        order_details = response['Order']
        return render_template('order_details.html', order=order, details=order_details)
    except ClientError as e:
        return jsonify({'error': str(e)}), 500
