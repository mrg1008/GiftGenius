import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from events import events as events_blueprint
    app.register_blueprint(events_blueprint)

    from recommendations import recommendations as recommendations_blueprint
    app.register_blueprint(recommendations_blueprint)

    from orders import orders as orders_blueprint
    app.register_blueprint(orders_blueprint)

    from feedback import feedback as feedback_blueprint
    app.register_blueprint(feedback_blueprint)

    @app.route('/')
    def home():
        return render_template('home.html')

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
