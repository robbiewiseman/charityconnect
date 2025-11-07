# VERSION 1

# This file is used to initialise and manage Flask extensions that are shared across the project.
from flask_wtf.csrf import CSRFProtect

# Create a CSRF (Cross-Site Request Forgery) protection object
# This helps secure all forms in the app by preventing unauthorised form submissions
# Reference: Flask-WTF CSRF protection setup (Pallets Projects, 2024)
# https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
csrf = CSRFProtect()

# VERSION 1