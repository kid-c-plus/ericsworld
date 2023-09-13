"""
App views for account creation.
"""
from flask import request
import flask_login
from werkzeug.utils import secure_filename
import bleach

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import User


@flaskapp.route("/create-account", methods=["POST"])
def create_account():
    """
    POST endpoint for creating a new account. Checks number for
        invite status, password for complexity requirement,
        username for length and uniqueness. If all pass and Twilio
        auth is present, creates an account. Otherwise, sends Twilio
        auth if all pass.
    :jsonparam phone_number: number of new account. Must pass 
        PHONE_NUMBER_CHECK and already be present in database as an
        invited number.
    :jsonparam recovery_email: email address of new account. Used
        exclusively for password reset process.
    :jsonparam username: username for new account. Must pass 
        USERNAME_CHECK and be unique.
    :jsonparam password: password for new account. Must pass
        PASSWORD_CHECK.
    :jsonparam auth_code: Twilio auth code for new account. Is 
        generated if new account is valid and auth_code not present.
    :return: 201 if account has been created, 204 if Twilio auth has 
        been sent, 403 if number not invited/disabled/bad auth code,
        400 if request is bad.
    """
    if flask_login.current_user.is_authenticated:
        return {"error": "User already authenticated."}, 400

    (phone_number, recovery_email, username, password, 
        profile_uri, auth_code) = (
        request.json.get(key) for key in (
            "phone_number", "recovery_email", "username", 
            "password", "profile_uri", "auth_code"
        )
    )
    # Input file sanitization
    if username:
        username = bleach.clean(username).strip()
    if profile_uri:
        profile_uri = secure_filename(profile_uri)

    if not (appconfig["PHONE_NUMBER_CHECK"](phone_number) and
            appconfig["EMAIL_CHECK"](recovery_email) and
            appconfig["USERNAME_CHECK"](username) and
            check_username(username)[0].get("unique") and
            appconfig["PASSWORD_CHECK"](password) and
            appconfig["PROFILE_URI_CHECK"](profile_uri)):
        return {"error": "Malformed request."}, 400

    user = db.session.execute(db.select(User).filter_by(
        phone_number=phone_number
    )).scalar()
    if user is None or user.status != constants.INVITED_USER:
        if user is None:
            flaskapp.logger.info(
                f"IP {request.remote_addr} attempted to create user " +
                f"for non-invited number: {phone_number}"
            )
        else:
            flaskapp.logger.info(
                f"IP {request.remote_addr} attempted to recreate " +
                f"user: {user}"
            )
        return {"error": "Number is not valid."}, 403

    if auth_code:
        if twilio_client:
            check = twilio_client.verify.v2.services(
                appconfig["TWILIO_VERIFY_SERVICE_SID"]
            ).verification_checks.create(
                to=phone_number,
                code=auth_code
            ).valid
        else:
            check = auth_code == constants.TEST_AUTH_CODE
        if check:
            user.recovery_email = recovery_email
            user.username = username
            user.update_status(constants.ACTIVE_USER)
            user.set_password(password)
            user.profile_uri = profile_uri
            db.session.commit()

            flaskapp.logger.info(f"User created: {user}")
            return {
                "response": "User created."
            }, 201
        else:
            flaskapp.logger.info(
                f"IP {request.remote_addr} submitted " +
                "invalid auth code for account creation for " +
                f"number {phone_number}."
            )
            return {"error": "Invalid auth code."}, 403
    else:
        if twilio_client:
            twilio_client.verify.v2.services(
                appconfig["TWILIO_VERIFY_SERVICE_SID"]
            ).verifications.create(
                to=phone_number,
                channel="sms"
            )
        return {"response": "Auth code sent."}, 204

@flaskapp.route("/check-username", methods=["GET"])
def check_username(username: str = None):
    """
    GET endpoint for checking the uniqueness of a provided username.
        Used as a backend helper when creating or changing a username.
    :queryparam username: prospective new username to check for 
        uniqueness. Can be passed as an argument or in request JSON
    :return: 200 and "unique" dict containing boolean if synactically
        valid username, 400 otherwise
    """
    username = username or request.args.get("username")
    if appconfig["USERNAME_CHECK"](username):
        user = db.session.execute(db.select(User).filter_by(
            username=username 
        )).scalar()
        return {"unique": user is None}, 200
    else:
        return {"error": "Malformed request."}, 400
