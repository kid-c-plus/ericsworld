"""
App views for current account information.
"""
import flask
import flask_login

from app import flaskapp, db, constants
from app.models import User

@flaskapp.route("/account-info", methods=["GET"])
def account_info():
    """
    GET endpoint for fetching information on the curent user.
    :return: 200 and {"username", "profile_uri", "heartscore"} response
        dict if there exists a currently authenticated user, else 401
    """
    flaskapp.logger.info(flask_login.current_user) 
    if flask_login.current_user.is_authenticated:
        curr_user = flask_login.current_user
        return {"response": {
            "username": curr_user.username,
            "profile_uri": curr_user.profile_uri,
            "heartscore": curr_user.heartscore
        }}, 200
    else:
        return {"error": "No authenticated user."}, 401
