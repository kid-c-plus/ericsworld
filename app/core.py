"""
Core functionality invoked by MVC pieces and scheduled as
    maintenance. None of these functions commit database
    sessions!
"""
from app import db, appconfig, constants
from app.models import *

def promote_or_remove_wisp(wisp: Wisp):
    """
    Helper method to either promote the given Wisp to a Remembrance,
        if there are fewer than the maximum number of Remembrances
        or it has more Hearts than the lowest of them, or to remove it.
    :param wisp: wisp to promote or remove
    """
    remembrances = sorted(db.session.scalars(
        db.select(Wisp).filter_by(
            status=constants.REMEMBRANCE_WISP
        )).all(),
        key=lambda wisp: len(wisp.hearted_users)
    )
    
    wisp.remove_hearts()
    if (len(remembrances) < appconfig["MAX_REMEMBRANCES"] or
            (len(remembrances) and len(wisp.hearted_users) > 
            len(remembrances[0].hearted_users))):
        wisp.status = constants.REMEMBRANCE_WISP
        if len(remembrances) == appconfig["MAX_REMEMBRANCES"]:
            db.session.delete(remembrances[0])
    else:
        db.session.delete(wisp)

def expire_song(song: Song):
    """
    Helper method to expire the given song
    :param song: Song object to expire
    """
    song.remove_hearts()
    db.session.delete(song)

def remove_excess_wisps():
    """
    Helper method to promote or delete as many old Wisps as 
        necessary to keep total number below maximum set in config.
    """
    
    excess = db.session.execute(
        db.select(db.func.count()).select_from(
            db.select(Wisp).filter_by(
                status=constants.LIVE_WISP
    ))).scalar() - appconfig["MAX_WISPS"]

    if excess > 0:
        excess_wisps = db.session.scalars(
            db.select(Wisp).filter_by(
                status=constants.LIVE_WISP
            ).order_by(
                Wisp.created_time.asc()
            ).limit(excess)
        ).all()
        for wisp in excess_wisps:
            promote_or_remove_wisp(wisp)

def delete_user_content(user: User):
    """
    Helper method to remove all Wisps and Songs from a deleted
        or banned user.
    """
    for wisp in user.wisps:
        wisp.remove_hearts()
        db.session.delete(wisp)
    for song in user.songs:
        song.remove_hearts()
        db.session.delete(song)
