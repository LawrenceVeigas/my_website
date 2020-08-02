import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

creds = {}
with open(os.getcwd() + '//lawrencelearns2code//misc.json', 'r') as f:
    file = f.read()
    creds = json.loads(file)
    creds = creds.get('email')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e94c3ddbf6c23558fe5b76032d0d7b78'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": creds.get('username'),
    "MAIL_PASSWORD": creds.get('pass'),
    "MAIL_DEFAULT_SENDER": creds.get('username')
}

app.config.update(mail_settings)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from lawrencelearns2code import routes