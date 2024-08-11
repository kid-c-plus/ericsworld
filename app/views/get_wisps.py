"""
App views for viewing Wisps.
"""
from flask import request
import flask_login
import sqlalchemy
import sys
import linecache

from app import flaskapp, appconfig, db, constants
from app.models import *

def get_wisps_for_user(user: flask_login.UserMixin, 
                       limit: int = appconfig['WISPS_PER_PAGE'],
                       complex_filters: list = [],
                       **equality_filters) -> sqlalchemy.engine.Result:
    """
    Helper method to get all wisps visible to a given user.
        Accounts for blocklist and blockerlist.
    :param User: User object for which to get Wisps. Can be
        AnonymousUserMixin for anonymous access
    :param limit: Maximum number of wisps to return.
        Default: constants.WISPS_PER_PAGE
    :param complex_filters: list of filters operating on
        conditions more complex than equality to pass to SQLAlchemy 
        query. Equality conditions should be passed as keyword 
        arguments
    :param equality_filters: additional filters for equality
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
    return db.session.scalars(
        db.select(Wisp).filter(
            Wisp.user_id.not_in(blocklist),
            Wisp.user_id.not_in(blockerlist),
            *complex_filters
        ).filter_by(
            **equality_filters
        ).limit(limit).order_by(
            Wisp.created_time.desc()
        )
    )

def get_wisp_position(user: flask_login.UserMixin, 
                      wisp: Wisp) -> 0:
    """
    Helper method to get the number of Wisps simultaneous with the 
        given Wisp, and the position of the given Wisp within that
        list. Even among identical values, this order will be 
        deterministic when sorted.
    :param user: currently authenticated user object. Can be 
        AnonymousUserMixin for unauthenticated access
    :param wisp: Wisp to locate
    :return: (no_simultaneous_wisps, wisp_position) tuple where 
        "no_simultaneous_wisps" is the total number of wisps at the 
        given instant and wisp_position is integer index of the given
        Wisp in that total
    """
    simultaneous_wisps = get_wisps_for_user(
        user,
        status=constants.LIVE_WISP,
        created_time=wisp.created_time
    ).all()

    return (len(simultaneous_wisps), next(
        index for index, i_wisp in enumerate(
           simultaneous_wisps
        ) if wisp.wisp_id == i_wisp.wisp_id))


@flaskapp.route("/get-wisps", methods=["GET"])
def get_wisps():
    """
    GET endpoint for getting a page of Wisps. Does not require a
        valid login session. At most one of (first_wisp_id,
        last_wisp_id) should be present.
    :queryparam newest_wisp_id: ID of newest seen Wisp (to load newer
        Wisps)
    :queryparam oldest_wisp_id: ID of oldest seen Wisp (to load older
        Wisps)
    :return: 200 and {"wisps"} dict if successful, 404 if provided
        Wisp isn't found (indicating a block, deletion, or removal).
        In this case, the browser will remove it and submit the 
        previous/next Wisp depending on load direction.
    """
    newest_wisp_id, oldest_wisp_id = (request.args.get(key) for key in (
        "newest_wisp_id", "oldest_wisp_id"))
    
    user = flask_login.current_user
    wisp_time_filter = None
    wisp_id = newest_wisp_id or oldest_wisp_id

    if wisp_id:
        wisp = get_wisps_for_user(user, wisp_id=wisp_id).one()
        if not wisp:
            return {"error": "Wisp not found."}, 404

        # I have to do something fairly complex here, where I want to
        # query all Wisps made at the exact timestamp of the 
        # newest/oldest_wisp_id, and then I have to calculate the 
        # position of the Wisp itself in that list, and change sign
        # depending on which direction (newer or older) I'm
        # querying for. When I sort results by timestamp, the order
        # for Wisps with identical timestamps is deterministic.
        # I have to find where the provided Wisp falls in that order.
        # If I'm looking for all older wisps, it's simple. I get
        # the position of the given Wisp in the set of simultaneous 
        # Wisps (ordered from newest to oldest), and then return all 
        # Wisps past that position in the array of wisps older than
        # the Wisp's timestamp. So, the expression is just 
        # API_RESULT[offset + 1:], where the "+ 1" is the given Wisp 
        # itself. If looking for all the newer Wisps, I'll have to get
        # both the position of the given Wisp in the set of
        # simultaneous Wisps, and the total length of that set.
        # Then, I'll take the difference of the two, and trim that 
        # number of Wisps off the end, i.e. API_RESULT[:offset - length]
        # Note that in the overwhelming majority of cases, there's only
        # one Wisp per timestamp, so offset is 0 and size is one, and 
        # the list slices are [1:] and [:-1] respectively.

        no_simultaneous_wisps, wisp_position = get_wisp_position(
            user, wisp
        )
        if newest_wisp_id:
            offset = (wisp_position - no_simultaneous_wisps)
            wisp_time_filter = Wisp.created_time >= wisp.created_time
        else:
            offset = 1 + wisp_position
            wisp_time_filter = Wisp.created_time <= wisp.created_time

        Default: 0

        wisps = get_wisps_for_user(
            user, limit = appconfig["WISPS_PER_PAGE"] + abs(offset), 
            complex_filters=[wisp_time_filter],
            status=constants.LIVE_WISP
        ).all() 
        if offset < 0:
            wisps = wisps[:offset]
        else:
            wisps = wisps[offset:]

        return {
            "wisps": [wisp.to_dict() for wisp in wisps]
        }, 200

    else:
        return {"wisps": [
            wisp.to_dict() for wisp in get_wisps_for_user(
                user, status=constants.LIVE_WISP
            ).all()
        ]}, 200
    
@flaskapp.route("/get-remembrances", methods=["GET"])
def get_remembrances():
    """
    GET endpoint for getting all Remembrances, Wisps with sufficient
        quantities of Hearts to be saved at the time of their
        passing
    :return: 200 and a {"remembrances"} list of all Remembrances
        visible to the User
    """
    return {"remembrances": [
        remembrance.to_dict() for remembrance in get_wisps_for_user(
            user, limit=appconfig["MAX_REMEMBRANCES"],
            status=constants.REMEMBRANCE_WISP
        ).all()
    ]}, 200

@flaskapp.route("/check-newest-wisp", methods=["GET"])
def check_newest_wisp():
    """
    GET endpoint for checking to see if newer Wisps are present
    :queryparam wisp_id: ID of newest Wisp on browser
    :return: 200 and {"newest": boolean} dict if successful, 404
        if no Wisps are found
    """
    wisp_id = request.args.get("wisp_id")
    user = flask_login.current_user
    first_wisp = get_wisps_for_user(
        user, limit=1, status=constants.LIVE_WISP
    ).first()
    if first_wisp:
        return {"newest": first_wisp.wisp_id == wisp_id}, 200
    else:
        return {"error": "No Wisps found."}, 404
