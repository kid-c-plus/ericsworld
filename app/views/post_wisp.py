"""
App views for posting wisps - includes GIF listing and searching
    functionality.
"""
from flask import request
import flask_login
import bleach
from werkzeug.utils import secure_filename

from app import flaskapp, appconfig, db, constants
from app.core import remove_excess_wisps
from app.models import User, Wisp

@flaskapp.route("/post-wisp", methods=["POST"])
@flask_login.login_required
def post_wisp():
    """
    POST endpoint for posting a new Wisp. Requires a valid login
        session.
    :jsonparam text: text of Wisp to post
    :jsonparam gif_uri: URI of GIF to add to post
    :return: 201 if post is created, 401 if unautorized, 403
        if over maximum number of Wisps, 400 if Wisp has too many 
        characters or GIF does not exist
    """
    curr_user = flask_login.current_user
    if not curr_user.is_authenticated:
        return {"error": "No authenticated user."}, 401
    # It shouldn't be possible for an inactive user to have a 
    # valid login session, but still
    if curr_user.account_status != constants.ACTIVE_ACCOUNT:
        return {"error": "Account not active."}, 403
    if len(curr_user.wisps) >= appconfig["MAX_WISPS_PER_USER"]:
        return {"error": 
            "Account has reached maximum number of Wisps."}, 403
    
    text, gif_uri = (request.values.get(key) for key in (
        "text", "gif_uri"
    ))
    text = bleach.clean(request.values.get("text", ""))
    gif_uri = secure_filename(
        request.values.get("gif_uri", "")
    )
    if (not appconfig["WISP_TEXT_CHECK"](text) or 
            (gif_uri and not 
            appconfig["GIF_URI_CHECK"](gif_uri))):
        return {"error": "Malformed request."}, 400

    # Theoretically, two wisps added at the exact same epoch time 
    # could  have duplicate uuids, so I'll keep trying on collision
    wisp_added = False
    tries = 0
    while not wisp_added:
        try:
            wisp = Wisp(
                wisp_id=uuid.uuid1().hex,
                user=curr_user, 
                text=text, 
                gif_uri=gif_uri 
            )
            db.session.add(wisp)
            remove_excess_wisps()
            db.session.commit()
            wisp_added=True
        except IntegrityError:
            tries += 1
            if tries >= 3:
                flaskapp.logger.error(
                    "Unable to post wisp for user " +
                    f"{curr_user.user_id} after too many Login " +
                    "UUID collisions."
                )
                return {
                    "error": "Unable to create wisp."
                }, 400

    return {"response":  "Wisp posted."}, 201


# TODO: Add GIF Search
