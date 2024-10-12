from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Feedback, Order
from app import db

feedback = Blueprint('feedback', __name__)

@feedback.route('/feedback/<int:order_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        data = request.json
        new_feedback = Feedback(
            rating=data['rating'],
            comment=data.get('comment', ''),
            order_id=order_id
        )
        db.session.add(new_feedback)
        db.session.commit()
        return jsonify({'message': 'Feedback submitted successfully'})
    
    return render_template('feedback.html', order=order)

@feedback.route('/feedback', methods=['GET'])
@login_required
def get_user_feedback():
    user_feedback = Feedback.query.join(Order).filter(Order.user_id == current_user.id).all()
    return render_template('user_feedback.html', feedback=user_feedback)
