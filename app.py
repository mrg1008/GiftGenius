import os
from flask import Flask, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder='frontend/build', static_url_path='')
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

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

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
    app.run(host="0.0.0.0", port=5000)
