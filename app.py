
import os
from flask import Flask, send_from_directory, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
import ssl

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object('config.Config')

    CORS(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from auth import auth as auth_blueprint, init_google_oauth
    app.register_blueprint(auth_blueprint)
    init_google_oauth(app)

    from events import events as events_blueprint
    app.register_blueprint(events_blueprint)

    from recommendations import recommendations as recommendations_blueprint
    app.register_blueprint(recommendations_blueprint)

    from orders import orders as orders_blueprint
    app.register_blueprint(orders_blueprint)

    from feedback import feedback as feedback_blueprint
    app.register_blueprint(feedback_blueprint)

    from group_gifts import group_gifts as group_gifts_blueprint
    app.register_blueprint(group_gifts_blueprint)

    from analytics import analytics

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            analytics.track_page_view(current_user.id)

    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/api/hello')
    def hello():
        return jsonify(message="Hello from Flask!")

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()

if __name__ == "__main__":
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host="0.0.0.0", port=5000, ssl_context=ssl_context, debug=True)
