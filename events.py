from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Event, Recipient
from app import db

events = Blueprint('events', __name__)

@events.route('/events')
@login_required
def get_events():
    user_events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('events.html', events=user_events)

@events.route('/events', methods=['POST'])
@login_required
def create_event():
    data = request.json
    new_event = Event(
        type=data['type'],
        date=data['date'],
        budget_min=data['budget_min'],
        budget_max=data['budget_max'],
        recipient_id=data['recipient_id'],
        user_id=current_user.id
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event created successfully'}), 201

@events.route('/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    event.type = data.get('type', event.type)
    event.date = data.get('date', event.date)
    event.budget_min = data.get('budget_min', event.budget_min)
    event.budget_max = data.get('budget_max', event.budget_max)
    event.recipient_id = data.get('recipient_id', event.recipient_id)
    
    db.session.commit()
    return jsonify({'message': 'Event updated successfully'})

@events.route('/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})
