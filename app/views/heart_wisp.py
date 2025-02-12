"""
App views for Hearting/UnHearting Wisps and accessing Hearted Wisps.
"""
from flask import request
import flask_login

from app import flaskapp, appconfig, db, constants
from app.models import *
from app.views.get_wisps import get_wisps_for_user

@flaskapp.route("/heart-wisp", methods=["POST"])
@flask_login.login_required
def heart_wisp():
    """
    POST endpoint for Hearting the provided Wisp. Requires a valid
        login session. 
    :jsonparam: wisp_id: ID of Wisp to Heart
    :return: 200 if Wisp Hearted, 404 if Wisp not found, 400 if 
        Wisp ID not provided. Returns 200 even if Wisp already
        Hearted, or Wisp from current user, though the User.heart_wisp
        helper method catches those things
    """
    curr_user = flask_login.current_user

    wisp_id = request.json.get("wisp_id")
    if not wisp_id:
        return {"error": "wisp id not provided"}, 400

    wisp = get_wisps_for_user(user, wisp_id=wisp_id).one()
    if not wisp:
        return {"error": "wisp not found"}, 404

    curr_user.heart_wisp(wisp)
    db.session.commit()
    return {"response": "wisp hearted"}, 200

@flaskapp.route("/unheart-wisp", methods=["POST"])
@flask_login.login_required
def unheart_wisp():
    """
    POST endpoint for UnHearting the provided Wisp. Requires a valid
        login session.
    :jsonparam: wisp_id: ID of Wisp to UnHeart
    :return: 200 if Wisp UnHearted, 404 if Wisp not found, 400 if 
        Wisp ID not provided. Returns 200 even if Wisp already
        UnHearted
    """
    curr_user = flask_login.current_user

    wisp_id = request.json.get("wisp_id")
    if not wisp_id:
        return {"error": "wisp id not provided"}, 400

    wisp = get_wisps_for_user(curr_user, wisp_id=wisp_id).one()
    if not wisp:
        return {"error": "wisp not found"}, 404

    curr_user.unheart_wisp(wisp)
    db.session.commit()
    return {"response": "wisp unhearted"}, 200

@flaskapp.route("/hearted-wisps", methods=["GET"])
@flask_login.login_required
def hearted_wisps():
    """
    GET endpoint for recieving a complete list of IDs of Wisps 
        Hearted by the current user. This could return a fairly
        large amount of data (up to MAX_WISPS Wisp IDs)
    :return: 200 and {"wisp_ids"} list
    """
    curr_user = flask_login.current_user

    return {"wisp_ids": [
        wisp.wisp_id for wisp in curr_user.hearted_wisps
    ]}, 200
