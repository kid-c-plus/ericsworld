"""
App views for deleting a user account
"""
import flask
import flask_login
import uuid

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import *
from app.core import *
 
from tests.constants import *

@flaskapp.route("/delete-account", methods=["POST"])
def delete_account():
    """
    POST method for deleting the currently authenticated account
        and all its Wisps. Requires password confirmation.
    :jsonparam password: password for confirmation
    :return: 200 if account deleted, 401 if no account authenticated,
        403 if password invalid, 400 if request malformed
    """
    curr_user = flask_login.current_user
    if not curr_user.is_authenticated:
        return {"error": "No authenticated user."}, 401

    password = request.values.get("password")
    if not password:
        return {"error": "Malformed request."}, 400

    if not curr_user.check_password(password):
        return {"error": "Invalid password."}, 403

    delete_user_content(user)
    db.session.delete(user)
    db.session.commit()

    return {"response": "User deleted."}, 200
