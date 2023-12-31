"""
App views for updating information for an existing account. 
    The items that can be changed are: phone number, recovery email,
    password, username, and profile_uri, the first 3 of which require
    the entry of a user's current password.
"""
from flask import request
import flask_login
from werkzeug.utils import secure_filename
import bleach
import os

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import User
from app.views.create_account import check_username

@flaskapp.route("/update-number", methods=["POST"])
@flask_login.login_required
def update_number():
    """
    POST endpoint for changing the phone number associated with
        an account. Requires password and 2-factor auth.
    :jsonparam new_number: new phone number for account.
    :jsonparam password: password for verification.
    :jsonparam auth_code: Twilio 2-factor authentication code
        for new number. Will be generated if not provided
    :return: 200 if number has been changed, 204 if Twilio auth
        has been sent, 403 if bad password/auth, 400 if bad request.
    """
    curr_user = flask_login.current_user
    
    new_number, password, auth_code = (
        request.json.get(key) for key in (
            "new_number", "password", "auth_code"
        )
    )
    if not (appconfig["PHONE_NUMBER_CHECK"](new_number) and
            new_number != curr_user.phone_number and
            db.session.execute(db.select(User).filter_by(
                phone_number=new_number
            )).scalar() == None):
        return {"error": "Malformed request."}, 400

    if not curr_user.check_password(password):
        return {"error": "Invalid password."}, 403

    if auth_code:
        if twilio_client:
            check = twilio_client.verify.v2.services(
                appconfig["TWILIO_VERIFY_SERVICE_SID"]
            ).verification_checks.create(
                to=new_number,
                code=auth_code
            ).valid
        else:
            check = auth_code == constants.TEST_AUTH_CODE
        if check:
            flaskapp.logger.info(
                "User phone number updated from " +
                f"{curr_user.phone_number} to {new_number}."
            )

            curr_user.phone_number = new_number
            db.session.commit()
            return {"response": "Number updated."}, 200
        else:
            return {"error": "Invalid auth code."}, 403
    else:
        if twilio_client:
            twilio_client.verify.v2.services(
                appconfig["TWILIO_VERIFY_SERVICE_SID"]
            ).verifications.create(
                to=new_number,
                channel="sms"
            )
        return {"response": "Auth code sent."}, 204

@flaskapp.route("/update-recovery-email", methods=["POST"])
@flask_login.login_required
def update_recovery_email():
    """
    POST endpoint for changing a user's recovery email.
        Requires password.
    :jsonparam new_email: new recovery email for user
    :jsonparam password: password for authentication
    :return: 200 if username has been changed, 403 if password
        is invalid, 400 if email is bad or request invalid
    """
    curr_user = flask_login.current_user

    new_email, password = (
        request.json.get(key) for key in (
            "new_email", "password"
        )
    )
    if not appconfig["EMAIL_CHECK"](new_email):
        return {"error": "Malformed request."}, 400
    
    if not curr_user.check_password(password):
        return {"error": "Invalid password."}, 403
    
    curr_user.recovery_email = new_email
    db.session.commit()
    return {"response": "Recovery email updated."}, 200

@flaskapp.route("/update-password", methods=["POST"])
@flask_login.login_required
def update_password():
    """
    POST endpoint for changing a user's password. Must, of course,
        include current password.
    :jsonparam current_password: user's current password
    :jsonparam new_password: new password to change to
    :return: 200 if password changed, 403 if current password is
        invalid, 400 if new password is malformed
    """
    curr_user = flask_login.current_user
    
    current_password, new_password = (
        request.json.get(key) for key in (
            "current_password", "new_password"
        )
    )
    if not appconfig["PASSWORD_CHECK"](new_password):
        return {"error": "Malformed request."}, 400

    if not curr_user.check_password(current_password):
        return {"error": "Invalid password."}, 403

    curr_user.set_password(new_password)
    db.session.commit()
    return {"response": "Password updated."}, 200

@flaskapp.route("/update-username", methods=["POST"])
@flask_login.login_required
def update_username():
    """
    POST endpoint for changing a user's password.
    :jsonparam new_username: new username value. Must pass 
        USERNAME_CHECK and be unique.
    :return: 200 if username has been changed, 400 if username is
        invalid
    """
    curr_user = flask_login.current_user
    
    new_username = bleach.clean(
        request.json.get("new_username", "")
    ).strip()
    if not (appconfig["USERNAME_CHECK"](new_username) and
            check_username(new_username)[0]["unique"]):
        return {"error": "Malformed request."}, 400
    
    curr_user.username = new_username
    db.session.commit()
    return {"response": "Username changed."}, 200
    
@flaskapp.route("/update-profile", methods=["POST"])
@flask_login.login_required
def update_profile():
    """
    POST endpoint for changing a user's profile picture.
    :jsonparam new_profile: new profile URI. must pass
        PROFILE_CHECK
    :return: 200 if profile has been changed, 400 if profile URI is
        invalid
    """
    curr_user = flask_login.current_user
    
    new_profile = secure_filename(
        request.json.get("new_profile", "")
    )
    if not appconfig["PROFILE_URI_CHECK"](new_profile):
        return {"error": "Malformed request."}, 400
    
    curr_user.profile_uri = new_profile
    db.session.commit()
    return {"response": "Profile changed."}, 200

@flaskapp.route("/get-profiles", methods=["GET"])
@flask_login.login_required
def get_profiles():
    """
    GET endpoint for providing URIs for the profile GIFs in the
        provided category, or the list of profile categories if none
        is provided.
    :queryparam category: category for which to return GIF URIs
    :return: 200 and {"gifs"} dict, where "gifs" is a list of
        filenames, or 400 if category not found
    """
    category = secure_filename(
        request.params.get("category", ""))

    if category:
        category_path = os.path.join(
            appconfig["PROFILE_DIR"], category
        )
        if os.path.exists(category_path):
            return {"gifs": os.listdir(category_path)}, 200
        else:
            return {"error": "Malformed request."}, 400
    else:
        return {"gifs": os.listdir(appconfig["PROFILE_DIR"])}
