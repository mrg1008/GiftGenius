from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, GroupGift, GroupGiftContribution, Event, User
from datetime import datetime

group_gifts = Blueprint('group_gifts', __name__)

@group_gifts.route('/group_gifts')
@login_required
def get_group_gifts():
    user_group_gifts = GroupGift.query.filter_by(creator_id=current_user.id).all()
    invited_group_gifts = GroupGift.query.join(GroupGiftContribution).filter(GroupGiftContribution.user_id == current_user.id).all()
    return render_template('group_gifts.html', created_gifts=user_group_gifts, invited_gifts=invited_group_gifts)

@group_gifts.route('/group_gifts/create', methods=['GET', 'POST'])
@login_required
def create_group_gift():
    if request.method == 'POST':
        new_group_gift = GroupGift(
            name=request.form['name'],
            description=request.form['description'],
            event_id=request.form['event_id'],
            creator_id=current_user.id,
            target_amount=float(request.form['target_amount']),
            status='Active'
        )
        db.session.add(new_group_gift)
        db.session.commit()
        flash('Group gift created successfully!', 'success')
        return redirect(url_for('group_gifts.get_group_gifts'))
    
    events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('create_group_gift.html', events=events)

@group_gifts.route('/group_gifts/<int:group_gift_id>')
@login_required
def get_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    contributions = GroupGiftContribution.query.filter_by(group_gift_id=group_gift_id).all()
    return render_template('group_gift_details.html', group_gift=group_gift, contributions=contributions)

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
    
    flash(f'You have successfully contributed ${amount:.2f} to the group gift!', 'success')
    return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))

@group_gifts.route('/group_gifts/<int:group_gift_id>/invite', methods=['POST'])
@login_required
def invite_to_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    if group_gift.creator_id != current_user.id:
        flash('You are not authorized to invite users to this group gift.', 'error')
        return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))
    
    email = request.form['email']
    invited_user = User.query.filter_by(email=email).first()
    if not invited_user:
        flash(f'No user found with email {email}', 'error')
        return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))
    
    if GroupGiftContribution.query.filter_by(group_gift_id=group_gift.id, user_id=invited_user.id).first():
        flash(f'{email} is already part of this group gift', 'info')
        return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))
    
    new_contribution = GroupGiftContribution(
        group_gift_id=group_gift.id,
        user_id=invited_user.id,
        amount=0,
        date=datetime.utcnow()
    )
    db.session.add(new_contribution)
    db.session.commit()
    
    flash(f'{email} has been invited to the group gift!', 'success')
    return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))

@group_gifts.route('/group_gifts/<int:group_gift_id>/update', methods=['POST'])
@login_required
def update_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    if group_gift.creator_id != current_user.id:
        flash('You are not authorized to update this group gift.', 'error')
        return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))
    
    group_gift.name = request.form['name']
    group_gift.description = request.form['description']
    group_gift.target_amount = float(request.form['target_amount'])
    
    db.session.commit()
    flash('Group gift updated successfully!', 'success')
    return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))

@group_gifts.route('/group_gifts/<int:group_gift_id>/delete', methods=['POST'])
@login_required
def delete_group_gift(group_gift_id):
    group_gift = GroupGift.query.get_or_404(group_gift_id)
    if group_gift.creator_id != current_user.id:
        flash('You are not authorized to delete this group gift.', 'error')
        return redirect(url_for('group_gifts.get_group_gift', group_gift_id=group_gift.id))
    
    db.session.delete(group_gift)
    db.session.commit()
    flash('Group gift deleted successfully!', 'success')
    return redirect(url_for('group_gifts.get_group_gifts'))
