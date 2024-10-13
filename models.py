from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(64), nullable=False)
    google_id = db.Column(db.String(64), unique=True, nullable=True)
    referral_code = db.Column(db.String(10), unique=True)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_referral_code(self):
        characters = string.ascii_letters + string.digits
        code = ''.join(random.choice(characters) for _ in range(10))
        while User.query.filter_by(referral_code=code).first():
            code = ''.join(random.choice(characters) for _ in range(10))
        self.referral_code = code

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    interests = db.Column(db.String(256))
    relationship = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('recipients', lazy=True))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)
    budget_min = db.Column(db.Float)
    budget_max = db.Column(db.Float)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    recipient = db.relationship('Recipient', backref=db.backref('events', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amazon_order_id = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('orders', lazy=True))
    gift_wrapping = db.Column(db.Boolean, default=False)
    personalization = db.Column(db.String(256))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', backref=db.backref('feedback', lazy=True))

class GroupGift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('group_gifts', lazy=True))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('created_group_gifts', lazy=True))
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(64), default='Active')

class GroupGiftContribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_gift_id = db.Column(db.Integer, db.ForeignKey('group_gift.id'), nullable=False)
    group_gift = db.relationship('GroupGift', backref=db.backref('contributions', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('group_gift_contributions', lazy=True))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(64), default='Pending')  # Pending, Completed, Rewarded

    referrer = db.relationship('User', foreign_keys=[referrer_id], backref=db.backref('referrals_made', lazy=True))
    referred = db.relationship('User', foreign_keys=[referred_id], backref=db.backref('referral', uselist=False))
