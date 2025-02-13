"""
App views for account login.
"""
from flask import request
import flask_login
from werkzeug.security import check_password_hash

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import User

@flaskapp.route("/login", methods=["POST"])
def login():
    """
    POST endpoint for logging into an existing account.
    :jsonparam phone_number: number of account. Cannot login with
        username.
    :jsonparam password: password for account.
    :jsonparam remember: whether to persist login on machine.
    :jsonparam auth_code: Twilio auth code for users with 2FA 
        enabled. Is generated if login is valid and 2FA is enabled
    :return: 200 if successful, 202 if auth code generated,
        403 if unsuccessful, 400 if lacking required fields
    """
    phone_number, password, remember, auth_code = (
        request.json.get(key) for key in (
            "phone_number", "password", "remember", "auth_code"
        )
    )
    if not (appconfig["PHONE_NUMBER_CHECK"](phone_number) and 
            password):
        return {"error": "malformed request"}, 400

    if flask_login.current_user.is_authenticated:
        return {"error": "user already authenticated"}, 400
    user = db.session.execute(db.select(User).filter_by(
        phone_number=phone_number
    )).scalar() 

    fail_reason = None
    if user is None:
        fail_reason = "Nonexistent user"
        # engage in a dummy hash in order to keep return time
        # consistent
        check_password_hash(constants.DUMMY_HASH, password)
    elif user.status != constants.ACTIVE_USER:
        fail_reason = "Non-active user"
        check_password_hash(constants.DUMMY_HASH, password)
    elif not user.check_password(password):
        fail_reason = "Bad password"

    if fail_reason:
        flaskapp.logger.info(
            f"User {phone_number} failed to log in from " +
            f"IP {request.remote_addr}. Reason: " +
            f"{fail_reason}."
        )
        return {"error": "invalid login"}, 403

    if user.two_factor_auth:
        if auth_code:
            if twilio_client:
                check = twilio_client.verify.v2.services(
                    appconfig["TWILIO_VERIFY_SERVICE_SID"]
                ).verification_checks.create(
                    to=phone_number,
                    code=otp_code
                ).valid
            else:
                check = (
                    auth_code == constants.TEST_AUTH_CODE
                )
            if check:
                flask_login.login_user(
                    user, remember=remember
                )
                flaskapp.logger.info(
                    f"Logged in user {user.username}."
                )
                return {"response": "logged in"}, 200
            else:
                # This data is used to configure Fail2Ban
                flaskapp.logger.info(
                    f"User {phone_number} " +
                    "failed to log in from " +
                    f"IP {request.remote_addr}." +
                    "Reason: 2FA Failed."
                )
                return {"error": "invalid login"}, 403
        else:
            if twilio_client:        
                twilio_client.verify.v2.services(
                    appconfig["TWILIO_SERVICE_SID"]
                ).verifications.create(
                    to=phone_number,
                    channel="sms"
                )
            return {"response": "auth code sent"}, 202
    else:
        flask_login.login_user(user, remember=remember)
        flaskapp.logger.info(
            f"Logged in user {user.username}."
        )
        return {"response": "logged in"}, 200
