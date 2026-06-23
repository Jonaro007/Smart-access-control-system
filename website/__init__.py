from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from datetime import timedelta
import mail_handler
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    basedir = os.path.abspath(os.path.dirname(__file__)) 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, DB_NAME)}'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)



    db.init_app(app)


    mail_handler.create_mail_app(app)


    from .views import views
    from .auth import auth
    from .verify import verify

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(verify, url_prefix='/')


    from .models import User, Logs
    

    

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), DB_NAME)
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
        print("Created Database!")
