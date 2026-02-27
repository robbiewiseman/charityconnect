# VERSION 1

from flask import redirect, url_for, flash
from routes import get_role # gets the current user's role from the session

def require_role(*roles):

    # Checks if the current user's role is allowed to access a page or action. If not, the user is shown a warning and redirected to the homepage.

    # If the user’s current role is not in the list of allowed roles
    if get_role() not in roles:
        # Show a message saying they are not authorised
        # Reference: Flask url_for (Pallets Projects, 2024)
        # https://flask.palletsprojects.com/en/stable/quickstart/#url-building
        flash("Not authorised for this action.", "warning")
        # Send them back to the homepage
        return redirect(url_for("main.index"))
    
    # If authorised, continue as normal
    return None

# VERSION 1