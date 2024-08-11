"""
App views for current account information.
"""
import flask
import flask_login

from app import flaskapp, db, constants
from app.models import User

@flaskapp.route("/get-account-info", methods=["GET"])
@flask_login.login_required
def get_account_info():
    """
    GET endpoint for fetching information on the curent user.
    :return: 200 and {"username", "profile_uri", "heartscore"} resp
        dict, or 401 as always if not authenticated
    """
    curr_user = flask_login.current_user
    return {
        "username": curr_user.username,
        "profile_uri": curr_user.profile_uri,
        "heartscore": curr_user.heartscore
    }, 200

@flaskapp.route("/get-heartscore", methods=["GET"])
@flask_login.login_required
def get_heartscore():
    """
    GET endpoint for fetching current user's HeartScore. Pared down
        version of above method
    :return: 200 and {"heartscore"} resp dict
    """
    return {
        "heartscore": flask_login.current_user.heartscore
    }, 200
