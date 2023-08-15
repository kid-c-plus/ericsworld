"""
App views for blocking a user account
"""
import flask
import flask_login
import uuid

from app import flaskapp, appconfig, db, constants, twilio_client
from app.models import *
from app.core import *
 
from tests.constants import *

@flaskapp.route("/block-account", methods=["POST"])
def block_account():
    """
    POST endpoint for blocking an account using the ID of one of
        its Wisps. Wisp IDs are used, not because User IDs are
        confidential, but because the block will be initiated by a
        button on a Wisp, and shouldn't be accomplishable outside
        the context of that.
    :jsonparam wisp_id: unique ID of offending Wisp, the posting User
        of which will be blocke
    :return: 200 if user has been blocked, 401 if no active user,
        404 if Wisp not found, 400 if request is malformed
    """
    curr_user = flask_login.current_user
    if not curr_user.is_authenticated:
        return {"error": "No authenticated user."}, 401

    wisp_id = flask.request.values.get("wisp_id")
    if not wisp_id:
        return {"error": "Malformed request."}, 400

    wisp = db.session.get(Wisp, wisp_id)
    if not wisp:
        flaskapp.logger.info(
            f"User {curr_user.user_id} from IP " +
            f"{flask.request.remote_addr}attempted block with " +
            f"nonexistent Wisp ID {wisp_id}"
        )
        return {"error": "Wisp not found."}, 404

    blocked_user = wisp.user
    if blocked_user == curr_user:
        return {"error": "Users cannot block themselves."}, 400

    curr_user.blocked_users.append(blocked_user)
    # if number of blocks is above threshold, disable user
    if len(blocked_user.blocked_by_users) >= appconfig["BLOCKS_TO_BAN"]:
        blocked_user.update_status(constants.DISABLED_ACCOUNT)
        delete_user_content(blocked_user)

        login_id_changed = False
        tries = 0
        while not login_id_changed:
            try:
                blocked_user.login_id = uuid.uuid1().hex
                db.session.commit()
                flaskapp.logger.info(
                    f"User {blocked_user.user_id} has been banned " +
                    f"after being blocked by {curr_user.user_id}"
                )
                login_id_changed = True
            except IntegrityError:
                tries += 1
                if tries >= 3:
                    flaskapp.logger.error(
                        f"Unable to ban user {blocked_user.user_id} " +
                        f"after too many Login UUID collisions."
                    )
                    return {
                        "error": "Unable to block user."
                    }, 500
    else:
        db.session.commit()
    return {"response": "User blocked."}, 200

