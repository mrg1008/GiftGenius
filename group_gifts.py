from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import db, GroupGift, GroupGiftContribution, Event
from datetime import datetime

group_gifts = Blueprint('group_gifts', __name__)

@group_gifts.route('/group_gifts')
@login_required
def get_group_gifts():
    user_group_gifts = GroupGift.query.filter_by(creator_id=current_user.id).all()
    return render_template('group_gifts.html', group_gifts=user_group_gifts)

@group_gifts.route('/group_gifts/create', methods=['GET', 'POST'])
@login_required
def create_group_gift():
    if request.method == 'POST':
        data = request.form
        new_group_gift = GroupGift(
            name=data['name'],
            description=data['description'],
            event_id=data['event_id'],
            creator_id=current_user.id,
            target_amount=float(data['target_amount']),
            status='Active'
        )
        db.session.add(new_group_gift)
        db.session.commit()
        return redirect(url_for('group_gifts.get_group_gifts'))
    
    events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('create_group_gift.html', events=events)

@group_gifts.route('/group_gifts/<int:group_gift_id>')
@login_required
def get_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    return render_template('group_gift_details.html', group_gift=group_gift)

@group_gifts.route('/group_gifts/<int:group_gift_id>/contribute', methods=['POST'])
@login_required
def contribute_to_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    amount = float(request.form['amount'])
    
    contribution = GroupGiftContribution(
        group_gift_id=group_gift.id,
        user_id=current_user.id,
        amount=amount,
        date=datetime.utcnow()
    )
    
    group_gift.current_amount += amount
    if group_gift.current_amount >= group_gift.target_amount:
        group_gift.status = 'Completed'
    
    db.session.add(contribution)
    db.session.commit()
    
    return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))

@group_gifts.route('/group_gifts/<int:group_gift_id>/update', methods=['POST'])
@login_required
def update_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    if group_gift.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    group_gift.name = data['name']
    group_gift.description = data['description']
    group_gift.target_amount = float(data['target_amount'])
    
    db.session.commit()
    return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))

@group_gifts.route('/group_gifts/<int:group_gift_id>/delete', methods=['POST'])
@login_required
def delete_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    if group_gift.creator_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(group_gift)
    db.session.commit()
    return redirect(url_for('group_gifts.get_group_gifts'))
