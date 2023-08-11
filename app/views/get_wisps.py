"""
App views for viewing Wisps.
"""
from flask import request
import flask_login
import sqlalchemy

from app import flaskapp, appconfig, db, constants
from app.models import *

def get_wisps_for_user(user: flask_login.UserMixin, 
                       offset: int = 0,
                       limit: int = constants.WISPS_PER_PAGE,
                       descending: bool = True,
                       **filters) -> sqlalchemy.Response:
    """
    Helper method to get all wisps visible to a given user.
        Accounts for blocklist and blockerlist.
    :param User: User object for which to get Wisps. Can be
        AnonymousUserMixin for anonymous access
    :param offset: Offset from which to start reading Wisps.
        Default: 0
    :param limit: Maximum number of wisps to return.
        Default: constants.WISPS_PER_PAGE
    :param descending: Whether to sort Wisps in descending order
        by time
        Default: True
    :param filters: Keyword dictionary of additional filters
        to pass to SQLAlchemy query
    :return: sqlalchemy.Result object containing Wisps
    """
    if isinstance(user, User):
        blocklist = [
            user.user_id for user in user.blocked_users
        ]
        blockerlist = [
            user.user_id for user in user.blocked_by_users
        ]
    else:
        blocklist = blockerlist = []
    order = (User.created_time.desc() if descending
        else User.created_time.asc())

    return db.session.execute(
        db.select(Wisp).filter(
            Wisp.user_id.not_in(blocklist),
            Wisp.user_id.not_in(blockerlist)
        ).filter_by(
            **filters
        ).offset(offset).limit(limit).order_by(order)
    )

def get_wisp_position(user: flask_login.UserMixin, 
                      wisp_id: str, 
                      descending: bool = True) -> int:
    """
    Helper method to get the database position of the Wisp with
        the provided ID, in the list of Wisps made at that exact
        time. Even among identical values, this order will be 
        deterministic when sorted.
    :param user: currently authenticated user object. Can be 
        AnonymousUserMixin for unauthenticated access
    :param wisp_id: ID of Wisp to locate
    :param descending: Whether to sort Wisps in descending order
        by time
        Default: True
    :return: integer index of database row containing Wisp, or -1
        if not found
    """
    wisp = get_wisps_for_user(user, wisp_id=wisp_id).scalar()
    if not wisp:
        return -1
    
    simultaneous_wisps = get_wisps_for_user(
        user,
        descending=descending,
        status=constants.LIVE_WISP,
        created_time=wisp.created_time
    ).all()
    return next(
        index for index, wisp in enumerate(
           simultaneous_wisps
       ) if wisp.wisp_id = wisp_id

@flaskapp.route("/get-wisps", methods=["GET"])
def get_wisps(first_wisp_id: str = None, last_wisp_id: str = None):
    """
    GET endpoint for getting a page of Wisps. Does not require a
        valid login session. At most one of (first_wisp_id,
        last_wisp_id) should be present.
    :param first_wisp_id: ID of first seen Wisp (to load newer
        Wisps)
    :param last_wisp_id: ID of last seen Wisp (to load older
        Wisps)
    :return: 200 and {"wisps"} dict if successful, 404 if provided
        Wisp isn't found (indicating a block, deletion, or removal).
        In this case, the browser will remove it and submit the 
        previous/next Wisp depending on load direction.
    """
    # I have to do something fairly complex here, where I want to
    # query all Wisps made at the exact timestamp of the 
    # first/last_wisp_id, and then I have to calculate the 
    # position of the Wisp itself in that list ordered 
    # deterministically by timestamp asc/desc as the case may be.
    # Then, I can use that position as the offset in the actual
    # call to get the next WISPS_PER_PAGE Wisps

    user = flask_login.current_user
    wisp_id = first_wisp_id or last_wisp_id
    if wisp_id:
        descending = True if last_wisp_id else False
        offset = get_wisp_position(user, wisp_id, descending)
        if offset == -1:
            return {"error": "Wisp not found."}, 404
        return get_wisps_for_user(
            user, offset=offset, 
            descending=descending, status=LIVE_WISP
        ).all(), 200

    else:
        return get_wisps_for_user(
            user, status=constants.LIVE_WISP
        ).all(), 200

@flaskapp.route("/check-newest-wisp", methods=["GET"])
def check_newest_wisp(wisp_id: str):
    """
    GET endpoint for checking to see if newer Wisps are present.
    :param wisp_id: ID of newest Wisp on browser
    :return: 200 and {"newest": boolean} dict if successful, 404
        if no Wisps are found. 
    """
    user = flask_login.current_user
    first_wisp = get_wisps_for_user(
        user, limit=1, status=constants.LIVE_WISP
    ).scalar()
    if first_wisp:
        return {"newest": first_wisp.wisp_id == wisp_id}, 200
    else:
        return {"error": "No Wisps found."}, 404
