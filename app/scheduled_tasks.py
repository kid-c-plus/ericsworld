"""
Scheduled database maintenance tasks, such as the removal of 
    expired Wisps. Uses BackgroundScheduler instance defined 
    in __init__.py.
"""
import datetime as dt
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app import flaskapp, scheduler, db, appconfig
from app.core import promote_or_remove_wisp, expire_song
from app.models import *

FILE = "thread_debug.txt"

def schedule():
    """
    Register all configured background tasks in this file.
    """
    scheduler.add_job(
        purge_wisps,
        trigger="interval",
        seconds=appconfig["WISP_PURGE_INTERVAL"]
    )
    scheduler.start()

def stop():
    """
    Shutdown background scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()

def purge_wisps():
    """
    Remove wisps (or classify them as remembrances)
        after the expiry period has elapsed.
    """
    try:
        with flaskapp.app_context():
            expiry = dt.datetime.now(dt.UTC) - appconfig["WISP_LIFESPAN"]
            expired_wisps = db.session.scalars(
                db.select(Wisp).filter_by(
                    status=constants.LIVE_WISP
                ).filter(
                    Wisp.created_time <= expiry
            )).all()
            for wisp in expired_wisps:
                promote_or_remove_wisp(wisp)
            db.session.commit()
    except OperationalError:
        # because the server fixture is long-lived and the DB one 
        # isn't, occasionally this'll run when the "wisp" table isn't
        # present
        pass

def purge_songs():
    """
    Remove Song database entries after their post-queue time
        has expired.
    """
    try:
        with flaskapp.app_context():
            expiry = dt.datetime.now(dt.UTC) - appconfig["SONG_LIFESPAN"]
            expired_songs = db.session.scalars(
                db.select(Song).filter_by(
                    status=constants.PLAYED_SONG
                ).filter(
                    Song.created_time <= expiry
            )).all()
            for song in expired_songs:
                expire_song(song) 
            db.session.commit()
    except OperationalError:
        # because the server fixture is long-lived and the DB one 
        # isn't, occasionally this'll run when the "song" table isn't
        # present
        pass
