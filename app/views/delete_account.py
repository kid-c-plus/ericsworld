"""
App views for deleting a user account
"""
from flask import request
import flask_login
import uuid

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import *
from app.core import *
 
from tests.constants import *

@flaskapp.route("/delete-account", methods=["POST"])
@flask_login.login_required
def delete_account():
    """
    POST method for deleting the currently authenticated account
        and all its Wisps. Requires password confirmation.
    :jsonparam password: password for confirmation
    :return: 200 if account deleted, 403 if password invalid, 
        400 if request malformed
    """
    curr_user = flask_login.current_user

    password = request.json.get("password")
    if not password:
        return {"error": "Malformed request."}, 400

    if not curr_user.check_password(password):
        return {"error": "Invalid password."}, 403

    delete_user_content(curr_user)
    db.session.delete(curr_user)
    db.session.commit()

    return {"response": "User deleted."}, 200
