"""
App views for posting wisps. Includes GIF listing and searching
    functionality.
"""
from flask import request
import flask_login
import bleach
from werkzeug.utils import secure_filename
import uuid

from app import flaskapp, appconfig, db, constants
from app.core import remove_excess_wisps
from app.models import *

@flaskapp.route("/post-wisp", methods=["POST"])
@flask_login.login_required
def post_wisp():
    """
    POST endpoint for posting a new Wisp. Requires a valid login
        session.
    :jsonparam text: text of Wisp to post
    :jsonparam gif_uri: URI of GIF to add to post
        (URI is also the SHA value of the GIF file)
    :return: 201 if post is created, 403 if over maximum number of 
        Wisps, 400 if Wisp too long or GIF does not exist
    """
    curr_user = flask_login.current_user

    if (len([wisp for wisp in curr_user.wisps 
            if wisp.status == constants.LIVE_WISP]) >= 
            appconfig["MAX_WISPS_PER_USER"]):
        return {"error": 
            "Account has reached maximum number of Wisps."}, 403
    text = bleach.clean(request.json.get("text", ""))
    gif_uri = secure_filename(
        request.json.get("gif_uri", "")
    )
    if (not appconfig["WISP_TEXT_CHECK"](text) or 
            (gif_uri and not 
            appconfig["GIF_URI_CHECK"](gif_uri))):
        return {"error": "Malformed request."}, 400

    # Theoretically, two wisps added at the exact same epoch time 
    # could have duplicate uuids, so I'll keep trying on collision
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
                    f"{curr_user.user_id} after too many " +
                    "uuid conflicts. This is statistically " +
                    "impossible. If you're reading this, go " +
                    "buy a lottery ticket."
                )
                return {
                    "error": "Unable to create wisp."
                }, 500

    return {"response":  "Wisp posted."}, 201

@flaskapp.route("/gif-search", methods=["GET"])
@flask_login.login_required
def gif_search():
    """
    GET endpoint for searching the GIF corpus for a provided term set. 
        Will not return more than the configured maximum.
    :queryparam term_string: space-deliminated string of search terms
    :return: 200 and {"gifs"} dict, where "gifs" is a list of matched
        GIF URIs, sorted in descending order of relevance, 400 if 
        term string not provided
    """
    curr_user = flask_login.current_user

    term_string = request.args.get("term_string")
    if not term_string:
        return {"error": "Search terms not provided."}, 400
    gifs = {}
    terms = term_string.split()
    for value in terms:
        associations = db.session.execute(
            db.select(SearchAssociation)
            .filter_by(
               term_value=value
            )
        ).scalars()
        for association in associations:
            if association.gif_sha in gifs:
                gifs[association.gif_sha] += association.weight
            else:
                gifs[association.gif_sha] = association.weight
    return {"gifs": sorted(
            gifs.keys(), key=lambda sha: gifs[sha], reverse=True
        )[:appconfig["GIFS_PER_SEARCH"]]
    }, 200

