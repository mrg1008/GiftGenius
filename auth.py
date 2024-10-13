import os
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from models import User, Referral, db
from datetime import datetime

auth = Blueprint('auth', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_google_oauth(app):
    google_bp = make_google_blueprint(
        client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
        scope=["profile", "email"],
        storage=SQLAlchemyStorage(User, db.session)
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    @oauth_authorized.connect_via(google_bp)
    def google_logged_in(blueprint, token):
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            google_info = resp.json()
            google_user_id = google_info["id"]

            with db.session.no_autoflush:
                user = User.query.filter_by(google_id=google_user_id).first()
                if not user:
                    user = User.query.filter_by(email=google_info["email"]).first()
                    if not user:
                        user = User(
                            name=google_info["name"],
                            email=google_info["email"],
                            google_id=google_user_id
                        )
                    else:
                        user.google_id = google_user_id
                    db.session.add(user)
                    db.session.commit()
                login_user(user)
            flash("Successfully signed in with Google.")
            return redirect(url_for("main.profile"))

        flash("Google sign-in failed.")
        return redirect(url_for("auth.login"))

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    logger.info("Signup attempt received")
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    referral_code = request.form.get('referral_code')

    logger.info(f"Signup details - Email: {email}, Name: {name}, Referral Code: {referral_code}")

    user = User.query.filter_by(email=email).first()

    if user:
        logger.info("Email address already exists")
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    try:
        new_user = User(email=email, name=name)
        new_user.set_password(password)
        new_user.generate_referral_code()

        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created with ID: {new_user.id}")

        if referral_code:
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                referral = Referral(referrer_id=referrer.id, referred_id=new_user.id, date=datetime.utcnow())
                referral.status = 'Completed'
                db.session.add(referral)
                
                referrer.referral_count += 1
                db.session.commit()
                
                logger.info(f"Referral recorded for user {new_user.id} by referrer {referrer.id}")
                flash('You have been referred successfully!')
            else:
                logger.info("Invalid referral code provided")
                flash('Invalid referral code. Continuing with registration.')

        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Error during user creation: {str(e)}")
        db.session.rollback()
        flash('An error occurred during registration. Please try again.')
        return redirect(url_for('auth.signup'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("main.profile"))

@auth.route('/referral')
@login_required
def referral():
    referrals = Referral.query.filter_by(referrer_id=current_user.id).all()
    return render_template('referral.html', referral_code=current_user.referral_code, referrals=referrals)
