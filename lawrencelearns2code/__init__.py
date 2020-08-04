import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

email = {}
app_secret = ''
db_url = ''
try:
    with open(os.getcwd() + '//lawrencelearns2code//misc.json', 'r') as f:
        file = f.read()
        creds = json.loads(file)
        email = creds.get('email')
        app_secret = creds.get('app_secret')
        db_url = 'sqlite:///site.db'
except:
    email = {'username': os.environ.get('email_username'), 'pass': os.environ.get('email_password')}
    app_secret = os.environ.get('app_secret')
    db_url = os.environ.get('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = app_secret
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": email.get('username'),
    "MAIL_PASSWORD": email.get('pass'),
    "MAIL_DEFAULT_SENDER": email.get('username')
}

app.config.update(mail_settings)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from lawrencelearns2code import routes