# flask-sovellus
from flask import Flask

app = Flask(__name__)

# tietokanta
from flask_sqlalchemy import SQLAlchemy

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
    app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

# kirjautuminen

from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager, current_user

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "Tämä toiminto vaatii kirjautumisen."


from functools import wraps

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user:
                return login_manager.unauthorized()

            if not current_user.is_authenticated():
                return login_manager.unauthorized()

            unauthorized = False

            if role != "ANY":
                unauthorized = True

                #for user_role in current_user.roles():
                if current_user.role == role:
                    unauthorized = False
             
            if unauthorized:
                return login_manager.unauthorized()
            
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# oman sovelluksen toiminnallisuudet
from application import views

from application.books import models
from application.books import views

from application.auth import models
from application.auth import views

from application.authors import models
from application.authors import views

# kirjautuminen osa 2

from application.auth.models import User
from application.auth.models import users_books

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# taulut tarvittaessa tietokantaan
try:
    db.create_all()
except:
    pass
