"""
Scheduled database maintenance tasks, such as the removal of 
    expired Wisps. Uses BackgroundScheduler instance defined 
    in __init__.py.
"""
from datetime import datetime

from app import scheduler, db, appconfig
from app.core import promote_or_remove_wisp
from app.models import *

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
    expiry = datetime.utcnow() - appconfig["WISP_LIFESPAN"]
    expired_wisps = db.session.execute(
        db.select(Wisp).filter_by(
            created_time <= expiry
    ))
    for wisp in expired_wisps:
        promote_or_remove_wisp(wisp)

def purge_songs():
    """
    Remove Song database entries after their post-queue time
        has expired.
    """
    # TODO: Remove Old Songs
