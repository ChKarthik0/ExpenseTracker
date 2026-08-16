from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

load_dotenv()

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User
    from app.models.transaction import Transaction
    from app.models.category import Category
    from app.models.income import Income
    from app.models.expense import Expense
    from app.routes.auth_routes import auth_bp
    from app.routes.home_routes import home_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.export_routes import export_bp
    from app.routes.insight_routes import insights_bp
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(insights_bp)

    return app