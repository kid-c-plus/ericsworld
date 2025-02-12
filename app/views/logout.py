"""
App views for account login.
"""
import flask
import flask_login

from app import flaskapp, db, constants
from app.models import User

@flaskapp.route("/logout", methods=["POST"])
@flask_login.login_required
def logout():
    """
    POST endpoint for logging out the current account.
    :return: 200 if user logged out
    """
    flask_login.logout_user()
    return {"response": "logged out"}, 200
