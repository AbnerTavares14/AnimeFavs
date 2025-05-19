from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager 
from config import config 
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect 
from flask_migrate import Migrate
from dotenv import load_dotenv

bootstrap = Bootstrap5()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['WTF_CSRF_ENABLED'] = True
    config[config_name].init_app(app)
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    from .main import main
    app.register_blueprint(main)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')


    return app