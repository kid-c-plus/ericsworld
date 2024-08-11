"""
App views for radio controller. Includes queueing, hearting, and 
    broken-hearting song functionality.
"""
from flask import request
import flask_login
from werkzeug.utils import secure_filename
import uuid

from app import flaskapp, appconfig, db, constants
from app.models import Song

@flaskapp.route("/check-queue-status", methods=["GET"])
@flask_login.login_required
def check_queue_status():
    """
    GET endpoint to check whether the current user has queued the
        maximum number of songs already, or if overall queue is full
    :return: 200 and {"personal_queue_full", "global_queue_full"} 
        booleans
    """
    curr_user = flask_login.current_user

    total_queued_count = db.session.execute(
        db.select(Song).filter_by(
            status=constants.QUEUED_SONG
        ).count()
    )
    return {
        "personal_queue_full": (
            len([song for song in curr_user.songs
                 if song.status == constants.QUEUED_SONG]) >=
            appconfig["MAX_QUEUED_SONGS_PER_USER"]),
        "global_queue_full": (
            total_queued_count >= appconfig["MAX_QUEUED_SONGS"])
    }, 200

@flaskapp.route("/queue-song", methods=["POST"])
@flask_login.login_required
def queue_song():
    """
    POST endpoint for adding a song to the queue. Checks to make sure
        the user is beneath the maximum number of queued songs.
    :jsonparam: song_uri: URI of song to enqueue
    :return: 201 if song queued, 403 if queue is over personal or
        global limit, 400 if song URI does not exist
    """
    curr_user = flask_login.current_user

    queue_status = check_queue_status()[0]
    if queue_status["personal_queue_full"]:
        return {
            "error": "You've queued the max number of songs already."
        }, 403
    elif queue_status["global_queue_full"]:
        return {
            "error": "The Eric's World song queue is full."
        }, 403
    song_uri = secure_filename(request.json.get("song_uri", ""))
    if not appconfig["SONG_URI_CHECK"](song_uri):
        return {"error": "Malformed request."}, 400
    song_added = False
    tries = 0
    while not song_added:
        try:
            song = Song(
                song_id=uuid.uuid1().hex,
                user=curr_user,
                uri=song_uri
            )
            db.session.add(song)
            db.session.commit()
            song_added = True
        except IntegrityError:
            tries += 1
            if tries >= 3:
                flaskapp.logger.error(
                    f"Unable to add queued song after " +
                    "too many uuid conflicts. This is " +
                    "statistically impossible. If you're " +
                    "reading this, go buy a lottery ticket."
                )
                return {
                    "error": "Unable to queue song."
                }, 500
    return {"response": "Song queued."}, 201

@flaskapp.route("/get-song-queuer", methods=["GET"])
def get_song_queuer():
    """
    GET endpoint for checking whether the current song is user-queued
        or automatic, and fetching the name of the queueing user if
        applicable.
    :return: 200 and {"user_queued", "queueing_username", 
        "queueing_user_id"} dict, where "queueing_*" is present only 
        if "user_queued" is true
    """
    curr_song = db.session.scalars(
        db.select(Song).filter_by(
            status=constants.PLAYING_SONG
        )
    ).first()

    ret_dict = {
        "user_queued": curr_song.user != None
    }
    if ret_dict["user_queued"]:
        ret_dict["queueing_username"] = curr_song.user.username
        ret_dict["queueing_user_id"] = curr_song.user.user_id
    return ret_dict, 200
