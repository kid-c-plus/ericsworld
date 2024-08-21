"""
App views for Hearting and BrokenHearting Songs.
"""
import flask_login

from app import flaskapp, appconfig, db, constants, radiocontroller
from app.models import Song

def get_current_song() -> Song:
    """
    Helper method to get the first song with status PLAYING_SONG.
    :return: Song object
    """
    return db.session.scalars(
        db.select(Song).filter_by(
            status=constants.PLAYING_SONG
        )
    ).first()

@flaskapp.route("/heart-song", methods=["POST"])
@flask_login.login_required
def heart_song():
    """
    POST endpoint for Hearting the currently playing song.
    :return: 200 if song Hearted.
        Returns 200 if song already Hearted or from current user,
        though the User.heart_song helper method catches those things.
    """
    curr_user = flask_login.current_user
    curr_song = get_current_song()

    curr_user.heart_song(curr_song)
    db.session.commit()
    return {"response": "Song Hearted."}, 200

@flaskapp.route("/unheart-song", methods=["POST"])
@flask_login.login_required
def unheart_song():
    """
    POST endpoint for UnHearting the currently playing song.
    :return: 200 if song UnHearted.
    """
    curr_user = flask_login.current_user
    curr_song = get_current_song()

    curr_user.unheart_song(curr_song)
    db.session.commit()
    return {"response": "Song UnHearted."}, 200

@flaskapp.route("/brokenheart-song", methods=["POST"])
@flask_login.login_required
def brokenheart_song():
    """
    POST endpoint for BrokenHearting the currently playing song.
    :return: 200 if song BrokenHearted.
    """
    curr_user = flask_login.current_user
    curr_song = get_current_song()

    curr_user.brokenheart_song(curr_song)
    db.session.commit()
    if (len(curr_song.broken_hearted_users) -
            len(curr_song.hearted_users) >=
            appconfig["BROKENHEARTS_TO_SKIP"]):
        flaskapp.logger.error("skipping song...")
        radiocontroller.skip_song()
    return {"response": "Song BrokenHearted."}, 200

@flaskapp.route("/unbrokenheart-song", methods=["POST"])
@flask_login.login_required
def unbrokenheart_song():
    """
    POST endpoint for UnBrokenHearting the currently playing song.
    :return: 200 if song UnBrokenHearted.
    """
    curr_user = flask_login.current_user
    curr_song = get_current_song()

    curr_user.unbrokenheart_song(curr_song)
    db.session.commit()
    return {"response": "Song UnBrokenHearted."}, 200
