"""
Python SQLAlchemy file defining Song.
"""
from sqlalchemy.sql import func 
from datetime import datetime

from app import db, constants

song_heart_association_table = db.Table(
    "song_heart_association_table",
    db.Model.metadata,
    db.Column(
        "hearted_user_id", db.String(32), 
        db.ForeignKey("user.user_id")
    ),
    db.Column(
        "hearted_song_id", db.String(32),
        db.ForeignKey("song.song_id")
    )
)

song_broken_heart_association_table = db.Table(
    "song_broken_heart_association_table",
    db.Model.metadata,
    db.Column(
        "broken_hearted_user_id", db.String(32), 
        db.ForeignKey("user.user_id")
    ),
    db.Column(
        "broken_hearted_song_id", db.String(32),
        db.ForeignKey("song.song_id")
    )
)

class Song(db.Model):
    """
    Definition of Song (queued, playing, or past) data model
    """
    song_id = db.Column(db.String(32), unique=True, primary_key=True)
    # user who queued song, can be anonymous for Otto-queued songs
    user_id = db.Column(db.String(32), db.ForeignKey("user.user_id"),
        nullable=True)
    user = db.relationship("User", back_populates="songs")
    
    # URI of song in static storage
    uri = db.Column(db.UnicodeText, nullable=False)

    # refer to constants.py for list of song status integers
    status = db.Column(db.Integer, 
        default=constants.QUEUED_SONG, nullable=False)
    status_updated_time = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    hearted_users = db.relationship(
        "User",
        secondary=song_heart_association_table,
        lazy=True,
        backref="hearted_songs"
    )
    broken_hearted_users = db.relationship(
        "User",
        secondary=song_broken_heart_association_table,
        lazy=True,
        backref="broken_hearted_songs"
    )

    def remove_hearts(self):
        """
        Deinitilization actions on Song. Does not remove self from
            database, but subtracts Hearts from poster's HeartScore
        """
        if self.user:
            self.user.heartscore -= len(self.hearted_users)
            self.user.heartscore += len(self.broken_hearted_users)

    def __repr__(self):
        return "\n".join(
                f"{k}:\t{v}" for k, v in self.__dict__.items()
            )
