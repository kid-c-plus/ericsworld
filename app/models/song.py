"""
Python SQLAlchemy file defining Song.
"""
from sqlalchemy.sql import func 

from app import db

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
    user_id = db.Column(db.String(32), db.ForeignKey("user.user_id"),
        nullable=False)
    user = db.relationship("User", back_populates="songs")
    
    # URI of song in static storage
    uri = db.Column(db.UnicodeText, nullable=False)

    queued_time = db.Column(db.DateTime, server_default=func.now())
    played_time = db.Column(db.DateTime)

    hearted_users = db.relationship(
        "User",
        secondary=song_heart_association_table,
        lazy=True,
        back_populates="hearted_songs"
    )
    broken_hearted_users = db.relationship(
        "User",
        secondary=song_broken_heart_association_table,
        lazy=True,
        back_populates="broken_hearted_songs"
    )

    def remove_hearts(self):
        """
        Deinitilization actions on Song. Does not remove self from
            database, but subtracts Hearts from poster's HeartScore
        """
        self.user.heartscore -= len(self.hearted_users)

    def __repr__(self):
        return "\n".join(
                f"{k}:\t{v}" for k, v in self.__dict__.items()
            )
