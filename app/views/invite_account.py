"""
App views for account invitation.
"""
from flask import request
import flask_login
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.exc import IntegrityError
import uuid

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import User

@flaskapp.route("/invite-account", methods=["POST"])
@flask_login.login_required
def invite_account():
    """
    POST endpoint for inviting a new account. Checks current user
        session, ensures they haven't reached the limit of invites,
        checks invited number with Twilio for validity, and sends
        invite and adds number to users database as an invited account.
    :jsonparam invited_number: number of account to invite.
    :return: 200 if invited, 403 if limit reached, 400 if number not 
        valid, or not provided. 200 also if user already present in
        database.
    """
    curr_user = flask_login.current_user

    if len(curr_user.invited_users) >= appconfig["MAX_INVITES"]:
        return {"error": "Maximum invites used."}, 403

    invited_number = request.json.get("invited_number")
    invited_user = db.session.execute(db.select(User).filter_by(
        phone_number=invited_number
    )).scalar() 

    if invited_user:
        # return 200 to prevent against user enumeration
        return {"response": "User invited."}, 200
        
    if not appconfig["PHONE_NUMBER_CHECK"](invited_number):
        return {"error": "Malformed request."}, 400

    if twilio_client:
        try:
            client.messages.create(
                messaging_service_sid=appconfig[
                    "TWILIO_MSG_SERVICE_SID"],
                body=appconfig["INVITE_MSG"],
                to=invited_number
            )
        except TwilioRestException:
            flaskapp.logger.info(
                f"User {curr_user.phone_number} " + 
                "attempted to invite unreachable number " +
                f"{invited_number}."
            )
            return {"error": "Number unreachable."}, 400

    # Theoretically, two users invited at the exact same epoch time 
    # could  have duplicate uuids, so I'll keep trying on collision
    user_added = False
    tries = 0
    while not user_added:
        try:
            new_user = User(
                user_id=uuid.uuid1().hex,
                login_id=uuid.uuid1().hex,
                phone_number=invited_number,
                inviting_user=curr_user
            )
            db.session.add(new_user)
            db.session.commit()
            user_added = True
        except IntegrityError:
            tries += 1
            if tries >= 3:
                flaskapp.logger.error(
                    f"Unable to add user {curr_user.phone_number}. " +
                    "Had too many uuid conflicts. This is " +
                    "statistically impossible. If you're reading " +
                    "this, go buy a lottery ticket"
                )
                return {
                    "error": "Unable to invite user."
                }, 500

    return {"response": "User invited."}, 200
