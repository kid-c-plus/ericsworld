"""
Python SQLAlchemy model file defining Wisp.
"""
from sqlalchemy.sql import func 
from datetime import datetime
import json

from app import db, appconfig, constants

wisp_heart_association_table = db.Table(
    "wisp_heart_association_table",
    db.Model.metadata,
    db.Column(
        "hearted_user_id", db.String(32), 
        db.ForeignKey("user.user_id")
    ),
    db.Column(
        "hearted_wisp_id", db.String(32),
        db.ForeignKey("wisp.wisp_id")
    )
)

class Wisp(db.Model):
    """
    Definition of Wisp data model. A wisp can have text and/or a 
        GIF attachment
    """
    # All IDs consist of randomly-generated 32-character
    # hexadecimal UUIDs
    wisp_id = db.Column(db.String(32), unique=True, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.user_id"),
        nullable=False)
    user = db.relationship("User", back_populates="wisps")
    
    # refer to constants.py for list of Wisp status integers
    status = db.Column(db.Integer, 
            default=constants.LIVE_WISP, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow)

    text = db.Column(db.String(appconfig["MAX_WISP_LENGTH"]))
    gif_uri = db.Column(db.UnicodeText)

    hearted_users = db.relationship(
        "User",
        secondary=wisp_heart_association_table,
        lazy=True,
        backref="hearted_wisps"
    )

    def remove_hearts(self):
        """
        Deinitialization actions on Wisp. Does not remove self from
            database, but subtracts Hearts from poster's HeartScore
        """
        self.user.heartscore -= len(self.hearted_users)

    def __repr__(self):
        return "\n".join(
                f"{k}:\t{v}" for k, v in self.__dict__.items()
            )

    def to_dict(self):
        """
        Dictionary conversion method, allowing for easy JSON
            serialization by Flask. Contains only the fields that
            would be necessary to send to the frontend
        :return: simple dictionary representation of Wisp
        """
        return {
            "wisp_id":          self.wisp_id,
            "user_id":          self.user_id,
            "user_username":    self.user.username,
            "user_profile_uri": self.user.profile_uri,
            "user_heartscore":  self.user.heartscore,
            "status":           self.status,
            "created_time":     self.created_time,
            "text":             self.text,
            "gif_uri":          self.gif_uri
        }
