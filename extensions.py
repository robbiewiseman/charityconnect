# VERSION 1

# This file is used to initialise and manage Flask extensions that are shared across the project.
from flask_wtf.csrf import CSRFProtect
# VERSION 3 START
from flask_login import LoginManager
# VERSION 3 END

# Create a CSRF (Cross-Site Request Forgery) protection object
# This helps secure all forms in the app by preventing unauthorised form submissions
# Reference: Flask-WTF CSRF protection setup (Pallets Projects, 2024)
# https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
csrf = CSRFProtect()

# VERSION 3 START
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "warning"
# VERSION 3 END

# VERSION 1