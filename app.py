# VERSION 1

# This file creates and configures the main Flask application for CharityConnect.
import os
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import text
from sqlalchemy.engine import make_url

# Import configuration, database, routes, and extensions
from config import Config         
from models import db
from routes import bp as main_bp, mail
from extensions import csrf        

def create_app():
    # Load environment variables from the .env file (for keys, database URL, etc.)
    load_dotenv() 

    # Reference: Flask config object pattern (Pallets Projects, 2024)
    # https://flask.palletsprojects.com/en/stable/config/
    # Create the Flask app and specify where templates and static files are stored
    app = Flask(__name__, template_folder="templates", static_folder="static")
    # Apply settings from the Config class (in config.py)
    app.config.from_object(Config) 

    # Initialise Flask extensions so they are linked to the app
    # Reference: SQLAlchemy ORM quickstart & init_app (SQLAlchemy, 2024)
    # https://docs.sqlalchemy.org/en/20/orm/quickstart.html
    db.init_app(app)

    # Reference: Flask-WTF CSRF integration (Pallets Projects, 2024)
    # https://flask-wtf.readthedocs.io/en/1.2.x/csrf/
    csrf.init_app(app)
    mail.init_app(app)

    # Try to safely display which database the app is connected to (without showing the password)
     # Reference: libpq connection string & safe display of URL (PostgreSQL, 2025)
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    try:
        safe = make_url(app.config["SQLALCHEMY_DATABASE_URI"]).set(password="***")
        print("DB URL (safe):", safe)
        print("Engine (detected):", safe.get_backend_name()) 
    except Exception:
        pass # If any issue occurs, skip printing the connection info

    # Test the database connection by running a simple query
    with app.app_context():
        # Reference: SQLAlchemy session execute/ping (SQLAlchemy, 2024)
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html
        try:
            print("DB Ping:", db.session.execute(text("select 1")).scalar())
        except Exception as e:
            print("DB ping failed:", e)

    # Register the main blueprint so routes become active
    # Reference: Flask Blueprints (Pallets Projects, 2024)
    # https://flask.palletsprojects.com/en/stable/blueprints/
    app.register_blueprint(main_bp)
    return app

# Run the application in debug mode if executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

# VERSION 1