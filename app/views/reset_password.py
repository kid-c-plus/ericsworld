"""
App views for resetting user passwords. Views to generate reset link,
    which will be sent to the user's email, and to receive the
    resultant request.
"""
from flask import request
import flask_login
from urllib.parse import quote

from app import flaskapp, appconfig, db, constants, twilio_client 
from app.models import User

def send_password_reset_email(user: User, reset_token: str):
    """
    Helper function to send an HTML password reset email with the 
        provided token to the provided user.
    :param user: User object of requesting user
    :param reset_token: newly generated password reset token, to be
        added to sent reset link
    """
    # TODO : Implement actual email send
    if appconfig["WEBMASTER_EMAIL"]:
        link = (
            "http://localhost/reset-password?" +
            f"phone_number={quote(user.phone_number, safe='')}" +
            f"&reset_token={quote(reset_token, safe='')}"
        )
    else:
        with open(constants.RESET_TOKEN_FILE, "w") as token_file:
            token_file.write(
                reset_token
            )

@flaskapp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    """
    POST endpoint for beginning password reset process. Users can use
        this endpoint to generate temporary links to be sent to their
        recovery email, which will allow them to reset their password.
    :jsonparam phone_number: phone number of account for which to reset
        password
    :return: 202 for any non-malformed request, 400 otherwise
        (important to avoid user base enumeration attacks).
    """
    if flask_login.current_user.is_authenticated:
        return {"error": "user already authenticated"}, 400

    phone_number = request.json.get("phone_number")
    if not appconfig["PHONE_NUMBER_CHECK"](phone_number):
        return {"error": "malformed request"}, 400

    user = db.session.execute(db.select(User).filter_by(
        phone_number=phone_number
    )).scalar()
    if user is not None and user.status == constants.ACTIVE_USER:
        new_token = user.generate_password_reset_token()
        if new_token:
            db.session.commit()
            send_password_reset_email(user, new_token)
    return {"response": "request recieved"}, 202

@flaskapp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    POST endpoint for resetting password. Recieves phone number and 
        reset auth token from frontend, which in turn recieves values
        from URL parameters from emailed reset link. Additional
        values provided by frontend form.
    :jsonparam phone_number: phone number for account resetting
        password (from URL params in reset link)
    :jsonparam reset_token: server-generated token authorizing reset
        (from URL params in reset link)
    :jsonparam auth_code: Twilio auth code for reset, sent to phone.
        Will be generated if not provided
    :jsonparam new_password: newly set password. Must pass 
        PASSWORD_CHECK
    :return: 200 if password reset, 202 if auth code sent, 
        403 for invalid request (non-active number, bad reset token, 
        etc), 400 for malformed request
    """
    if flask_login.current_user.is_authenticated:
        return {"error": "user already authenticated"}, 400
    
    phone_number, reset_token, auth_code, new_password = (
        request.json.get(key) for key in (
            "phone_number", "reset_token", "auth_code", "new_password"
        )
    )
    if (not appconfig["PHONE_NUMBER_CHECK"](phone_number) or
            not appconfig["PASSWORD_CHECK"](new_password) or 
            not reset_token):
        return {"error": "malformed request"}, 400
    
    user = db.session.execute(db.select(User).filter_by(
        phone_number=phone_number
    )).scalar()

    error_log_msg = None
    if user is None:
        error_log_msg = (
            f"IP {request.remote_addr} attempted to reset " +
            f"password for nonexistent number {phone_number}."
        )
    elif user.status != constants.ACTIVE_USER:
        error_log_msg = (
            f"IP {request.remote_addr} attempted to reset " +
            f"password for non-active number {phone_number}."
        )
    elif not user.check_password_reset_token(reset_token):
        error_log_msg = (
            f"IP {request.remote_addr} attempted to reset " +
            f"password for {phone_number} with invalid reset token."
        )
    if error_log_msg:
        flaskapp.logger.info(error_log_msg)
        return {"error": "number is not valid"}, 403
    
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
            user.set_password(new_password)
            db.session.commit()
            
            flaskapp.logger.info(
                f"IP {request.remote_addr} reset password for  "+
                f"{phone_number}."
            )
            return {"response": "password reset"}, 200
        else:
            flaskapp.logger.info(
                f"IP {request.remote_addr} submitted " +
                "invalid auth code for password reset for " +
                f"number {phone_number}."
            )
            return {"error": "invalid auth code"}, 403
    else:
        if twilio_client:
            twilio_client.verify.v2.services(
                appconfig["TWILIO_VERIFY_SERVICE_SID"]
            ).verifications.create(
                to=phone_number,
                channel="sms"
            )
        return {"response": "auth code sent"}, 202
