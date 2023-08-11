"""
App views for account login.
"""
import flask
import flask_login

from app import flaskapp, db, constants
from app.models import User

@flaskapp.route("/logout", methods=["POST"])
def logout():
    """
    POST endpoint for logging out the current account.
    :return: 200 if user logged out, 401 if no authenticated user
        account.
    """
    if flask_login.current_user.is_authenticated:
        flask_login.logout_user()
        return {"response": "Logged out."}, 200
    else:
        return {"error": "No authenticated user."}, 401
